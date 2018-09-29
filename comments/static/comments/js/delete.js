import {countTotalComments, updateCommentsCounter, reportError} from './create_comment.js';
import {manageVisibleComments} from './manage_visible_comments.js';

function deleteCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            showResponseMessage(id, response);
            removeCommentOrReplyFromDOM(id);
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

function removeCommentOrReplyFromDOM(id) {
    $(getTarget(id)).fadeTo(700, 0.00, function(){ 
        $(this).slideUp(500, function() {
            if (isLastReply($(this))){
                let parentComment = getParentComment($(this));
                removeShowRepliesButton(parentComment); 
                displayNoRepliesYetMessage(parentComment); 
            }
            
            if(isComment(id)){
                decrementCommentsCount();
                updateCommentsCounter();
                // Deletes comment. It's important to call it here because manageVisibleComments(); has to be called after comment removal.
                // This is because then visibleCommentsCount() returns exact num of visible comments remained after deletion.
                $(this).remove(); // comment is removed.
                // Calls loadMoreComments() from 'else if' block (visibleComments < previousBreakPoint) which sends ajax request.
                // Ajax is send from ajax.
                manageVisibleComments(); 
            } 
            else $(this).remove(); // It is reply -> reply is removed.
    
            if (lastCommentDeleted()){
                displayNoCommentsYetMessage();
                $('#comments-counter').remove();
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
    comment.find('.text').after(message)
}

function isComment(id){
    return getTarget(id).hasClass('comment');
}

function decrementCommentsCount(){
    $('#comments-count').text(countTotalComments() - 1);
}

function displayNoCommentsYetMessage(){
    $('#comments').prepend('<p id="no-comments-yet-message">No comments yet.</p>')
}

function lastCommentDeleted(){
    return $('.comment').length === 0;
}

export default deleteCommentOrReply;