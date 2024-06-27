from flask import Flask, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = "secretkey12"

GOOGLE_APPLICATION_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_APPLICATION_CREDENTIALS = json.loads(GOOGLE_APPLICATION_CREDENTIALS_JSON)
EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")

@app.route("/")
def index():
    data = {"key_json": GOOGLE_APPLICATION_CREDENTIALS, "expected_password": EXPECTED_PASSWORD}
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)