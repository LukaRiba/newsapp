import {addShowRepliesButtonListener, addEditButtonListener, addReplyButtonListener,
    addReplyFormSubmitListener, addEditFormListeners, addDeleteFormSubmitListener} from './main.js';
import {getLastRenderedCommentId, updateLoadMoreCommentsButton, reportError} from './utils.js';
import {toggleShowLessButton} from './manage_visible_comments.js';

function addLoadMoreCommentsButtonListener(){
    $('.load-more-comments').on('click', function(event){
        event.preventDefault;
        let lastRenderedCommentId = getLastRenderedCommentId();
        loadMoreComments(lastRenderedCommentId, 10); // load 10 more comments after lastVisibleComment
    })
}

// ajax for loading more comments after last visible (bottom) one
function loadMoreComments(lastRenderedCommentId, numOfCommentsToLoad){
    $.ajax({
        url : '/comments/load-more-comments/',
        type : "GET",
        data : { 
            lastRenderedCommentId: lastRenderedCommentId, // used by django to filter comments with ids < lastRenderedCommentId (next ones in db)
            numOfCommentsToLoad: numOfCommentsToLoad, // num of comments to return from database
            owner_id: window.comments.owner_id
        }, 
        success : function(loadedComments) {
            console.log(loadedComments);
            addloadedComments(lastRenderedCommentId, loadedComments);
            //#region
            /**
             * Now, after loaded comments are added, last visible comment is
             * last one of newly added ones, but lastRenderedCommentId is id of
             * previously last visible one, before adding loaded ones, and is
             * used to get comments after it (added ones) for adding listeners
             * to them. addListenersToloadedComments(lastRenderedCommentId);
             */
            //#endregion
            addListenersToloadedComments(lastRenderedCommentId);
            updateLoadMoreCommentsButton();
            toggleShowLessButton();
        },
        error : function(xhr,errmsg) { 
            reportError(xhr,errmsg); }
    });
}

// Adds loaded comments after last visible one.
function addloadedComments(lastRenderedCommentId, loadedComments){
    $('#' + lastRenderedCommentId).after(loadedComments);
}

function addListenersToloadedComments(lastRenderedCommentId){
    let ids = getloadedCommentsIds(lastRenderedCommentId);
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
function getloadedCommentsIds(lastRenderedCommentId){
    let ids = [];
    let loadedComments = getloadedComments(lastRenderedCommentId);
    loadedComments.each(function(){
        ids.push($(this).attr('id'));
    });
    return ids;
}

function getloadedComments(lastRenderedCommentId){
    return $('#' + lastRenderedCommentId).nextAll('.comment'); 
}

export {addLoadMoreCommentsButtonListener, loadMoreComments};