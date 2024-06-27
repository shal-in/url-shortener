from flask import Flask, render_template, request, redirect, jsonify, send_file, abort
import os
import json
import helper
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv('.env')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Load necessary environment variables
GOOGLE_APPLICATIONS_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATIONS_CREDENTIALS_JSON")
EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")

# If environment variables are not found in .env, set them from system environment
if not (GOOGLE_APPLICATIONS_CREDENTIALS_JSON and EXPECTED_PASSWORD):
    GOOGLE_APPLICATIONS_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")

# Parse JSON if credentials are provided as a JSON string
if GOOGLE_APPLICATIONS_CREDENTIALS_JSON:
    GOOGLE_APPLICATION_CREDENTIALS = json.loads(GOOGLE_APPLICATIONS_CREDENTIALS_JSON)

# Firebase stuff
db = helper.get_db_ref(GOOGLE_APPLICATION_CREDENTIALS)

# Cloud Storage stuff
bucket = helper.get_bucket(GOOGLE_APPLICATION_CREDENTIALS, "shalin_test_bucket")

# Routes and API requests
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/submit-url", methods=["POST"])
def submit_url_form():
    form = request.get_json()
    
    print (form)
    
    # Verify and handle the form
    success, message = helper.handle_url_form(db, form)
    
    if success:
        response = {'status': 'success', 'message': message}
    else:
        response = {'status': 'error', 'message': message}
    
    return jsonify(response)

@app.route("/api/submit-file", methods=["POST"])
def submit_file_form():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    jsonData = request.form.get("jsonData")

    if jsonData:
        try:
            form = json.loads(jsonData)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON data"}), 400
    else:
        return jsonify({"error": "No JSON data provided"}), 40
    
    success, message = helper.handle_file_form(db, bucket, form, file)

    if success:
        response = {'status': 'success', 'message': message}
    else:
        response = {'status': 'error', 'message': message}
    
    return jsonify(response)

@app.route("/api/get-url", methods=["GET"])
def get_url():
    shortener = request.args.get("shortener")

    if not shortener:
        return jsonify({"error": "No shortener provided"}), 400
    
    response = helper.get_url_for_shortener(db, bucket, shortener)

    if response:
        return jsonify(response)
    else:
        return jsonify({"error": f"No URL found for shortener '{shortener}'"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)