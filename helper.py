# General helper
from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Firebase stuff
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_db_ref(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    return firestore.client()

def get_collection_ref(db, collection):
    return db.collection(collection)

def add_to_collection(data, collection_ref):
    key = data['shortener']
    collection_ref.document(key).set(data)


def upload_file_to_db(data, db):
    pass

def shortener_taken(shortener, collection):
    doc_ref = collection.document(shortener)
    doc = doc_ref.get()

    if doc.exists:
        return doc
    
    return None

    


# Write to database
with open("password.txt", "r") as file:
    CORRECT_PASSWORD = file.read()

def check_password(password):
    return password == CORRECT_PASSWORD

# form = {
#     "type": checkboxState,
#     "input": input,
#     "shortener": shortener,
#     "password": password
# }

def verify_form(form, collection):
    if not check_password(form["password"]):
        # Check password
        return False, "Incorrect password"

    if shortener_taken(form["shortener"], collection):
        # shortener taken
        return False, "Shortener is already taken"

    return True, ""

def handle_form(db, form):
    active_collection_ref = get_collection_ref(db, "active")

    valid, error_message = verify_form(form, active_collection_ref)
    if not valid:
        return False, error_message

    if form["type"] == "url":
        data = {
            "shortener": form["shortener"],
            "type": "url",
            "url": form["input"],
            "time added": get_current_time()
        }

        add_to_collection(data, active_collection_ref)
        return True, "URL added successfully"

    elif form["type"] == "file":
        # upload file, return success.failure
        return False, "Unable to add files yet"

    return False, "Invalid form type"

# Read from database (API)
def get_url_for_shortener(db, shortener):
    active_collection_ref = get_collection_ref(db, "active")
    doc = shortener_taken(shortener, active_collection_ref)

    if doc:
        data = doc.to_dict()
        if data["type"] == "url":
            return data["url"]
        
    return None