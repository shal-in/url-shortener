from flask import Flask, render_template, request, redirect, jsonify, send_file, abort
import os
import json
import helper

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Firebase stuff
db = helper.get_db_ref("cred_key.json")

# Cloud Storage stuff
bucket = helper.get_bucket("shalin_test_bucket")

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
    
    url = helper.get_url_for_shortener(db, shortener)

    if url:
        return jsonify({"url": url})
    else:
        return jsonify({"error": f"No URL found for shortener '{shortener}'"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return "No selected file", 400

    # Save the file to the upload folder
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return "File uploaded successfully", 200

if __name__ == '__main__':
    app.run(port=7000, debug=True)