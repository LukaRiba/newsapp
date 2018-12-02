import {addShowRepliesButtonListener, addEditButtonListener, addReplyButtonListener,
    addReplyFormSubmitListener, addEditFormListeners, addDeleteFormSubmitListener} from './main.js';
import {getCommentsCount, reportError} from './utils.js';
import {toggleShowLessButton} from './manage_visible_comments.js';


function addLoadMoreCommentsButtonListener(){
    $('.load-more-comments').on('click', function(event){
        event.preventDefault;
        let lastVisibleCommentId = getLastVisibleCommentId();
        loadMoreComments(lastVisibleCommentId, 10); // load 10 more comments after lastVisibleComment
    })
}

function getLastVisibleCommentId(){
    return ($('.comment').last().attr('id'));
}

// ajax for loading more comments after last visible (bottom) one
function loadMoreComments(lastVisibleCommentId, numOfCommentsToLoad){
    $.ajax({
        url : '/comments/load-more-comments/',
        type : "GET",
        data : { 
            lastVisibleCommentId: lastVisibleCommentId, // used by django to filter comments with ids < lastVisibleCommentId (next ones in db)
            numOfCommentsToLoad: numOfCommentsToLoad, // num of comments to return from database
        }, 
        success : function(loadedComments) {
            addloadedComments(lastVisibleCommentId, loadedComments);
            // Now, after loaded comments are added, last visible comment is last 
            // one of newly added ones, but lastVisibleCommentId is id of
            // previously last visible one, before adding loaded ones, and is
            // used to get comments after it (added ones) for adding listeners to them.
            addListenersToloadedComments(lastVisibleCommentId);
            updateLoadMoreCommentsButton();
            toggleShowLessButton();

        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

// Adds loaded comments after last visible one.
function addloadedComments(lastVisibleCommentId, loadedComments){
    $('#' + lastVisibleCommentId).after(loadedComments);
}

function addListenersToloadedComments(lastVisibleCommentId){
    let ids = getloadedCommentsIds(lastVisibleCommentId);
    ids.forEach(function(commentId){
        addShowRepliesButtonListener(commentId);
        addEditButtonListener(commentId);
        addReplyButtonListener(commentId);
        addReplyFormSubmitListener($('#reply-form-' + commentId));
        addEditFormListeners($('#edit-form-' + commentId));
        addDeleteFormSubmitListener($('#delete-form-' + commentId));
    });
}

// returns a list of ids of newly loaded comments, which come after previously last visible one.  
function getloadedCommentsIds(lastVisibleCommentId){
    let ids = [];
    let loadedComments = getloadedComments(lastVisibleCommentId);
    loadedComments.each(function(){
        ids.push($(this).attr('id'));
    });
    return ids;
}

function getloadedComments(lastVisibleCommentId){
    return $('#' + lastVisibleCommentId).nextAll('.comment'); 
}

function updateLoadMoreCommentsButton(){
    let button = $('.load-more-comments');
    let remainingComments = getCommentsCount() - visibleCommentsCount(); 
    if (remainingComments === 0) {
        button.hide();
    } else if(remainingComments === 1) {
        button.text('Load 1 more Comment');
    } else if(remainingComments < 10) {        
        button.text('Load ' + remainingComments + ' more Comments');
    } else if(remainingComments >= 10) {
        button.text('Load ' + 10 + ' more Comments');
    }  
}

function visibleCommentsCount(){
    return $('.comment').length;
}

export {addLoadMoreCommentsButtonListener,
        getLastVisibleCommentId,
        loadMoreComments,
        updateLoadMoreCommentsButton,
        visibleCommentsCount
    };