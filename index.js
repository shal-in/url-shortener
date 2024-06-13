console.log("index.js");

// Checkbox container and upload container
const urlCheckBoxEl = document.getElementById("checkbox-url");
const fileCheckBoxEl = document.getElementById("checkbox-file");

const urlUploadContainerEl = document.getElementById("upload-container-url");
const fileUploadContainerEl = document.getElementById("upload-container-file");


let checkboxState = "url";
urlCheckBoxEl.addEventListener("change", () => {checkboxFunction("url")});
fileCheckBoxEl.addEventListener("change", () => {checkboxFunction("file")});

const urlInputEl = document.getElementById("url-input");

const testUrlBtnEl = document.getElementById("test-url-btn");

testUrlBtnEl.addEventListener("click", () => {
    testUrlFunction(urlInputEl.value);
})

function testUrlFunction(string) {
    if (string) {
        if (!string.startsWith('https://') && !string.startsWith('http://')) {
            string = 'https://' + string;
        }
        window.open(string, '_blank').focus();
    }
    else {
        alert("please insert a url link to shorten")
    }
}

function checkboxFunction(input) {
    if (input === "url") {
        if (urlCheckBoxEl.checked) {
            fileCheckBoxEl.checked = false;
        }
        else {
            urlCheckBoxEl.checked = false;
            fileCheckBoxEl.checked = true;
        }
    } 
    else if (input === "file") {
        if (fileCheckBoxEl.checked) {
            urlCheckBoxEl.checked = false;
        }
        else {
            fileCheckBoxEl.checked = false;
            urlCheckBoxEl.checked = true;
        }
    } 

    if (urlCheckBoxEl.checked) {
        checkboxState = "url";
    }
    else if (fileCheckBoxEl.checked) {
        checkboxState = "file";
    }
    prepareUploadContainer(checkboxState);
}

function prepareUploadContainer(checkboxState) {
    if (checkboxState === "url") {
        fileUploadContainerEl.style.display = "none";
        urlUploadContainerEl.style.display = "inline";
    }
    else if (checkboxState === "file") {
        urlUploadContainerEl.style.display = "none";
        fileUploadContainerEl.style.display = "inline";
    }
}


// Shortener container
const shortenerInputEl = document.getElementById("shortener-input");


// Password container
const passwordInputEl = document.getElementById("password-input");
const showPasswordCheckboxEl = document.getElementById("show-password-checkbox");

showPasswordCheckboxEl.addEventListener("change", () => {
    if (showPasswordCheckboxEl.checked) {
        passwordInputEl.type = "text";
        
        setTimeout(() => {
            passwordInputEl.type = "password";
            showPasswordCheckboxEl.checked = false;
        }, 1500);
    }
})


// Submit container
const submitBtnEl = document.getElementById("submit-btn");

submitBtnEl.addEventListener("click", submitBtnFunction)
window.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        submitBtnFunction()
    }
})

function submitBtnFunction() {
    let input;
    let shortener = shortenerInputEl.value;
    let password = passwordInputEl.value;

    if (checkboxState === "url") {
        input = urlInputEl.value;
    }
    else if (checkboxState === "file") {
        input = "file to be added"
    }

    form = {
        "type": checkboxState,
        "input": input,
        "shortener": shortener,
        "password": password
    }

    console.log(form);
}

