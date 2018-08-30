import {reportError} from './create_comment.js';

function deleteCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            showResponseMessage(id, response)
            removeCommentOrReply(id);
            $(".modal").modal("hide");
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function showResponseMessage(id, response) {
    let target = $(getTarget(id));
    target.children().html('');
    target.children('.text').html(response);
}

function getTarget(id) {
    return $('#delete-button-' + id).parent() //find target comment/reply through delete-button
}

function removeCommentOrReply(id) {
    $(getTarget(id)).fadeTo(2000, 0.00, function(){ 
        $(this).slideUp(500, function() { 
            removeShowRepliesButtonIfLastReply($(this));
            $(this).remove();
            displayNoCommentsYetMessageIfLastCommentDeleted();
             
        });
    });
}

function removeShowRepliesButtonIfLastReply(reply){
    if( isLastReply(reply) ){
        let parent = getParent(reply);
        displayNoRepliesYetMessage(parent);
    }
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

function displayNoCommentsYetMessageIfLastCommentDeleted(){
    if( LastCommentDeleted() ){
        $('#comments').prepend('<p id="no-comments-yet-message">No comments yet.</p>')
    }
}

function LastCommentDeleted(){
    return $('.comment').length === 0;
}

export default deleteCommentOrReply;