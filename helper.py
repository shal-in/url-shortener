# General helper
from datetime import datetime, timedelta
import mimetypes

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Firebase stuff
def get_collection_ref(db, collection):
    return db.collection(collection)

def add_to_collection(data, collection_ref):
    key = data['shortener']
    collection_ref.document(key).set(data)

    return True

def upload_file_to_db(data, db):
    pass

def shortener_taken(shortener, collection):
    doc_ref = collection.document(shortener)
    doc = doc_ref.get()

    if doc.exists:
        return doc
    
    return None

# Cloud storage stuff
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

def generate_signed_url(blob_name, bucket, duration=24):
    expiration_time = timedelta(hours=duration)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(
    version="v4",
    # This URL is valid for 15 minutes
    expiration=datetime.utcnow() + expiration_time,
    # Allow GET requests using this URL.
    method="GET",
    )

    return url

# Write to database
def check_password(password):
    return password == "example1"

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


# Read from database (API)
def get_url_for_shortener(db, bucket, shortener):
    active_collection_ref = get_collection_ref(db, "active")
    doc = shortener_taken(shortener, active_collection_ref)

    if doc:
        data = doc.to_dict()
        if data["type"] == "url":
            return data["url"]
        else:
            blob_name = data["blob name"]
            return generate_signed_url(blob_name, bucket, 24)
    return None
