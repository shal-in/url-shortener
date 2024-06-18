# General helper
from datetime import datetime, timedelta
import os
import json
import io
import base64
import mimetypes
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Firebase stuff
def get_db_ref(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    return firestore.client()

def get_collection_ref(db, collection):
    return db.collection(collection)

def add_to_collection(data, collection_ref):
    key = data['shortener']
    collection_ref.document(key).set(data)

    return True

def shortener_taken(shortener, collection):
    doc_ref = collection.document(shortener)
    doc = doc_ref.get()

    if doc.exists:
        return doc
    
    return None



# Cloud storage stuff
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cred_key.json"

storage_client = storage.Client()

def get_bucket(bucket_name):
    return storage_client.get_bucket(bucket_name)


def upload_to_bucket(blob_name, file_content, bucket_name, content_type=None):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # If content type is not provided, guess it based on the file extension
        if content_type is None:
            content_type, _ = mimetypes.guess_type(blob_name)

        # Set content type when uploading the file content
        blob.upload_from_string(file_content, content_type=content_type)

        return True
    except Exception as e:
        print(f"Error uploading to bucket: {e}")
        return False
    
def generate_signed_url(blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)

        if blob.exists():
            signed_url = blob.generate_signed_url(expiration=timedelta(hours=24))
            return signed_url
        
        print(f"Blob {blob_name} does not exist in bucket.")
        return False
    except Exception as e:
        print (e)
        return False
    
def generate_file_content(blob_name, bucket):
    try:
        blob = bucket.blob(blob_name)
        
        # Download the file content as bytes
        file_content = blob.download_as_bytes()

        # Encode the file content using Base64
        encoded_file_content = base64.b64encode(file_content).decode('utf-8')

        return encoded_file_content
    
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

# Write to database
CORRECT_PASSWORD = os.getenv("EXPECTED_PASSWORD")

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

def handle_url_form(db, form):
    active_collection_ref = get_collection_ref(db, "active")

    valid, error_message = verify_form(form, active_collection_ref)
    if not valid:
        return False, error_message

    data = {
        "shortener": form["shortener"],
        "type": "url",
        "url": form["url"],
        "time added": get_current_time()
    }

    if add_to_collection(data, active_collection_ref):
        return True, "URL added successfully"

    return False, "Invalid form type"

def handle_file_form(db, bucket, form, file):
    active_collection_ref = get_collection_ref(db, "active")

    valid, error_message = verify_form(form, active_collection_ref)
    if not valid:
        return False, error_message
    
    file_content = file.read()
    blob_name = file.filename
    # Get the file size
    file_size = len(file_content)

    max_size = 50 * 1024 * 1024  # Example: 50 MB limit
    if file_size > max_size:
        signed_url = True
    else:
        signed_url = False

    signed_url = False # remove this line after testing

    data = {"shortener": form["shortener"],
            "type": "file",
            "signed url": signed_url,
            "blob name": blob_name,
            "time added": get_current_time()}
    
    if upload_to_bucket(blob_name, file_content, bucket):
        if add_to_collection(data, active_collection_ref):
            return True, "File uploaded successfully"
        
    return False, "Error with file upload"

# Read from database (API)
def get_url_for_shortener(db, bucket, shortener):
    active_collection_ref = get_collection_ref(db, "active")
    doc = shortener_taken(shortener, active_collection_ref)

    if doc:
        data = doc.to_dict()
        if data["type"] == "url":
            return {"url": data["url"]}
        if data["type"] == "file":
            if data["signed url"]:
                return {"url": generate_signed_url(data["blob name"], bucket)}
            if not data["signed url"]:
                return {"file name": data["blob name"],
                        "file content": generate_file_content(data["blob name"], bucket)}

    return None