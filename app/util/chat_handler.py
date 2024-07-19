import os
import json
import logging
import requests
import subprocess
import tempfile
import re
import base64
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFium2Loader
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

logger = logging.getLogger(__name__)

# In-memory storage for session contexts and PDFQuery instances
session_contexts = {}
pdf_query_instances = {}

class PDFQuery:
    def __init__(self, openai_api_key=None) -> None:
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        os.environ["ICED_DEMO_API_KEY"] = openai_api_key
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
        self.chain = None
        self.db = None

    def ask(self, question: str, chat_history: list) -> str:
        if self.chain is None:
            response = "Please, add a document."
        else:
            docs = self.db.get_relevant_documents(question)
            response = self.chain.run(input_documents=docs, question=question, chat_history=chat_history)
        return response

    def ingest(self, file_path: os.PathLike) -> None:
        loader = PyPDFium2Loader(file_path)
        documents = loader.load()
        splitted_documents = self.text_splitter.split_documents(documents)
        self.db = Chroma.from_documents(splitted_documents, self.embeddings).as_retriever()
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

    def ingest_folder(self, folder_path: os.PathLike) -> None:
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                file_path = os.path.join(folder_path, filename)
                self.ingest(file_path)

    def forget(self) -> None:
        self.db = None
        self.chain = None

def check_if_action_requested(user_message, session_context):
    prompt = f"""
    The user has sent the following message: "{user_message}".
    Please answer:
    'GENERATE_GRAPH', if the user's message would be best answered by generating a graph.
    'PREFORM_PYTHON_ANALYSIS', if the user's message would be best answered by running code to analyze the dataset, for all questions that require calculations done on the dataset.
    'DONT_GENERATE_GRAPH_OR_CODE', otherwise.
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
            'messages': [{'role': 'system', 'content': 'You are an assistant that determines user intent.'}] +
                        session_context + [
                        {'role': 'user', 'content': prompt},
                    ],
            'max_tokens': 1000,
            'n': 1,
            'stop': None,
            'temperature': 0.1,
        },
        headers=headers
    )

    response_data = response.json()

    logger.info(f"GPT response_data to action request: {response_data}")

    gpt_response = response_data['choices'][0]['message']['content'].strip()

    logger.info(f"GPT response to action request: {gpt_response}")

    answer_pattern = r"Answer: (\w+)"
    
    match = re.search(answer_pattern, gpt_response)
    
    if match:
        answer = match.group(1)
    else:
        answer = 'DONT_GENERATE_GRAPH_OR_CODE'

    return answer

def load_metadata(package, filename):
    filename = filename.replace(".csv", "")
    metadata_path = os.path.join('data', package, 'metadata', f"{filename}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return metadata
    else:
        raise FileNotFoundError(f"Metadata file not found for package {package} and filename {filename}")
    
def load_summary(package):
    summary_path = os.path.join('data', package, "summary.txt")

    logger.info(f"summary_path: {summary_path}")

    if os.path.exists(summary_path):
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = f.read()
            return summary
        except UnicodeDecodeError as e:
            logger.error(f"Error reading the summary file: {e}")
            raise
    else:
        raise FileNotFoundError(f"Summary file not found for package {package}")

def string_to_base64(input_string):
    string_bytes = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def trim_metadata(metadata):
    return [
        {
            "column": col["name"],
            "data_type": col["type"],
            **({"potential_values": col["potentialValues"]} if col["type"] != "float64" else {})
        }
        for col in metadata
    ]

def update_session_context(session_context, user_msg, assistant_msg):
    session_context.append({'role': 'user', 'content': user_msg})
    session_context.append({'role': 'assistant', 'content': assistant_msg})
    # Keep only the first system message and the last two pairs of user/assistant messages
    session_context = [session_context[0]] + session_context[-4:]

def handle_chat_request(token, data):
    user_message = data['message']
    package = data['package']
    filename = data['filename']
    session_id = string_to_base64(data['package']) + string_to_base64(data['filename']) + token

    metadata = load_metadata(package, filename)
    metadata = trim_metadata(metadata)
    metadata_string = json.dumps(metadata)

    summary = load_summary(package)

    logger.info(f"Summary: {summary}")

    session_context = session_contexts.get(session_id, [
        {"role": "system", "content": f"""
         You are a chatbot built to help uneducated people understand this dataset. You should take on the role of a teacher, treating the user as your student.
         Keep your responses concise, and use natural language when explaining complex topics, unless the user requests detailed analysis.
         You are a chatbot on the webpage of ICED (International Center for Evaluation & Development).
         If the user asks what you are capable of, let them know that you can answer questions about the dataset, its context, do statistical analysis of it, and generate graphs.
         
         Purpose Statement for ICED:
         "The International Centre for Evaluation and Development (ICED) is an independent, Africa-based and African-led not-for-profit think-tank that applies monitoring and evaluation (M&E) in the development sector. 
         ICED uses the outputs of evaluation to contribute to and enhance development outcomes and impacts, concentrating on Africa, where the need for its expertise is greatest."
         
         Summary of the dataset:
         {summary}

         You are also provided with the metadata of the dataset, which includes columns, data types, and potential values.
         Metadata of the dataset: {metadata_string}
        """}
    ])

    try:
        action_requested = check_if_action_requested(user_message, session_context[-4:])

        if action_requested == 'GENERATE_GRAPH':
            prompt = f"""
            Find the metadata of the dataset from previous context.
            Please generate JavaScript code using Chart.js to plot a graph based on the user's request: {user_message}.
            The graph should have clearly labeled legends, clearly labeled axes and a sorted X-Axis.
            Please include extensive console log statements in the code for debugging of all variables printing as strings in neat format.
            The code should use the variable 'dataset' (already defined in the outer scope) to reference the data, and ensure the code uses this variable to populate the chart.
            The code should be ready to execute in a React component and render the graph inside a given HTML container with id 'graph-container'.
            If you need to preform numerical operations on values in the dataset, assume values are read in as strings and convert them to the type you need.
            Ensure the code handles undefined or null values appropriately, avoiding errors such as trying to call methods on undefined or null values.
            Do not redeclare the 'dataset' variable in the code. Do not include import statements, React component definitions, or any other extraneous content. Only include the JavaScript code to initialize and render the chart inside the 'graph-container' element.
            Before giving the JavaScript code, could you also include a brief 1-2 sentence summary of the graph in this format:
            Summary: [<summary>]
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
                    'temperature': 0.1,
                },
                headers=headers
            )

            response_data = response.json()
            logger.info(f"response_data graph: {response_data}")
            bot_message = response_data['choices'][0]['message']['content'].strip()
            code_match = bot_message.split('```javascript')

            if len(code_match) > 1:
                summary = code_match[0].replace('Summary:', '')
                code = code_match[1].split('```')[0].strip()
            else:
                summary = f'This is a graph for query: {user_message}'
                code = bot_message

            code = code.replace("const ctx = document.getElementById('graph-container').getContext('2d');", '').strip()

            update_session_context(session_context, user_message, bot_message)
            session_contexts[session_id] = session_context

            return {'reply': bot_message, 'graphCode': code, 'summary': summary, 'sessionId': session_id}
        
        elif action_requested == 'PREFORM_PYTHON_ANALYSIS':

            num_tries = 0
            error = ""

            while num_tries < 3:

                prompt = f"""{error}
                Find the metadata of the dataset from previous context.
                Please generate Python code to perform data analysis based on the user's request: {user_message}.
                The code should reference the pre-defined pandas dataframe 'dataset' (already defined in the outer scope).
                Ensure the code handles undefined or null values appropriately, avoiding errors such as trying to call methods on undefined or null values.
                Keep in mind that the dataset might contain columns with non-numerical values, so workaround this if it is the case.
                If you need to preform numerical operations on values in the dataset, assume values are read in as strings and convert them to the type you need.
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
                        'max_tokens': 2000,
                        'n': 1,
                        'stop': None,
                        'temperature': 0.1,
                    },
                    headers=headers
                )

                response_data = response.json()

                logger.info(f"response_data: {response_data}")

                bot_message = response_data['choices'][0]['message']['content'].strip()
                code_match = bot_message.split('```python')

                if len(code_match) > 1:
                    summary = code_match[0]
                    code = code_match[1].split('```')[0].strip()
                else:
                    summary = f'This is a data analysis for query: {user_message}'
                    code = bot_message

                dataset_path = os.path.join('data', package, 'normalized_data', f"{filename.replace('.csv', '')}_normalized.csv")
                dataset_path = dataset_path.replace('\\', '\\\\')
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

                logger.info(f"Output: {output}")

                if "Error executing Python code" in output:
                    num_tries += 1
                    error += f"There was an error with the previous attempt at answering this prompt: {output} Try number: {num_tries}\n"
                    logger.info(f"Retrying generation of python code, Try Number: {num_tries}")
                    continue
                else:
                    break

            better_response_prompt = f"""
            The user has asked the following question: "{user_message}".
            Python code was ran, generating an output.
            The output of the Python code is: "{output}".
            Please generate a concise and clear response to the user's question incorporating the output.
            Please tailor your response around answering the question to someone who might not understand all scientific terms.
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
                    'temperature': 0.5,
                },
                headers=headers
            )

            response_data = response.json()
            better_response = response_data['choices'][0]['message']['content'].strip()

            python_output_context = f"""
            Raw Python script output: {output}\n
            """

            update_session_context(session_context, user_message, python_output_context + better_response)
            session_contexts[session_id] = session_context

            return {'reply': better_response, 'sessionId': session_id}

        else:

            # if session_id not in pdf_query_instances:
            #     pdf_folder_path = os.path.join('data', package, 'pdfs')
            #     if any(filename.endswith('.pdf') for filename in os.listdir(pdf_folder_path)):
            #         pdf_query_instances[session_id] = PDFQuery(openai_api_key=os.getenv('ICED_DEMO_API_KEY'))
            #         pdf_query_instances[session_id].ingest_folder(pdf_folder_path)
            #     else:
            #         pdf_query_instances[session_id] = None

            pdf_query = None #pdf_query_instances[session_id]

            if pdf_query:
                response = pdf_query.ask(user_message, session_context)
            else:
                prompt = f"""
                {user_message}
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
                        'temperature': 0.5,
                    },
                    headers=headers
                )

                response_data = response.json()
                response = response_data['choices'][0]['message']['content'].strip()
            
            update_session_context(session_context, user_message, response)
            session_contexts[session_id] = session_context

            return {'reply': response, 'sessionId': session_id}
    except Exception as e:
        logger.error(f"Error in handle_chat_request: {e}")
        return {'error': str(e)}
