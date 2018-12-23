import {addReplyButtonListener, addReplyFormSubmitListener, addEditButtonListener, addEditFormListeners,
    addDeleteFormSubmitListener} from './main.js';
import {updateCommentsCounter, getCommentsCount, reportError} from './utils.js'
import {manageVisibleComments} from './manage_visible_comments.js';

// ajax for comments
function createComment(textarea){
    $.ajax({
        url : '/comments/create-comment/',
        type : "POST",
        data : { 
            text: textarea.val(),
            owner_id: window.comments.owner_id,
            owner_model: window.comments.owner_model,
        }, 
        success : function(newComment) {
            addComment(newComment);
            if(firstCreated()){
                removeNoCommentsMessage();
                addCommentsCounterToDOM();
            }   
            resetCommentForm(textarea);
            incrementCommentsCount();
            updateCommentsCounter();
            manageVisibleComments();
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function addComment(comment){
    $('#comments').prepend(comment);
    fadeInComment(); 
    addEventListenersToComment(newCommentId());
}

function addEventListenersToComment(id){
    addReplyButtonListener(id);
    addEditButtonListener(id);
    addEditFormListeners('#edit-form-' + id);
    addReplyFormSubmitListener('#reply-form-' + id);
    addDeleteFormSubmitListener('#delete-form-' + id);
}

function fadeInComment(){
    $('.comment').first().hide().fadeIn(1000)
}

function newCommentId() {
    let newComment =  $('.comment').first();
    return newComment.attr('id');
}

function resetCommentForm(textarea) {
    textarea.val('');
}

function firstCreated() {
    return $('.comment').length === 1;
}

function removeNoCommentsMessage() {
    $('#no-comments-yet-message').remove();
}

function incrementCommentsCount(){
    $('#comments-count').text(getCommentsCount() + 1);
}

function addCommentsCounterToDOM(){
    let commentsCounter = '<p id="comments-counter"><strong>1 comment</strong></p>'
    $('#title').after(commentsCounter);
}

export {
    createComment,
    addComment,
    addEventListenersToComment,
    fadeInComment,
    newCommentId,
    resetCommentForm,
    firstCreated,
    removeNoCommentsMessage,
    incrementCommentsCount,
    addCommentsCounterToDOM,
}