import './csrf.js'; // Import an entire module for side effects only, without importing anything. This runs the module's global code, but doesn't actually import any values.
import {createComment} from './create_comment.js';
import createReply from './create_reply.js';
import updateCommentOrReply from './edit.js';
import deleteCommentOrReply from './delete.js';

$(function(){
    
    addCommentFormSubmitListener();

    $('.reply-form').each(function(){
        addReplyFormSubmitListener($(this));
    });

    addListenersToCommentsButtons();

    addListenersToRepliesButtons();

    $('.edit-form').each(function(){
        addEditFormListeners($(this));
    });
    
    $('.delete-form').each(function(){
        addDeleteFormSubmitListener($(this));
    });
});

function addCommentFormSubmitListener(){
    $('#comment-form').on('submit', function(event){
        event.preventDefault();
        let textarea = $(this).find('textarea');
        createComment(textarea);
    });
}

function addReplyFormSubmitListener(form){
    $(form).on('submit', function(event){
        event.preventDefault();
        let parentId = $(this).parent().attr('id') // comment model instance id (owner of replies, their ForeignKey) AND id of DOM comment div element
        let textarea = $(this).find('textarea'); 
        createReply(textarea, parentId);
    });
}

function addListenersToCommentsButtons(){
    $('.comment').each(function(){
        let commentId = $(this).attr('id');
        addShowRepliesButtonListener(commentId);
        addReplyButtonListener(commentId);
        addEditButtonListener(commentId);
        // Delete button works with Bootstrap Modal component
    });
}

function addListenersToRepliesButtons(){
    $('.reply').each(function(){
        let replyId = $(this).attr('id');
        addEditButtonListener(replyId);
        // Delete button works with Bootstrap Modal component
    });
}

function addShowRepliesButtonListener(id){
    getShowRepliesButton(id).click(function(){
        toggleReplies(id);
    });
}

function getShowRepliesButton(id){
    return $('#show-replies-' + id);
}

function toggleReplies(id){
    $('#replies-' + id ).animate({ height: 'toggle', opacity: 'toggle' }, 'fast'); 
    toggleShowRepliesButtonText(id);
}

function toggleShowRepliesButtonText(id){
    let button = getShowRepliesButton(id);
    if (button.text() === 'Show replies'){
        button.text('Hide replies');
    } else button.text('Show replies'); 
}

function addReplyButtonListener(id){
    getReplyButton(id).click(function(){
        toggleReplyForm(id);
    });
}

function getReplyButton(id){
    return $('#reply-button-' + id);
}

function toggleReplyForm(id){
    $('#reply-form-' + id ).animate({ height: 'toggle', opacity: 'toggle' }, 'fast')
}

function addEditButtonListener(id){
    getEditButton(id).click(function(){
        toggleEditForm(id);
    });
}

function getEditButton(id){
    return $('#edit-button-' + id);
}

function toggleEditForm(id){
    let editForm = $('#edit-form-' + id );
    let currentTextElement = editForm.siblings('.text'); // select <p> element which holds comment/reply text
    currentTextElement.animate({ height: 'toggle', opacity: 'toggle' }, 'fast'); // hides/shows comment/reply text
    editForm.animate({ height: 'toggle', opacity: 'toggle' }, 'fast'); // shows/hides edit-form
    setFormTextArealdInitialValue(editForm, currentTextElement.text()) // sets current comment/reply text as edit-form's initial value
}

function setFormTextArealdInitialValue(form, text){
    form.find('textarea').val(text);
}

function addEditFormListeners(form){
    addEditFormSubmitListener(form);
    addEditFormCancelButtonListener($(form).find('.cancel-button'))
}

function addEditFormSubmitListener(form){
    $(form).on('submit', function(event){
        event.preventDefault();
        let url = $(this).attr('action');
        let textarea = $(this).find('textarea'); 
        let id = url.split('/')[2];
        updateCommentOrReply(url, textarea, id);
    });
}

function addEditFormCancelButtonListener(button){
    $(button).click(function(){
        // id of the form which contains the button, returns for example 'edit-form-544'
        let id = $(this).parents('.edit-form').attr('id');
        // splits id to get only number contained in it
        toggleEditForm(id.split('-')[2]);
    }); 
}

function addDeleteFormSubmitListener(form) {
    $(form).on('submit', function(event){
        event.preventDefault();
        let url = $(this).attr('action');
        let id = url.split('/')[2];
        deleteCommentOrReply(url, id);
    });
}

export {
    addShowRepliesButtonListener,
    addEditButtonListener,
    addReplyButtonListener,
    addReplyFormSubmitListener,
    addEditFormListeners,
    addDeleteFormSubmitListener, 
    toggleReplyForm,
    toggleReplies,
    toggleEditForm,
    getShowRepliesButton,
};