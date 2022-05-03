function setFormMessage(formElement, type, message) {
    const messageElement = formElement.querySelector(".form__message");
    
    // Reset the message
    messageElement.textContent = message;
    messageElement.classList.remove("form__message--success", "form__message--error");
    //Set correct message
    messageElement.classList.add("form__message--"+type);
}

function setInputError(inputElement, message) {
    inputElement.classList.add("form__input--error");
    inputElement.parentElement.querySelector(".form__input-error-message").textContent = message;
}

function clearInputError(inputElement) {
    inputElement.classList.remove("form__input--error")
    inputElement.parentElement.querySelector(".form__input-error-message").textContent = "";
}

function getTextboxContent(inputElement) {
    let content = document.getElementById(inputElement).value;
    return content;
}

function stringToHash(string) {
    return new Promise(function(resolve) {
        var hash = 0;

        if (string.length == 0) {
            return hash;
        }

        for (i = 0; i < string.length; i++) {
            char = string.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash
        }

        return resolve(hash)
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("#login");
    const createAccountForm = document.querySelector("#createAccount");

    // Toggle the create account form
    document.querySelector("#linkCreateAccount").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.add("form--hidden");
        createAccountForm.classList.remove("form--hidden");
    });

    //Toggle the Login Form
    document.querySelector("#linkLogin").addEventListener("click", e => {
        e.preventDefault();
        loginForm.classList.remove("form--hidden");
        createAccountForm.classList.add("form--hidden");
    });
    
    loginForm.addEventListener("submit", async e => {
        e.preventDefault();
        
        // Get entered Username and password
        let loginUsername = getTextboxContent("loginUsername");
        let loginPassword = await stringToHash(getTextboxContent("loginPassword"));
        // Create the request
        var request = new XMLHttpRequest();
        // Send to correct file
        request.open('POST', './api', true);
        // Set content type and encoding
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        request.setRequestHeader('Content-Encoding', document.characterSet);
        // Send the contents
        request.send(`tagPOST=login&loginUsername=${loginUsername}&loginPassword=${loginPassword}`);
        // Check response 
        request.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.response == 'Successful login.') {
                    window.location.href = `repositories`;
                } else {
                    setFormMessage(loginForm, "error", "Invalid Username/Password combination");
                }
            }
        }
    });
    
    createAccountForm.addEventListener('submit', async e => {
        e.preventDefault();

        // Get entered username and password
        let signupUsername = getTextboxContent('signupUsername');
        let signupPassword = getTextboxContent('signupPassword');
        let signupPasswordCheck = getTextboxContent('signupPasswordCheck');
        // Create the request
        var request = new XMLHttpRequest();
        // Send to correct file
        request.open('POST', './api', true);
        // Set content tpye and encoding
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        request.setRequestHeader('Content-Encoding', document.characterSet);
        // Check if username and password valid
        let allowedCharacters = /^[A-Za-z0-9_-]+$/
        let validUsername = allowedCharacters.test(signupUsername)
        let validPassword = allowedCharacters.test(signupPassword)
        // TODO: you can make that more organize by putting the check somewhere else maybe that its also done in real
        // time instead of on button press?
        if (validPassword == true && validUsername == true) {
            // Send the contents
            if (signupPassword === signupPasswordCheck) {
                // Hash password
                signupPassword = await stringToHash(signupPassword);
                request.send(`tagPOST=signup&signupUsername=${signupUsername}&signupPassword=${signupPassword}`);
            } else {
                setFormMessage(createAccountForm, "error", "Passwords don't match.");
            }
        } else {
            setFormMessage(createAccountForm, "error", "Please only use letters and numbers for your username and password.")
        }
        // Check response
        request.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.response == 'Successful signup.') {
                    window.location.href = '/repositories';
                } else if (this.response == 'Username already in use.') {
                    setFormMessage(createAccountForm, "error", "Username taken.");
                }
            }
        }
    });

    document.querySelectorAll(".form__input").forEach(inputElement => {
        inputElement.addEventListener("blur", e => {
            if (e.target.id === "signupUsername" && e.target.value.length > 0 && e.target.value.length < 10) {
                setInputError(inputElement, "Username must be atleast 10 characters in length.")
            }
        });

        inputElement.addEventListener("input", e => {
            clearInputError(inputElement);
        });
    });
});