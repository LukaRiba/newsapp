import {reportError} from './create_comment.js';

function editCommentOrReply(url, textarea, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            text: textarea.val(),
            id : id,
        },
        success : function(response) {
            updateCommentOrReply(id, response);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function updateCommentOrReply(id, response){
    let target = getTarget(id);
    let updatedText = target.find('.text').text(response);
    $('#edit-form-' + id).toggle();
    updatedText.fadeIn(2000);
}

function getTarget(id) {
    return $('#edit-button-' + id).parent() //find target comment/reply through edit-button
}

export default editCommentOrReply;
