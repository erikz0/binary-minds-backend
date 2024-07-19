import os
import logging
import jwt
import datetime
import re
import pandas as pd
import json  # Add this import
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from functools import wraps
from app.util.chat_handler import handle_chat_request
from app.util.ingest_data import ingest_new_data, save_metadata, save_normalized_data, generate_metadata_from_file, normalize_data

application = app = Flask(__name__, static_folder='app/static/build')

# Allow CORS for localhost and other origins
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://www.binarytint.com/", "http://localhost:5000"]}})

# Increase the limit for JSON payloads
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

# Define routes
@app.route('/')
def index():
    return "Hello Users of Binary Mind's API!"

@app.route('/iced-data-analysis/', defaults={'path': ''})
@app.route('/iced-data-analysis/<path:path>')
def serve_react_app(path):
    logger.info(f"Requested path: {path}")
    full_path = os.path.join(app.static_folder, path)
    logger.info(f"Full path: {full_path}")
    
    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Define your correct password
CORRECT_PASSWORD = os.getenv('BM_PASSWORD')

BINARYMINDS_API_KEY = 'bm'

def check_internal_api_key(api_key_from_header):
    
    if not BINARYMINDS_API_KEY:
        logger.info(f'Missing Internal API key from env')
        return False
    
    if not api_key_from_header:
        logger.info("BINARYMINDS-API-KEY not found in headers of payload")
        return False

    if api_key_from_header == BINARYMINDS_API_KEY:
        return True
    else:
        return False

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

@app.route('/upload', methods=['POST'])
def upload_file():

    bm_api_key = request.headers.get('BINARYMINDS-API-KEY')
    if not (check_internal_api_key(bm_api_key)):
        return jsonify({
            "error": "Could not verify BinaryMinds API key"
        }), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        package = request.form.get('package', 'default_package')
        ingest_new_data(file, package)
        
        return jsonify({"message": "File processed successfully"}), 200
    else:
        return jsonify({"error": "Unsupported file type"}), 400

@app.route('/data/<package>/<filename>', methods=['GET'])
@token_required
def serve_data(package, filename):
    package_path = os.path.join('data', package, 'data')
    return send_from_directory(package_path, filename)

@app.route('/data-info/<package>', methods=['GET'])
@token_required
def serve_datainfo(package):
    datainfo_path = os.path.join('data', package)
    return send_from_directory(datainfo_path, 'datainfo.md')

@app.route('/data-pdf/<package>', methods=['GET'])
@token_required
def serve_datapdf(package):
    datapdf_path = os.path.join('data', package, 'pdfs')
    return send_from_directory(datapdf_path, 'datapdf.pdf')

@app.route('/normalized-data/<package>/<filename>', methods=['GET'])
@token_required
def serve_normalized_data(package, filename):
    filename = filename.replace(".csv", "")
    normalized_data_dir = os.path.join('data', package, 'normalized_data')
    normalized_data_path = os.path.join(normalized_data_dir, f"{filename}_normalized.csv")
    print(f"normalized_data_path: {normalized_data_path}")
    if os.path.exists(normalized_data_path):
        print("Normal data exists")
        data = pd.read_csv(normalized_data_path)
        data = data.fillna('')  # Fill NaN with an empty string or another placeholder
        normalized_data = data.to_dict(orient='records')
    else:
        data_path = os.path.join('data', package, 'data', filename + '.csv')
        data = pd.read_csv(data_path)
        normalized_data = normalize_data(data.to_dict(orient='records'))
        save_normalized_data(os.path.join('data', package), filename, normalized_data)
        #print(f"Normalized data: {normalized_data}")  # Logging the normalized data
    
    return jsonify(normalized_data)

@app.route('/metadata/data/<package>/<filename>', methods=['GET'])
@token_required
def serve_metadata(package, filename):
    filename = filename.replace(".csv", "")
    metadata_path = os.path.join('data', package, 'metadata', f"{filename}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        return jsonify(metadata)
    data_path = os.path.join('data', package, 'data', filename + '.csv')
    metadata, normalized_data = generate_metadata_from_file(data_path)
    save_metadata(os.path.join('data', package), filename, metadata)
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
            title_file = os.path.join(package_path, 'title.txt')
            data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
            
            title = 'No description available'
            if os.path.exists(title_file):
                with open(title_file, 'r') as file:
                    title = file.read().strip()

            print(title)
            
            for data_file in data_files:
                if '.csv' in data_file:
                    datasets.append({
                        'package': package,
                        'file': data_file,
                        'title': title
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
