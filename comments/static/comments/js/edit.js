import {reportError} from './create_comment.js';
import {toggleEditForm} from './main.js';

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
    toggleEditForm(id);
    updatedText.hide().fadeIn(2000); // toggleEditForm() hides form and shows text, so it has to be hidden again before fadeIn()
}

function getTarget(id) {
    return $('#edit-button-' + id).parent() //find target comment/reply through delete-button
}

export default editCommentOrReply;