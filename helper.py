with open("password.txt", "r") as file:
    CORRECT_PASSWORD = file.read()

def check_password(password):
    return password == CORRECT_PASSWORD

def shortener_taken(shortener):
    pass

def upload_url_to_db(database, shortener, url):
    pass

def upload_file_to_db(database, shortener, file):
    pass

def verify_form(form):
    if not check_password(form.password):
        # incorrect password
        pass

    if shortener_taken(form.shortener):
        # shortener taken
        pass

    return True

def handle_form(form):
    if not verify_form(form):
        # a problem, handle and return problem
        pass

    if form.type == "url":
        # upload url, return success/failure
        pass

    elif form.type == "file":
        # upload file, return success.failure
        pass