from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

@app.route("/")
def index():
    return "index"

if __name__ == '__main__':
    app.run(port=7000, debug=True)