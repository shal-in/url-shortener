from flask import Flask, render_template, request, jsonify, make_response, redirect
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
import helper
import google.auth
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'   # Necessary for flashing messages

# FOR LOCAL DEVELOPMENT ONLY 
cred_path = "url-shortener-426321-0a521fcab6e0.json"
if os.path.exists(cred_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    cred = credentials.Certificate(cred_path)

# Obtain the application default credentials and project ID
credentials, project_id = google.auth.default()

# Initialize Google Cloud Storage
storage_client = storage.Client(credentials=credentials, project=project_id)
bucket = storage_client.get_bucket("url-file-uploads")

# Initialize Firebase Admin SDK for Firestore
firebase_admin.initialize_app()
db = firestore.client()

# Routes and API requests
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/<shortener>")
def shortener(shortener):
    content, content_type, file_name = helper.get_url_for_shortener(db, bucket, shortener)

    if content:
        if content_type == "": #url
            return redirect(content)
        else: #file
            decoded_content = base64.b64decode(content)

            file = make_response(decoded_content)
            file.headers['Content-Type'] = content_type
            file.headers['Content-Disposition'] = f'inline; filename="{file_name}"; filename*=UTF-8\'\'{file_name}'

            return file

    return jsonify({"error": "Failed to fetch data"}), 404
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

@app.route("/api/get-shortener", methods=["GET"])
def get_shortener():
    shortener = request.args.get("shortener")

    if not shortener:
        return jsonify({"error": "No shortener provided"}), 400
    
    content, content_type, file_name = helper.get_url_for_shortener(db, bucket, shortener)

    if content:
        if content_type == "":
            response_data = {
                "type": "url",
                "content": content
            }

            return jsonify(response_data), 200
        else:
            response_data = {
                "type": "file",
                "content": content,
                "content_type": content_type,
                "file_name": file_name
            }

            return jsonify(response_data), 200

    else:
        return jsonify({"error": f"No URL found for shortener '{shortener}'"}), 404

@app.route("/api/admin-access-request", methods=["POST"])
def admin_access_request():
    password = request.get_json()

    success, shorteners = helper.handle_admin_access_request(db, password)

    if success:
        response = {'status': 'success', 'shortenerData': shorteners}
    else:
        response = {'status': 'error', 'message': shorteners}
    
    return jsonify(response)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)