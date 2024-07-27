# General helper
from datetime import datetime, timedelta
import os
import mimetypes
from google.cloud import storage
import base64

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Firebase stuff
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
def get_bucket(credentials, project_id, bucket_name):
    storage_client = storage.Client(credentials=credentials, project=project_id)
    bucket = storage_client.get_bucket(bucket_name)

    return bucket

def upload_to_bucket(blob_name, file_content, bucket, content_type=None):
    try:
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
    
def download_from_bucket1(blob_name, bucket):
    # Get the blob
    blob = bucket.blob(blob_name)

    # Download the blob's content as a string
    content = blob.download_as_string()

    # Determine the content type
    content_type = blob.content_type or 'application/octet-stream'

    return content, content_type

def download_from_bucket(blob_name, bucket):
    blob = bucket.blob(blob_name)

    # Download the content as bytes
    content = blob.download_as_bytes()
    
    # Determine the content type
    content_type = blob.content_type or 'application/octet-stream'

    # Encode content in Base64
    encoded_content = base64.b64encode(content).decode('utf-8')
    

    return encoded_content, content_type, blob_name


# Write to database
def check_password(password):
    if os.path.exists("password.txt"):
        with open("password.txt", 'r') as file:
            EXPECTED_PASSWORD = file.read()
    else:
        EXPECTED_PASSWORD = os.getenv("EXPECTED_PASSWORD")
    return password == EXPECTED_PASSWORD

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

    data = {"shortener": form["shortener"],
            "type": "file",
            "blob_name": blob_name,
            "time added": get_current_time()}
    
    # add file to bucket
    if upload_to_bucket(blob_name, file_content, bucket):
        if add_to_collection(data, active_collection_ref):
            return True, "File uploaded successfully"
        
    return False, "Error with file upload"


# Admin
def handle_admin_access_request(db, password):
    if not check_password(password):
        return False, "Incorrect password"

    active_collection_ref = get_collection_ref(db, "active")
    shorteners = get_all_documents(active_collection_ref)

    print (len(shorteners))
    return True, shorteners

def get_all_documents(collection_ref):    
    # Get all documents in the collection
    docs = collection_ref.stream()
    
    documents = []
    for doc in docs:
        documents.append(doc.to_dict())

    return documents

# Read from database (API)
def get_url_for_shortener(db, bucket, shortener):
    active_collection_ref = get_collection_ref(db, "active")
    doc = shortener_taken(shortener, active_collection_ref)

    if doc:
        data = doc.to_dict()
        if data["type"] == "url":
            return data["url"], "", ""
        else:
            blob_name = data["blob_name"]
            content, content_type, filename = download_from_bucket(blob_name, bucket)
            return content, content_type, filename
    return False, "", ""
