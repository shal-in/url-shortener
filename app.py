from flask import Flask, render_template, request, redirect, url_for, jsonify
import helper

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-form", methods=["POST"])
def submit_form():
    data = request.get_json()
    print (data)
    response = {'status': 'success', 'data_received': data}
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=7000, debug=True)