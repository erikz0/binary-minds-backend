import requests
import os
import json
import logging
import subprocess
import tempfile
import re
import base64 

logger = logging.getLogger(__name__)

# In-memory storage for session contexts
session_contexts = {}

def check_if_action_requested(user_message):
    prompt = f"""
    The user has sent the following message: "{user_message}".
    Please include 'GENERATE_GRAPH' if the user's message explicitly requests a graph, 'GENERATE_PYTHON_CODE' if numerical analysis, calculations, or data manipulation using Python code could assist in answering the user's query, or 'DONT_GENERATE_GRAPH_OR_CODE' otherwise.
    Only answer 'GENERATE_GRAPH' if a visualization is requested directly.
    Answer 'GENERATE_PYTHON_CODE' if the user's query involves data analysis, calculations, or manipulations that require executing Python code.
    Answer 'DONT_GENERATE_GRAPH_OR_CODE' if the user's query is general advice, questions about the data without the need for numerical analysis, or pertains to a graph or code without requiring their generation.
    Please make sure your answer has this format: Answer: <answer>
    Please also include a brief explanation of your answer.
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.getenv('ICED_DEMO_API_KEY')}",
    }

    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            'model': 'gpt-4o-2024-05-13',
            'messages': [
                {'role': 'system', 'content': 'You are an assistant that determines user intent.'},
                {'role': 'user', 'content': prompt},
            ],
            'max_tokens': 1000,
            'n': 1,
            'stop': None,
            'temperature': 0.2,
        },
        headers=headers
    )

    response_data = response.json()

    gpt_response = response_data['choices'][0]['message']['content'].strip()

    logger.info(f"GPT gpt_response to action request: {gpt_response}")

    answer_pattern = r"Answer: (\w+)"
    
    # Search for the pattern in the text
    match = re.search(answer_pattern, gpt_response)
    
    # If a match is found, return the captured group
    if match:
        answer = match.group(1)
    else:
        answer = 'DONT_GENERATE_GRAPH_OR_CODE'

    if 'DONT_GENERATE_GRAPH_OR_CODE' in answer:
        return 'DONT_GENERATE_GRAPH_OR_CODE'
    elif 'GENERATE_GRAPH' in answer:
        return 'GENERATE_GRAPH'
    elif 'GENERATE_PYTHON_CODE' in answer:
        return 'GENERATE_PYTHON_CODE'
    else:
        return 'DONT_GENERATE_GRAPH_OR_CODE'

def load_metadata(package, filename):
    filename = filename.replace(".csv", "")
    metadata_path = os.path.join('data', package, 'metadata', f"{filename}_metadata.json")
    print(f"Metadata path: {metadata_path}")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata
    else:
        raise FileNotFoundError(f"Metadata file not found for package {package} and filename {filename}")
    
def string_to_base64(input_string):
    # Convert the string to bytes
    string_bytes = input_string.encode('utf-8')
    # Encode the bytes to Base64
    base64_bytes = base64.b64encode(string_bytes)
    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def handle_chat_request(token, data):
    user_message = data['message']
    package = data['package']
    filename = data['filename']
    session_id = string_to_base64(data['package']) + string_to_base64(data['filename']) + token

    print(f"Received message from user: {user_message}")
    print(f"Received package: {package}, filename: {filename}")

    # Retrieve the session context or create a new one
    session_context = session_contexts.get(session_id, [
        {"role": "system", "content": "You are an assistant built to help people analyze, generate graphs, and understand a dataset. You will be receiving the dataset's metadata with every message."}
    ])

    logger.info(f"Current session context: {session_context}")

    try:
        metadata = load_metadata(package, filename)
        metadata_string = json.dumps(metadata)

        action_requested = check_if_action_requested(user_message)

        logger.info(f'action_requested: {action_requested}')
        
        if action_requested == 'GENERATE_GRAPH':
            prompt = f"""
            Here is the metadata from the dataset: {metadata_string}.
            Please generate JavaScript code using Chart.js to plot a graph based on the user's request: {user_message}.
            The graph should have clearly labeled legends, clearly labeled axes and a sorted X-Axis.
            The code should use the variable 'dataset' (already defined in the outer scope) to reference the data, and ensure the code uses this variable to populate the chart.
            The code should be ready to execute in a React component and render the graph inside a given HTML container with id 'graph-container'.
            Ensure the code handles undefined or null values appropriately, avoiding errors such as trying to call methods on undefined or null values.
            Do not redeclare the 'dataset' variable in the code. Do not include import statements, React component definitions, or any other extraneous content. Only include the JavaScript code to initialize and render the chart inside the 'graph-container' element.
            Before giving the Javascript code, could you also include a brief 1-2 sentence summary of the graph.
            """

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {os.getenv('ICED_DEMO_API_KEY')}",
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                json={
                    'model': 'gpt-4o-2024-05-13',
                    'messages': session_context + [
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 1000,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()
            bot_message = response_data['choices'][0]['message']['content'].strip()
            code_match = bot_message.split('```javascript')

            logger.info(f"CHAT GPT CHAT RESPONSE: {response_data}")
            
            if len(code_match) > 1:
                summary = code_match[0]
                code = code_match[1].split('```')[0].strip()
            else:
                summary = f'This is a graph for query: {user_message}'
                code = bot_message

            code = code.replace("const ctx = document.getElementById('graph-container').getContext('2d');", '').strip()

            # Update the session context
            session_context.append({'role': 'user', 'content': user_message})
            session_context.append({'role': 'assistant', 'content': bot_message})
            session_contexts[session_id] = session_context

            return {'reply': bot_message, 'graphCode': code, 'summary': '', 'sessionId': session_id}
        
        elif action_requested == 'GENERATE_PYTHON_CODE':
            prompt = f"""
            Here is the metadata from the dataset: {metadata_string}.
            Please generate Python code to perform data analysis based on the user's request: {user_message}.
            The code should reference the pre-defined pandas dataframe 'dataset' (already defined in the outer scope).
            Ensure the code handles undefined or null values appropriately, avoiding errors such as trying to call methods on undefined or null values.
            Keep in mind that the dataset might contain columns with non-numerical values, so workaround this if it is the case
            Include import statements for any necessary libraries, such as scipy.stats for statistical tests.
            Include print statements for all the output results.
            Do not include any other extraneous content. Only include the Python code to perform the requested analysis.
            Before giving the Python code, could you also include a brief 1-2 sentence summary of the analysis to be performed.
            """

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {os.getenv('ICED_DEMO_API_KEY')}",
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                json={
                    'model': 'gpt-4o-2024-05-13',
                    'messages': session_context + [
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 1000,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()
            bot_message = response_data['choices'][0]['message']['content'].strip()
            code_match = bot_message.split('```python')

            logger.info(f"CHAT GPT CHAT RESPONSE: {response_data}")

            if len(code_match) > 1:
                summary = code_match[0]
                code = code_match[1].split('```')[0].strip()
            else:
                summary = f'This is a data analysis for query: {user_message}'
                code = bot_message

            # Execute the generated Python code
            dataset_path = os.path.join('data', package, 'normalized_data', f"{filename.replace('.csv', '')}_normalized.csv")
            dataset_path = dataset_path.replace('\\', '\\\\')  # Escape backslashes for Windows paths
            python_code = f"""
import pandas as pd

dataset = pd.read_csv('{dataset_path}')
{code}
"""
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_py_file:
                temp_py_file.write(python_code.encode('utf-8'))
                temp_py_file_path = temp_py_file.name

            try:
                result = subprocess.check_output(['python', temp_py_file_path], stderr=subprocess.STDOUT)
                output = result.decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                output = f"Error executing Python code: {e.output.decode('utf-8').strip()}"
            finally:
                os.remove(temp_py_file_path)

            logger.info(f"output: {output}")

            # Generate a better response using GPT
            better_response_prompt = f"""
            The user has asked the following question: "{user_message}".
            Python code was ran, generating an output
            The output of the Python code is: "{output}".
            Please generate a concise and clear response to the user's question incorporating the output.
            Please tailor your response around answering the question to someone who might not understand all scientific terms
            """

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                json={
                    'model': 'gpt-4o-2024-05-13',
                    'messages': [
                        {'role': 'system', 'content': 'You are an assistant that generates clear and concise responses based on the given information.'},
                        {'role': 'user', 'content': better_response_prompt},
                    ],
                    'max_tokens': 500,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()
            better_response = response_data['choices'][0]['message']['content'].strip()

            # Update the session context
            session_context.append({'role': 'user', 'content': user_message})
            session_context.append({'role': 'assistant', 'content': better_response})
            session_contexts[session_id] = session_context

            return {'reply': better_response, 'sessionId': session_id}

        else:
            # If no graph or python code is requested, just call ChatGPT with the user message.
            prompt = f"""
            Please respond to the user message in plain text. Try to keep the message under 3 sentences, if possible.
            This message will be displayed in a chatbox capable of only displaying plain text.
            User message: "{user_message} Metadata for the dataset: {metadata_string}"
            """

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {os.getenv('ICED_DEMO_API_KEY')}",
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                json={
                    'model': 'gpt-4o-2024-05-13',
                    'messages': session_context + [
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 1000,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()

            logger.info(f"GPT RESPONSE: {response_data}")

            bot_message = response_data['choices'][0]['message']['content'].strip()

            # Update the session context
            session_context.append({'role': 'user', 'content': user_message})
            session_context.append({'role': 'assistant', 'content': bot_message})
            session_contexts[session_id] = session_context

            return {'reply': bot_message, 'sessionId': session_id}
    except Exception as e:
        logger.error(f"Error in handle_chat_request: {e}")
        return {'error': str(e)}
