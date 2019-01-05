import {manageVisibleComments} from './manage_visible_comments.js';
import {getCommentsCount, updateCommentsCounter, reportError} from './utils.js'

function deleteCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function() {
            showIsDeletedMessage(id);
            removeCommentOrReplyFromDOM(id);
            hideDeleteModal();
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function showIsDeletedMessage(id) {
    let target = $(getTarget(id));
    target.children().text('');
    if(isComment(id))
        // show() because if edit form opened while deleting, .text element would remain hidden
        target.children('.text').show().html(
            '<div><br><p style="color: rgb(124, 0, 0)"><strong>Comment deleted</strong></p></div>');
    else 
        target.children('.text').show().html(
            '<div><br><p style="color: rgb(124, 0, 0)"><strong>Reply deleted</strong></p></div>');
}

function getTarget(id) {
    return $('#delete-button-' + id).parent() //find target comment/reply through delete-button
}

function isComment(id){
    return getTarget(id).hasClass('comment');
}

function removeCommentOrReplyFromDOM(id) {
    $(getTarget(id)).fadeTo(700, 0.00, function(){ 
        $(this).slideUp(500, function() {
            if (isComment(id)){
                decrementCommentsCount();
                updateCommentsCounter();
                // Deletes comment. It's important to call it here because manageVisibleComments(); has to be called after comment removal.
                // This is because then renderedCommentsCount() returns exact num of visible comments remained after deletion.
                $(this).remove(); // comment is removed.
                // Calls loadMoreComments() from 'else if' block (visibleComments < previousBreakPoint) which sends ajax request.
                // Ajax is sent from ajax.
                manageVisibleComments();
                if (lastCommentDeleted()){
                    displayNoCommentsYetMessage();
                    $('#comments-counter').remove();
                }
            } 
            else { // It is reply
                if (isLastReply($(this))){
                    let parentComment = getParentComment($(this));
                    removeShowRepliesButton(parentComment); 
                    displayNoRepliesYetMessage(parentComment); 
                }
                $(this).remove();
            }
        });
    });
}

function isLastReply(reply){
    return getParentComment(reply).find('.reply').length === 1;
}

function getParentComment(reply){
    return $(reply).parents('.comment');
}

function removeShowRepliesButton(comment){
    comment.find('.show-replies').remove();
}

function displayNoRepliesYetMessage(comment){
    let commentId = comment.attr('id');
    let message = '<span class="no-replies-message" id="no-replies-message-' + commentId + '">No replies yet</span>'
    comment.find('.edit-form').after(message);
}

function decrementCommentsCount(){
    $('#comments-count').text(getCommentsCount() - 1);
}

function displayNoCommentsYetMessage(){
    $('#comments').prepend('<p id="no-comments-yet-message">No comments yet.</p>')
}

function lastCommentDeleted(){
    return $('.comment').length === 0;
}

function hideDeleteModal(){
    $(".modal").modal("hide");
}

export {
    deleteCommentOrReply,
    showIsDeletedMessage,
    getTarget,
    removeCommentOrReplyFromDOM,
    isLastReply,
    getParentComment,
    removeShowRepliesButton,
    displayNoRepliesYetMessage,
    isComment,
    decrementCommentsCount,
    displayNoCommentsYetMessage,
    lastCommentDeleted
}