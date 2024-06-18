import os
import logging
import jwt
import datetime
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

@app.route('/data/<path:filename>')
@token_required
def serve_data(filename):
    return send_from_directory('data', filename)

@app.route('/bm-chat', methods=['POST'])
@token_required
def chat():
    logging.info("CHAT METHOD CALLED")
    data = request.get_json()
    logging.info(f"Received data: {data}")
    response = handle_chat_request(data)
    return jsonify(response)

@app.route('/data/list', methods=['GET'])
@token_required
def list_data():
    data_directory = 'data'
    datasets = []
    for filename in os.listdir(data_directory):
        if filename.endswith('.csv'):
            datasets.append({
                'name': filename,
                'description': f'Description for {filename}'
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
    port = int(os.getenv('PORT', 8000))  # Get port from environment variable or fallback to 8000
    print(f"Port: {port}")

    app.run(port=port, debug=True)

if __name__ == '__main__':
    main()
