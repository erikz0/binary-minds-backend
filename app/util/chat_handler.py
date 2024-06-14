import requests
import os
import json
import logging
logger = logging.getLogger(__name__)

def check_if_graph_requested(user_message):
    prompt = f"""
    The user has sent the following message: "{user_message}".
    Determine if the user is requesting a graph to be generated from a dataset. Respond with "Yes" if a graph is requested, otherwise respond with "No".
    Just respond with yes or no, nothing else.
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
    return response_data['choices'][0]['message']['content'].strip()

def handle_chat_request(data):
    user_message = data['message']
    metadata = data['metadata']

    print(f"Received message from user: {user_message}")
    print(f"Received dataset and metadata from user")

    try:
        is_graph_requested = check_if_graph_requested(user_message)

        logger.info(f'is_graph_requested: {is_graph_requested}')
        
        if is_graph_requested.lower() == "yes":
            metadata_string = json.dumps(metadata)
            
            prompt = f"""
            Here is the metadata from the dataset: {metadata_string}.
            Please generate JavaScript code using Chart.js to plot a graph based on the user's request: {user_message}.
            The code should use the variable 'dataset' (already defined in the outer scope) to reference the data, and ensure the code uses this variable to populate the chart.
            The code should be ready to execute in a React component and render the graph inside a given HTML container with id 'graph-container'.
            Ensure the code handles undefined or null values appropriately, avoiding errors such as trying to call methods on undefined or null values.
            Do not redeclare the 'dataset' variable in the code. Do not include import statements, React component definitions, or any other extraneous content. Only include the JavaScript code to initialize and render the chart inside the 'graph-container' element.
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
                        {'role': 'system', 'content': 'You are a helpful assistant that creates custom code for graphing data.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 4096,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()
            bot_message = response_data['choices'][0]['message']['content'].strip()
            code_match = bot_message.split('```javascript')

            logger.info(f"CHAT GPT CHAT RESPONSE: {response}")
            
            if len(code_match) > 1:
                code = code_match[1].split('```')[0].strip()
            else:
                code = bot_message

            code = code.replace("const ctx = document.getElementById('graph-container').getContext('2d');", '').strip()

            return {'reply': bot_message, 'graphCode': code}
        else:

            metadata_string = json.dumps(metadata)

            # If no graph is requested, just call ChatGPT with the user message.
            prompt = f"""
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
                    'messages': [
                        {'role': 'system', 'content': 'You are a helpful assistant that assists with analyzing and answering questions about data'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': 4096,
                    'n': 1,
                    'stop': None,
                    'temperature': 0.2,
                },
                headers=headers
            )

            response_data = response.json()

            logger.info(f"GPT RESPONSE: ? {response_data}")

            bot_message = response_data['choices'][0]['message']['content'].strip()

            return {'reply': bot_message}
    except Exception as e:
        raise e