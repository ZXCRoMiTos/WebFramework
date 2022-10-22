let forms = {
    1: `{% include template('create_post_form.html') %}`,
    2: `{% include template('subscribe_form.html') %}`,
    3: `{% include template('subscribers_list.html') %}`,
    4: `<hr style="margin-bottom: 20px; ">` + `{% include template('create_category_form.html') %}`,
};

let formDiv = document.getElementsByClassName('form-space')[0];
let actionList = document.getElementsByClassName('action-menu')[0];
try {
    let options = actionList.getElementsByTagName('li');
    for (let i=0; i < options.length; i++) {
        options[i].onclick = function(){formDiv.innerHTML = forms[i + 1];};
    };
} catch (error) {
    console.log(error);
};

let data = document.getElementsByClassName('all-content-block');
for (let i=0; i < data.length; i++) {
    let content = data[i].getElementsByTagName('div');
    let post = content[0];
    data[i].onclick = function () { location = "http://127.0.0.1:8080/post/?id=" + post.id; };
    let editForm = content[1];
    post.classList.add('space');
    editForm.classList.add('hide');
    let editButton = post.getElementsByClassName('edit-post-button')[0];
    let flag = 1;
    try {
        editButton.onclick = function() {
            if (flag) {
                post.classList.remove('space');
                editForm.classList.remove('hide');
                editForm.classList.add('space');
                flag = 0;
            } else {
                post.classList.add('space');
                editForm.classList.add('hide');
                editForm.classList.remove('space');
                flag = 1;
            };
        };
    } catch (error) {
        console.log(error);
    };
};