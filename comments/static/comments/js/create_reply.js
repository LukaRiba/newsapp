import {addShowRepliesButtonListener,
       getShowRepliesButton,
       addEditButtonListener,
       addEditFormListeners,
       addDeleteFormSubmitListener} from './main.js';
import {reportError} from './utils.js';

function createReply(textarea, parentId){
    $.ajax({
        url : '/comments/create-reply/',
        type : "POST",
        data : { 
            text: textarea.val(),
            parentId: parentId
        }, 
        success : function(newReply) {
            hideReplyForm(textarea, parentId);
            addReply(newReply, parentId);
            fadeInReply(parentId);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function hideReplyForm(textarea, parentId) {
    textarea.val(''); // remove submitted text from the textarea
    $('#reply-form-' + parentId).hide();
}

function addReply(reply, parentId){
    $('#replies-' + parentId).prepend(reply).show();
    addShowRepliesButtonOrChangeItsText(parentId);
    addEditButtonListener(newReplyId(parentId));
    addEditFormListeners('#edit-form-' + newReplyId(parentId));
    addDeleteFormSubmitListener('#delete-form-' + newReplyId(parentId))
}

function addShowRepliesButtonOrChangeItsText(parentId) {
    if (isFirstReply(parentId)) {
        addShowRepliesButton(parentId); 
    } else getShowRepliesButton(parentId).text('Hide replies'); 
}

function isFirstReply(parentId) {
    return $('#replies-' + parentId + ' > .reply').length === 1;
}

function addShowRepliesButton(parentId) {
    let showRepliesbutton = $('<button class="show-replies" id="show-replies-' + 
        parentId + '">Hide replies</button>')
    $('#no-replies-message-' + parentId).after(showRepliesbutton).remove();
    addShowRepliesButtonListener(parentId); 
}

function newReplyId(parentId) {
    let newReply =  $('#replies-' + parentId).children().first();
    return newReply.attr('id');
}

function fadeInReply(parentId){
    $('#replies-' + parentId + ' .reply').first().hide().fadeIn(1000)
}

export {
    createReply,
    hideReplyForm,
    addReply,
    addShowRepliesButtonOrChangeItsText,
    isFirstReply,
    addShowRepliesButton,
    newReplyId,
    fadeInReply
}