import pandas as pd
import requests
import os
import json
import re
from flask import Flask, request, jsonify

# Function to normalize data
def normalize_data(data):
    char_map = {
        '%': 'percent',
        '&': 'and',
        '<': 'less_than',
        '>': 'greater_than',
        '#': 'number',
        '$': 'dollar',
        '@': 'at',
        '!': 'exclamation',
        '^': 'caret',
        '*': 'asterisk',
        '(': 'left_parenthesis',
        ')': 'right_parenthesis',
        '+': 'plus',
        '=': 'equals',
        '{': 'left_curly_brace',
        '}': 'right_curly_brace',
        '[': 'left_square_bracket',
        ']': 'right_square_bracket',
        '|': 'pipe',
        '\\': 'backslash',
        ':': 'colon',
        ';': 'semicolon',
        '"': 'double_quote',
        "'": 'single_quote',
        ',': 'comma',
        '.': 'dot',
        '?': 'question_mark',
        '/': 'slash'
    }

    def normalize_key(key):
        key = key.strip().lower()
        key = re.sub(r'[^a-zA-Z0-9]', lambda match: char_map.get(match.group(0), '_'), key)
        if re.match(r'^[0-9]', key):
            key = '_' + key
        return key

    def handle_nan(value):
        if pd.isna(value):
            return None
        return value

    normalized_data = []
    for row in data:
        normalized_row = {}
        for key, value in row.items():
            normalized_key = normalize_key(key)
            if isinstance(value, str):
                normalized_row[normalized_key] = value.strip().lower()
            else:
                normalized_row[normalized_key] = handle_nan(value)
        normalized_data.append(normalized_row)

    return normalized_data

# Function to generate metadata from the file
def generate_metadata_from_file(file):
    data = pd.read_csv(file)
    normalized_data = normalize_data(data.to_dict(orient='records'))
    data = pd.DataFrame(normalized_data)
    columns = data.columns
    metadata = []
    for column in columns:
        column_data = data[column]
        numeric_data = column_data.dropna().apply(pd.to_numeric, errors='coerce').dropna()
        min_value = numeric_data.min() if not numeric_data.empty else None
        max_value = numeric_data.max() if not numeric_data.empty else None
        avg_value = numeric_data.mean() if not numeric_data.empty else None
        unique_values = column_data.unique().tolist()
        potential_values = [v if pd.notna(v) else None for v in unique_values if len(unique_values) <= 20] or None
        metadata.append({
            'name': column,
            'type': str(column_data.dtype),
            'min': min_value if min_value is None else float(min_value),
            'max': max_value if max_value is None else float(max_value),
            'avg': avg_value if avg_value is None else float(avg_value),
            'count': int(len(column_data)),
            'uniqueValues': int(len(unique_values)),
            'potentialValues': potential_values
        })
    return metadata, normalized_data

# Function to call GPT and get the title and information sheet
def get_metadata_information(filename, metadata):
    metadata_str = json.dumps(metadata)
    prompt = f"""Please generate the following items for this dataset given its filename: {filename} and metadata: {metadata_str}

1. Good title for the dataset, should be short and descriptive
2. Information sheet about the dataset in markdown

Please denote the title with 

title: <title>

and denote the information sheet with:

information sheet: <markdown_code>

the information sheet should contain 

Title: <title of dataset>
Description: <good description of the dataset>
Structure: <columns with potential values>
Context: <historical context around the data>
Usage Notes:
• Limitations: 
• License: Data is licensed under the Creative Commons Attribution 4.0 International License.
Technical Information:
• Format: CSV (.csv)"""

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.getenv('ICED_DEMO_API_KEY')}",
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            'model': 'gpt-4o-2024-05-13',
            'messages': [
                {'role': 'user', 'content': prompt},
            ],
            'max_tokens': 4000,
            'n': 1,
            'stop': None,
            'temperature': 0.2,
        },
        headers=headers
    )

    response_data = response.json()
    content = response_data['choices'][0]['message']['content'].strip()
    title = content.split('title:')[1].split('\n')[0].strip()
    information_sheet = content.split('information sheet:')[1].strip()

    return title, information_sheet

# Function to save metadata
def save_metadata(directory, filename, metadata):
    metadata_dir = os.path.join(directory, 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)
    metadata_path = os.path.join(metadata_dir, f"{filename}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    return metadata_path

# Function to save normalized data
def save_normalized_data(directory, filename, normalized_data):
    normalized_data_dir = os.path.join(directory, 'normalized_data')
    os.makedirs(normalized_data_dir, exist_ok=True)
    normalized_data_path = os.path.join(normalized_data_dir, f"{filename}_normalized.csv")
    df = pd.DataFrame(normalized_data)
    df.to_csv(normalized_data_path, index=False)
    return normalized_data_path

# Function to save original CSV
def save_original_data(directory, filename, file):
    data_dir = os.path.join(directory, 'data')
    os.makedirs(data_dir, exist_ok=True)
    data_path = os.path.join(data_dir, f"{filename}.csv")
    
    file.seek(0)  # Move to the beginning of the file
    with open(data_path, 'wb') as f:
        f.write(file.read())
    
    return data_path

# Function to sanitize directory names
def sanitize_directory_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Function to ingest new data
def ingest_new_data(file, package):
    filename = os.path.splitext(file.filename)[0]
    metadata, normalized_data = generate_metadata_from_file(file)
    title, information_sheet = get_metadata_information(filename, metadata)

    title.replace("*", "")

    # Sanitize the title for directory name
    sanitized_title = sanitize_directory_name(title.replace(' ', '_'))
    title_dir = os.path.join('data', sanitized_title)
    os.makedirs(title_dir, exist_ok=True)

    # Save original data, metadata, and normalized data in the appropriate directories
    save_original_data(title_dir, filename, file)
    save_metadata(title_dir, filename, metadata)
    save_normalized_data(title_dir, filename, normalized_data)

    # Save title and information sheet
    with open(os.path.join(title_dir, 'title.txt'), 'w') as title_file:
        title_file.write(title)
    
    with open(os.path.join(title_dir, 'datainfo.md'), 'w') as info_file:
        info_file.write(information_sheet)
    
    print(f"Title: {title}")
    print("Information sheet saved to datainfo.md")
