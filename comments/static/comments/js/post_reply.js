import {addShowRepliesButtonListener, getShowRepliesButton} from './main.js';
import {reportError} from './post_comment.js';

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
        error : function() { reportError() }
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
}

// if ($('#no-replies-message-' + id)) always returns True, because it always return object, even if it's empty. But, length
// attribute is 0 for empty $ object, so now it is false if there is no '#no-replies-message-' + id'. Otherwise returns 1 (true).
function addShowRepliesButtonOrChangeItsText(id) {
    if (isFirstReply(id)) {
        addShowRepliesButton(id); 
        addShowRepliesButtonListener(id);
    } else getShowRepliesButton(id).text('Hide replies'  + ' '); 
}

function isFirstReply(id) {
    return $('#replies-' + id + ' > .reply').length === 1;
}

// Line '$('#no-replies-message-...': dodaje showRepliesbutton nakon no-replies-message i zatim briše no-replies-message 
function addShowRepliesButton(parentId) {
    let showRepliesbutton = $('<button class="show-replies" id="show-replies-' + 
        parentId + '" style="white-space:pre">Hide replies </button>')
    $('#no-replies-message-' + parentId).after(showRepliesbutton).remove() 
}

// Fades in first .reply element (just created) from parent #replies div
function fadeIn(parentId){
    $('#replies-' + parentId + ' .reply').first().hide().fadeIn(1000)
}

export default createReply;