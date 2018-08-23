import {reportError} from './create_comment.js';

function deleteCommentOrReply(){
    $.ajax({
        url : 'comments/delete_comment_or_reply/',
        type : "POST",
        
        success : function() {
            removeComment();
            
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function removeComment() {
    $('#comments').children('.comment').first().remove();
}

export default deleteCommentOrReply;
