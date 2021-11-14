function likeInteraction(ele) {
    const csrf = document.cookie.split("="); // document.cookie = 'csrftoken=aaaabbbbcccc'
    const csrftoken = csrf[1];
    const id = ele.dataset.postId;

    fetch(`/post-like-interaction/${id}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
        if(data === 200) { // like the post
            let likes = parseInt(ele.innerHTML);
            likes++;
            ele.innerHTML = likes;
            ele.classList.add("liked");
        }
        else if (data === 202) { // unlike the post
            let likes = parseInt(ele.innerHTML);
            likes--;
            ele.innerHTML = likes;
            ele.classList.remove("liked");
        }
        else if (data === 300) { // user is not logged in - redirect them
            window.location.replace("http://127.0.0.1:8000/login");
        }
        else if(data === 400) { // post method was not used - the user would be playing with the code
            alert("something went wrong please try again later")
        }
        else { // something went wrong on the server end
            alert("something went wrong please try again later")
        }
    })
    .catch(err => {
        console.log(err)
        alert("something went wrong please try again later")
    })
}

function toggleEdit(ele) {
    const post = ele.parentNode;
    const postContent = post.querySelector(".post-text");

    if(post.classList.contains("active")) {
        // hide edit post feature
        post.classList.remove("active");
        postContent.classList.remove("hide");
    }
    else {
        // show edit post feature
        post.classList.add("active");
        postContent.classList.add("hide");
    }
}

function saveEdit(ele) {
    const post = ele.parentNode;
    const updatedPost = post.querySelector(".edit-post").value;
    const postId = post.dataset.postId

    const csrf = document.cookie.split("="); // document.cookie = 'csrftoken=aaaabbbbcccc'
    const csrftoken = csrf[1];
    fetch(`/updatePost/${postId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        credentials: 'same-origin',
        body: updatedPost
    })
    .then(res => res.json())
    .then(data => {
        if(data === 200) { // post updated
            post.querySelector(".post-text").innerHTML = updatedPost;
            toggleEdit(ele)
        }
        else { // post not updated and 'edit post' feature hidden
            toggleEdit(ele)
        }
    })
    .catch(err => {
        console.log(err)
        alert("something went wrong please try again later")
    })
}