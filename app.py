from flask import Flask, render_template, request, redirect, url_for, jsonify
import helper

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

# Firebase stuff
db = helper.get_db_ref("cred_key.json")






# Routes and API requests
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/submit-form", methods=["POST"])
def submit_form():
    form = request.get_json()
    print(form)
    
    # Verify and handle the form
    success, message = helper.handle_form(db, form)
    
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
    

if __name__ == '__main__':
    app.run(port=7000, debug=True)