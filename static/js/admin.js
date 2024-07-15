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

const submitBtnEl = document.getElementById("submit-btn");

submitBtnEl.addEventListener("click", submitBtnFunction);
document.addEventListener("keydown", (e) => {
    if (e.keyCode === 13) {
        submitBtnFunction();
    }
})

password;
function submitBtnFunction() {
    password = passwordInputEl.value;

    if (!password) {
        return
    }
    sendAdminAccessPOSTRequest(password);
    
    passwordInputEl.value = "";
}

function sendAdminAccessPOSTRequest(password) {
    fetch("api/admin-access-request", {
        method:  "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(password)
    })
    .then(response => response.json())
    .then(data => {
        success = (data.status === "success");

        if (!success) {
            alert(data.message);
            return;
        }

        setupAdminPage(data.shortenerData)
    })
}

function setupAdminPage(shorteners) {
    console.log(shorteners);
    console.log(password)
}