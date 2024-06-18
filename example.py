from flask import Flask, jsonify
import os

app = Flask(__name__)
app.secret_key = "secretkey12"

key_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")

@app.route("/")
def index():
    data = {"key_json": key_json, "expected_password": EXPECTED_PASSWORD}
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)