import {addReplyButtonListener,
        addReplyFormSubmitListener, 
        addEditButtonListener,
        addEditFormListeners,
        addDeleteFormSubmitListener,
        addLoadMoreCommentsButtonListener
        } from './main.js';
import {updateLoadMoreCommentsButton, visibleCommentsCount} from './load_more_comments.js';

// ajax for comments
function createComment(textarea){
    $.ajax({
        url : '/comments/create_comment/',
        type : "POST",
        data : { 
            text: textarea.val()
        }, 
        success : function(newComment) {
            addComment(newComment);
            resetCommentForm(textarea);
            commentsCount++;
            updateCommentsCounter();
            manageVisibleCommentsCount();
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

function updateCommentsCounter(){
    var text = ' comments';
    if(commentsCount === 1) { //commentsCount is global variable defined in base.html
        text = ' comment';
        if(getCommentsCounter().length === 0){ // check if comment-counter is in the DOM,
            addCommentsCounterToDOM(); 
        }
    }
    getCommentsCounter().html('<strong>' + commentsCount + text + '</strong>');
}

function addCommentsCounterToDOM(){
    var commentCounter = '<p id="comments-counter"><strong>1 comment</strong></p>'
    $('#title').after(commentCounter);
}

function getCommentsCounter(){
    return $('#comments-counter');
}

// možda bi se moglo modificirati da radi i kod brisanja komentara..i onda sve funkcije prebaciti u manage_visible_comments.js ??
// refaktorirati funkciju - sigurno se može skratiti
// čini mi se da radi besprijekorno za sada
function manageVisibleCommentsCount(){
    var visibleComments = visibleCommentsCount()
    var previousBreakPoint = getPreviousBreakpoint(visibleComments);

    if(isBreakPoint(visibleComments)){
        if(commentsCount === visibleComments){
            addLoadMoreButtonToDOM();
        }
        removeExtraComment(); 
        updateLoadMoreCommentsButton();
    } 
    else if(visibleComments > previousBreakPoint) {
        while(!(visibleComments === previousBreakPoint  - 1)){ //because we want visible comments to be 5, 15, 25,... ect.
            removeExtraComment();
            visibleComments--;
        }
        addLoadMoreButtonToDOM();
        updateLoadMoreCommentsButton();
    }
}

// Calculates previous breakpoint number given visible comments number.
// For exaple, if num of visible comments is 22, it returns 16.
function getPreviousBreakpoint(visibleCommentsCount){
    if(visibleCommentsCount > 5){
        while(!(isBreakPoint(visibleCommentsCount))){
            visibleCommentsCount--;
        }
    }
    return visibleCommentsCount;
}

// returns true if there are 6, 16, 26, 36,... visible comments 
function isBreakPoint(visibleCommentsCount){
    return (visibleCommentsCount - 6) % 10 === 0;
}

function addLoadMoreButtonToDOM(){
    var button = '<button class="load-more-comments btn-md btn-primary">Load 1 more Comment</button>';
    $('#load-more-button-container').prepend(button);
    addLoadMoreCommentsButtonListener();
}

function removeExtraComment(){
    $('.comment').last().remove();
}

function reportError(xhr,errmsg) {
    $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}

export {
    createComment,
    updateCommentsCounter,
    reportError
}