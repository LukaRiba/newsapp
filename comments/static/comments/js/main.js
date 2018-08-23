import './csrf.js'; // Import an entire module for side effects only, without importing anything. This runs the module's global code, but doesn't actually import any values.
import {createComment} from './create_comment.js';
import createReply from './create_reply.js';
import deleteCommentOrReply from './delete.js';

$(function() {
    addCommentFormSubmitListener();

    $('.reply-form').each(function(){
        addReplyFormSubmitListener($(this));
    });

    addCommentButtonListeners();

    $('.delete-form').each(function(){
        addDeleteFormSubmitListener($(this));
    });
});

function addCommentFormSubmitListener() {
    $('#comment-form').on('submit', function(event){
        event.preventDefault();
        let textarea = $(this).find('textarea');
        createComment(textarea);
    });
}

function addReplyFormSubmitListener(form) {
    $(form).on('submit', function(event){
        event.preventDefault();
        let parentId = $(this).parent().attr('id') // comment model instance id (owner of replies, their ForeignKey) AND id of DOM comment div element
        let textarea = $(this).find('textarea'); 
        createReply(textarea, parentId);
    });
}

function addCommentButtonListeners() {
    $('.comment').each(function(){
        let commentId = $(this).attr('id');
        addShowRepliesButtonListener(commentId);
        addReplyButtonListener(commentId);
    });
}

function addShowRepliesButtonListener(id) {
    getShowRepliesButton(id).click(function() {
        toggleReplies(id);
    });
}

function getShowRepliesButton(id) {
    return $('#show-replies-' + id);
}

function toggleReplies(id){
    $('#replies-' + id ).animate({ height: 'toggle', opacity: 'toggle' }, 'fast'); 
    toggleShowRepliesButtonText(id);
}

function toggleShowRepliesButtonText(id) {
    let button = getShowRepliesButton(id);
    if (button.text() === 'Show replies') {
        button.text('Hide replies'  + ' ');
    } else button.text('Show replies'); 
}

function addReplyButtonListener(id) {
    getReplyButton(id).click(function() {
        toggleReplyForm(id);
    });
}

function getReplyButton(id) {
    return $('#reply-button-' + id);
}

function toggleReplyForm(id){
    $('#reply-form-' + id ).animate({ height: 'toggle', opacity: 'toggle' }, 'fast')
}

function addDeleteFormSubmitListener(form) {
    $(form).on('submit', function(event){
        event.preventDefault();
        deleteCommentOrReply();
    });
}

export {
    addReplyFormSubmitListener, 
    toggleReplyForm,
    toggleReplies,
    addShowRepliesButtonListener,
    addReplyButtonListener,
    getShowRepliesButton
};



