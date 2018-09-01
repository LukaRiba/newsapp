import {addShowRepliesButtonListener,
       getShowRepliesButton,
       addEditButtonListener,
       addEditFormListeners,
       addDeleteFormSubmitListener} from './main.js';
import {reportError} from './create_comment.js';

// ajax for replies
function createReply(textarea, parentId){
    $.ajax({
        url : '/comments/add_reply/',
        type : "POST",
        data : { 
            text: textarea.val(),
            parentId: parentId
        }, 
        success : function(newReply) {
            hideReplyForm(textarea, parentId);
            addReply(newReply, parentId);
            fadeIn(parentId);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function hideReplyForm(textarea, parentId) {
    textarea.val(''); // remove submitted text from the textarea
    $('#reply-form-' + parentId).hide();
}

// Add new reply to DOM and show replies if hidden
function addReply(reply, parentId){
    $('#replies-' + parentId).prepend(reply).show();
    addShowRepliesButtonOrChangeItsText(parentId);
    addEditButtonListener(newReplyId(parentId));
    console.log(newReplyId(parentId));
    addEditFormListeners('#edit-form-' + newReplyId(parentId));
    addDeleteFormSubmitListener('#delete-form-' + newReplyId(parentId))
}

function addShowRepliesButtonOrChangeItsText(id) {
    if (isFirstReply(id)) {
        addShowRepliesButton(id); 
        addShowRepliesButtonListener(id);
    } else getShowRepliesButton(id).text('Hide replies'); 
}

function isFirstReply(id) {
    return $('#replies-' + id + ' > .reply').length === 1;
}

function addShowRepliesButton(parentId) {
    let showRepliesbutton = $('<button class="show-replies" id="show-replies-' + 
        parentId + '">Hide replies</button>')
    $('#no-replies-message-' + parentId).after(showRepliesbutton).remove() 
}

function newReplyId(parentId) {
    let newReply =  $('#replies-' + parentId).children().first();
    return newReply.attr('id');
}

function fadeIn(parentId){
    $('#replies-' + parentId + ' .reply').first().hide().fadeIn(1000)
}

export default createReply;