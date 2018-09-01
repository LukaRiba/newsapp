import {reportError} from './create_comment.js';

function editCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            updateCommentOrReply(id, response);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

// function showEditForm(id){

// }  in edit.js


function getTarget(id) {
    return $('#delete-button-' + id).parent() //find target comment/reply through delete-button
}


function getParent(reply){
    return $(reply).parents('.comment');
}






export default deleteCommentOrReply;