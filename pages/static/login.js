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
    let password = registerInputs[1].value;
    if (checkPassword(password)) {
        registerInputs[1].style.borderColor = 'chartreuse';
        registerInputs[1].style.borderSize = '10px';
    } else {
        registerInputs[1].style.borderColor = 'red';
    };
};

function checkEmail (email) {
    return EMAIL_REGEXP.test(email);
};

function checkPassword (password) {
    if (password.length >= 8) {
        return PASSWORD_REGEXP.test(password);
    } else {
        return false;
    };
};

registerSubmit.onclick = function() {
    let email = registerInputs[0].value;
    let password = registerInputs[1].value;
    if (checkEmail(email) && checkPassword(password)) {
        registerForm.submit();
    };
};
