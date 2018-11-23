import {addReplyButtonListener,
        addReplyFormSubmitListener, 
        addEditButtonListener,
        addEditFormListeners,
        addDeleteFormSubmitListener,
        } from './main.js';
import {manageVisibleComments} from './manage_visible_comments.js';

// ajax for comments
function createComment(textarea){
    $.ajax({
        url : '/comments/create-comment/',
        type : "POST",
        data : { 
            text: textarea.val()
        }, 
        success : function(newComment) {
            addComment(newComment);
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
    fadeIn(); 
    addReplyButtonListener(newCommentId());
    addEditButtonListener(newCommentId());
    addEditFormListeners('#edit-form-' + newCommentId());
    addReplyFormSubmitListener('#reply-form-' + newCommentId());
    addDeleteFormSubmitListener('#delete-form-' + newCommentId());
}

function fadeIn(){
    $('.comment').first().hide().fadeIn(1000)
}

function newCommentId() {
    let newComment =  $('.comment').first();
    return newComment.attr('id');
}

function resetCommentForm(textarea) {
    textarea.val(''); // remove the value from the input
    if (isFirstComment()) removeNoCommentsMessage();
}

function isFirstComment() {
    return $('.comment').length === 1;
}

function removeNoCommentsMessage() {
    $('#no-comments-yet-message').remove();
}

function incrementCommentsCount(){
    $('#comments-count').text(countTotalComments() + 1);
}

function updateCommentsCounter(){
    let commentsCount = countTotalComments();
    let text = ' comments';
    if(commentsCount === 1) { //commentsCount is global variable defined in base.html
        text = ' comment';
        if(getCommentsCounter().length === 0){ // check if comment-counter is in the DOM,
            addCommentsCounterToDOM(); 
        }
    }
    getCommentsCounter().html('<strong>' + commentsCount + text + '</strong>');
}

function countTotalComments(){
    return Number($('#comments-count').text());
}

function addCommentsCounterToDOM(){
    let commentCounter = '<p id="comments-counter"><strong>1 comment</strong></p>'
    $('#title').after(commentCounter);
}

function getCommentsCounter(){
    return $('#comments-counter');
}

function reportError(xhr,errmsg) {
    $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}

export {
    countTotalComments,
    createComment,
    updateCommentsCounter,
    reportError
}