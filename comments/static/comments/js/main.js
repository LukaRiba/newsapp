import './csrf.js'; // Import an entire module for side effects only, without importing anything. This runs the module's global code, but doesn't actually import any values.
import createComment from './post_comment.js';
import createReply from './post_reply.js';

$(function() {
    addCommentFormSubmitListener();

    $('.reply-form').each(function(){
        addReplyFormSubmitListener(this);
    });

    addListenersToReplyButtons();
});

function addCommentFormSubmitListener() {
    $('#comment-form').on('submit', function(event){
        event.preventDefault();
        let textarea = $(this).find('textarea');
        createComment(textarea);
    });
}

function addReplyFormSubmitListener($selector) {
    $($selector).on('submit', function(event){
        event.preventDefault();
        let parentId = $(this).parent().attr('id') // comment model instance id (owner of replies, their ForeignKey) AND id of DOM comment div element
        let textarea = $(this).find('textarea'); 
        createReply(textarea, parentId);
    });
}

function addListenersToReplyButtons() {
    $('.comment').each(function(){
        let commentId = $(this).attr('id');
        $('#reply-button-' + commentId).click(function(){
            toggleReplyForm(commentId);
        });
    });
}

function toggleReplyForm(id){
    $('#reply-form-' + id ).toggle(); 
}

export {addReplyFormSubmitListener, toggleReplyForm};



