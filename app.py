from flask import Flask, render_template, request, redirect, jsonify, send_file, abort
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
import helper

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages


# # LOCAL DEVELOPMENT ONLY (comment out for deployment)
# cred_path = "url-shortener-426321-0a521fcab6e0.json"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
# cred = credentials.Certificate(cred_path)

# DEPLOYMENT ONLY (comment out for local development)
cred = credentials.ApplicationDefault()


# Initialize Google Cloud Storage
storage_client = storage.Client()
bucket = storage_client.get_bucket("shalin_test_bucket")

# Initialize Firebase Admin SDK for Firestore
firebase_admin.initialize_app(cred)
db = firestore.client()


# Routes and API requests
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/submit-url", methods=["POST"])
def submit_url_form():
    form = request.get_json()
    
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