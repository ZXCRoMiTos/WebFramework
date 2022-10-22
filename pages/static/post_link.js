let allContentBlocks = document.getElementsByClassName('all-content-block');
let posts = document.getElementsByClassName('content-block');
for (let i=0; i < posts.length; i++) {
    let post = posts[i];
    allContentBlocks[i].onclick = function () { location = "http://127.0.0.1:8080/post/?id=" + post.id; };
};