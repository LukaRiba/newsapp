import {updateCommentsCounter, reportError} from './create_comment.js';

function deleteCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            showResponseMessage(id, response);
            removeCommentOrReply(id);
            $(".modal").modal("hide");
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function showResponseMessage(id, response) {
    let target = $(getTarget(id));
    target.children().html('');
    // show() because if edit form opened while deleting, .text element, here response, would remain hidden
    target.children('.text').show().html(response);
}

function getTarget(id) {
    return $('#delete-button-' + id).parent() //find target comment/reply through delete-button
}

function removeCommentOrReply(id) {
    $(getTarget(id)).fadeTo(700, 0.00, function(){ 
        $(this).slideUp(500, function() {
            if (isLastReply($(this))){
                removeShowRepliesButton($(this));
            } 
            $(this).remove();
            if (lastCommentDeleted()){
                displayNoCommentsYetMessage();
                $('#comments-counter').remove();
            }
            updateCounter(); 
        });
    });
}

function removeShowRepliesButton(reply){
    let parent = getParent(reply);
    displayNoRepliesYetMessage(parent);
}

function isLastReply(reply){
    return getParent(reply).find('.reply').length === 1;
}

function getParent(reply){
    return $(reply).parents('.comment');
}

function displayNoRepliesYetMessage(comment){
    let commentId = comment.attr('id');
    let message = '<span class="no-replies-message" id="no-replies-message-' + commentId + '">No replies yet</span>'
    comment.find('.show-replies').remove();
    comment.find('.text').after(message)
}

function displayNoCommentsYetMessage(){
    $('#comments').prepend('<p id="no-comments-yet-message">No comments yet.</p>')
}

function lastCommentDeleted(){
    return $('.comment').length === 0;
}

function updateCounter(){
    if(isReply()){
        updateRepliesCounter(id);
    }
    else{
        updateCommentsCounter();
    }
}

function isReply(id){
    return getTarget(id).parents('.comment').length === 1;
}

export default deleteCommentOrReply;