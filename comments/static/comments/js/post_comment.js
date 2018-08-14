import {addReplyFormSubmitListener, toggleReplyForm} from './main.js';

// ajax for comments
function createComment(textarea){
    $.ajax({
        url : '/comments/add_comment/',
        type : "POST",
        data : { 
            text: textarea.val()
        }, 
        success : function(newComment) {
            textarea.val(''); // remove the value from the input
            if ($('#no-comments-yet-message')) $('#no-comments-yet-message').remove()
            addComment(newComment);
            fadeIn();
        },
        error : function(xhr,errmsg) {
            $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}

function addComment(comment){
    $('#comments').prepend(comment); 
    addReplyButtonListener();
    addReplyFormSubmitListener('#reply-form-' + newCommentId());
}

function addReplyButtonListener(){
    let commentId = newCommentId();
    $('#reply-button-' + commentId).click(function(){
        toggleReplyForm(commentId); 
    });
}

function newCommentId() {
    let newComment =  $('.comment').first();
    return newComment.attr('id');
}

function fadeIn(){
    $('.comment').first().hide().fadeIn(1000)
}

export default createComment;