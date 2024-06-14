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
const randomShortenerBtnEl = document.getElementById("generate-shortener-btn");
const shortenerUrlExampleBtnEl = document.getElementById("shortened-url-example-btn");
const shortenedUrlExampleEl = document.getElementById("shortened-url-example");

randomShortenerBtnEl.addEventListener("click", () => {
    shortenerInputEl.value = generateRandomString();
})

shortenerUrlExampleBtnEl.addEventListener("click", () => {
    alert(`this is just an example link. please press submit first.`);
})

function generateRandomString(length = 12) {
    const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let randomString = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        randomString += characters[randomIndex];
    }
    return randomString;
}

function isValidString(string) {
    const regex = /^[a-z0-9-]+$/;

    if (!regex.test(string)) {
        shortenerInputEl.value = string.slice(0, -1);
        return [false, "Shortener can only contain characters a-z, 0-9 and -"];
    }

    if (string.length < 4 || string.length > 20) {
        return [false, "Shortener must be 4-20 characters long"];
    }

    if (string.startsWith('-') || string.endsWith('-')) {
        return [false, "Shortener cannot start or end with - character"];
    }

    if (string.includes("--")) {
        return [false, "Shortener cannot contain consecutive - characters"];
    }

    return [true, ""];
}

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
        input = "file to be added";
    }

    if (!input) {
        alert("please insert a url or select a file");
        return
    }

    if(!shortener) {
        alert("please insert a shortener");
        return
    }

    let [valid, error] = isValidString(shortener);
    if (!valid) {
        alert(error);
        return
    }

    if (!password) {
        alert("please insert a password");
        return
    }

    form = {
        "type": checkboxState,
        "input": input,
        "shortener": shortener,
        "password": password
    }

    sendPOSTRequest(form);

    setTimeout(() => {
        urlInputEl.value = "";
        shortenerInputEl.value = "";
        passwordInputEl.value = "";
    }, 800);
}

function sendPOSTRequest(form) {
    fetch("/api/submit-form", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(form)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        return
    })
    .catch((error) => {
        console.error("Error", error);
    })
}

// Footer container
const footerBtnEls = Array.from(document.getElementsByClassName("footer-btn"));

for (let footerBtnEl of footerBtnEls) {
    let link = footerBtnEl.getAttribute("link");

    footerBtnEl.addEventListener("click", () => {
        window.open(link, "_blank");
    })
}