import os
import logging
import jwt
import datetime
import re
import pandas as pd
import json  # Add this import
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
from app.util.chat_handler import handle_chat_request

application = app = Flask(__name__)

# Allow CORS for localhost and other origins
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Increase the limit for JSON payloads
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

# Define routes
@app.route('/')
def index():
    return "Hello Users of Binary Mind's API!"

# Define your correct password
CORRECT_PASSWORD = os.getenv('BM_PASSWORD')

@app.route('/check-bm-password', methods=['POST'])
def check_bm_password():
    data = request.get_json()
    password = data.get('password')

    if password == CORRECT_PASSWORD:
        token = jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'success': True, 'token': token})
    else:
        return jsonify({'success': False}), 401
    
@app.route('/check-token', methods=['GET'])
def check_token():
    token = request.headers.get('Authorization', None)
    if token:
        try:
            decoded = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])
            return jsonify({'valid': True}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'valid': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    return jsonify({'valid': False, 'error': 'Token missing'}), 401


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            logging.error(f"Token error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated_function

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

def generate_metadata_from_file(filepath):
    data = pd.read_csv(filepath)
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
    print(f"metadata: {metadata}")
    return metadata

def save_metadata(package, filename, metadata):
    metadata_dir = os.path.join('data', package, 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)
    metadata_path = os.path.join(metadata_dir, f"{filename}_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    return metadata_path

def save_normalized_data(package, filename, normalized_data):
    normalized_data_dir = os.path.join('data', package, 'normalized_data')
    os.makedirs(normalized_data_dir, exist_ok=True)
    normalized_data_path = os.path.join(normalized_data_dir, f"{filename}_normalized.csv")
    df = pd.DataFrame(normalized_data)
    df.to_csv(normalized_data_path, index=False)
    return normalized_data_path

@app.route('/data/<package>/<filename>', methods=['GET'])
@token_required
def serve_data(package, filename):
    package_path = os.path.join('data', package, 'data')
    return send_from_directory(package_path, filename)

@app.route('/normalized-data/<package>/<filename>', methods=['GET'])
@token_required
def serve_normalized_data(package, filename):
    normalized_data_dir = os.path.join('data', package, 'normalized_data')
    normalized_data_path = os.path.join(normalized_data_dir, f"{filename}_normalized.csv")
    if os.path.exists(normalized_data_path):
        return send_from_directory(normalized_data_dir, f"{filename}_normalized.csv")
    data_path = os.path.join('data', package, 'data', filename)
    data = pd.read_csv(data_path)
    normalized_data = normalize_data(data.to_dict(orient='records'))
    save_normalized_data(package, filename, normalized_data)
    return jsonify(normalized_data)

@app.route('/metadata/data/<package>/<filename>', methods=['GET'])
@token_required
def serve_metadata(package, filename):
    metadata_path = os.path.join('data', package, 'metadata', f"{filename}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return jsonify(metadata)
    data_path = os.path.join('data', package, 'data', filename)
    metadata = generate_metadata_from_file(data_path)
    save_metadata(package, filename, metadata)
    return jsonify(metadata)

@app.route('/bm-chat', methods=['POST'])
@token_required
def chat():
    logging.info("CHAT METHOD CALLED")
    data = request.get_json()
    token = request.headers.get('Authorization').split(" ")[1]
    logging.info(f"Received data: {data}")
    response = handle_chat_request(token, data)
    return jsonify(response)

@app.route('/data/list', methods=['GET'])
@token_required
def list_data():
    data_directory = 'data'
    datasets = []
    
    for package in os.listdir(data_directory):
        package_path = os.path.join(data_directory, package)
        data_path = os.path.join(package_path, 'data')
        if os.path.isdir(data_path):
            description_file = os.path.join(package_path, 'description.txt')
            data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
            
            description = 'No description available'
            if os.path.exists(description_file):
                with open(description_file, 'r') as desc_file:
                    description = desc_file.read().strip()
            
            for data_file in data_files:
                if '.csv' in data_file:
                    datasets.append({
                        'package': package,
                        'file': data_file,
                        'description': description
                    })
    
    return jsonify(datasets)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# List all registered endpoints
def list_endpoints():
    output = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(rule.methods)
            output.append((rule.rule, methods))
    return output

# Print the list of registered endpoints to the terminal
endpoints = list_endpoints()
for endpoint in endpoints:
    print(f"Endpoint: {endpoint[0]}, Methods: {endpoint[1]}")

# Ensure CORS headers are set correctly
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response

def main():
    port = int(os.getenv('PORT', 5000))  # Get port from environment variable or fallback to 5000
    print(f"Port: {port}")

    app.run(port=port, debug=True)

if __name__ == '__main__':
    main()
