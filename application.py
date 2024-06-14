import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from app.util.chat_handler import handle_chat_request

application = app = Flask(__name__)

# Allow CORS for localhost and other origins
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Increase the limit for JSON payloads
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 401

# Serve static files from the "data" directory with API key check
@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

@app.route('/bm-chat', methods=['POST'])
def chat():
    logging.info("CHAT METHOD CALLED")
    data = request.get_json()
    logging.info(f"Received data: {data}")
    response = handle_chat_request(data)
    return jsonify(response)

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
    port = int(os.getenv('PORT', 8000))  # Get port from environment variable or fallback to 5000
    print(f"Port: {port}")

    app.run(port=port, debug=True)

if __name__ == '__main__':
    main()
