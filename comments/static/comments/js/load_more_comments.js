import {reportError} from './create_comment.js';
import {addShowRepliesButtonListener, addEditButtonListener, addReplyButtonListener,
        addReplyFormSubmitListener, addEditFormListeners, addDeleteFormSubmitListener} from './main.js';

function loadMoreComments(lastVisibleCommentId){
    $.ajax({
        url : '/comments/load_more_comments/',
        type : "GET",
        data : { 
            lastVisibleCommentId: lastVisibleCommentId,
        }, 
        success : function(nextComments) {
            loadNextComments(lastVisibleCommentId, nextComments);
            addListenersToNextComments(lastVisibleCommentId);
            updateLoadMoreCommentsButtonText();
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function loadNextComments(lastVisibleCommentId, nextComments){
    $('#' + lastVisibleCommentId).after(nextComments);
}

function addListenersToNextComments(lastVisibleCommentId){
    var ids = getNextCommentsIds(lastVisibleCommentId);
    ids.forEach(function(commentId){
        addShowRepliesButtonListener(commentId);
        addEditButtonListener(commentId);
        addReplyButtonListener(commentId);
        addReplyFormSubmitListener($('#reply-form-' + commentId));
        addEditFormListeners($('#edit-form-' + commentId));
        addDeleteFormSubmitListener($('#delete-form-' + commentId));
    });
}

// returns a list of ids of newly loaded comments, which come after last visible one after loading  
function getNextCommentsIds(lastVisibleCommentId){
    var ids = [];
    var nextComments = $('#' + lastVisibleCommentId).nextAll('.comment'); 
    nextComments.each(function(){
        ids.push($(this).attr('id'));
    });
    return ids;
}

function updateLoadMoreCommentsButtonText(){
    var button = $('.load-more-comments');
    var visibleComments = $('.comment').length;
    var remainingComments = commentsCount - visibleComments; 
    if (remainingComments === 0) {
        button.remove();
    } else if(remainingComments === 1) {
        button.text('Load 1 more Comment');
    } else if(remainingComments < 10) {        
        button.text('Load ' + remainingComments + ' more Comments');
    } else if(remainingComments > 10) {
        button.text('Load ' + 10 + ' more Comments');
    }  
}

export {loadMoreComments, updateLoadMoreCommentsButtonText};