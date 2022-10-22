const EMAIL_REGEXP = /^(([^<>()[\].,;:\s@"]+(\.[^<>()[\].,;:\s@"]+)*)|(".+"))@(([^<>()[\].,;:\s@"]+\.)+[^<>()[\].,;:\s@"]{2,})$/iu;
const PASSWORD_REGEXP = /(?=.*\d)(?=.*[a-z])/i;

let registerForm = document.getElementsByClassName('register-form')[0];
let registerSubmit = document.getElementsByClassName('register-submit')[0];
let registerInputs = registerForm.getElementsByTagName('input');

registerInputs[0].onchange = function () {
    let email = registerInputs[0].value;
    if (checkEmail(email)) {
        registerInputs[0].style.borderColor = 'chartreuse';
        registerInputs[0].style.borderSize = '10px';
    } else {
        registerInputs[0].style.borderColor = 'red';
    };
};

registerInputs[1].onchange = function () {
    let name = registerInputs[1].value;
    if (checkName(name)) {
        registerInputs[1].style.borderColor = 'chartreuse';
    } else {
        registerInputs[1].style.borderColor = 'red';
    };
};

registerInputs[2].onchange = function () {
    let password = registerInputs[2].value;
    if (checkPassword(password)) {
        registerInputs[2].style.borderColor = 'chartreuse';
    } else {
        registerInputs[2].style.borderColor = 'red';
    };
};

registerInputs[3].onchange = function () {
    let password = registerInputs[3].value;
    if (checkPasswordTwo(password)) {
        registerInputs[2].style.borderColor = 'chartreuse';
        registerInputs[3].style.borderColor = 'chartreuse';
    } else {
        registerInputs[2].style.borderColor = 'red';
        registerInputs[3].style.borderColor = 'red';
    };
};

function checkEmail (email) {
    return EMAIL_REGEXP.test(email);
};

function checkName (name) {
    if (name.length >= 1 && name.length <= 16) {
        return true;
    };
    return false;
};

function checkPassword (password) {
    if (password.length >= 8) {
        return PASSWORD_REGEXP.test(password);
    } else {
        return false;
    };
};

function checkPasswordTwo (password) {
    if (password.length >= 8 && PASSWORD_REGEXP.test(password)) {
        if (registerInputs[2].value == password) {
            return true;
        } else {
            return false;
        };
    } else {
        return false;
    };
};

registerSubmit.onclick = function() {
    let email = registerInputs[0].value;
    let name = registerInputs[1].value;
    let password1 = registerInputs[2].value;
    let password2 = registerInputs[3].value;
    if (checkEmail(email) && checkName(name) && checkPassword(password1) && checkPasswordTwo(password2)) {
        registerForm.submit();
    };
};