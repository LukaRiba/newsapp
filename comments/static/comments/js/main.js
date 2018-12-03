import './csrf.js'; // Import an entire module for side effects only, without importing anything. This runs the module's global code, but doesn't actually import any values.
import {createComment} from './create_comment.js';
import createReply from './create_reply.js';
import updateCommentOrReply from './edit.js';
import deleteCommentOrReply from './delete.js';
import {addLoadMoreCommentsButtonListener, visibleCommentsCount, updateLoadMoreCommentsButton} from './load_comments.js';
import {getPreviousBreakpoint, removeExtraComments, hideShowLessButton, showLoadMoreCommentsButton} from './manage_visible_comments.js';

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

    addLoadMoreCommentsButtonListener();

    addShowLessCommentsButtonListener();
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
    getShowRepliesButton(id).on('click', function(){
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
    if (button.text() !== 'Hide replies'){
        button.text('Hide replies');
    } else {
        let text = countReplies(id) === 1 ? ' reply' : ' replies';
        button.text('Show ' + countReplies(id) + text); 
    }
}

function countReplies(id){
    return $('#replies-' + id ).children('.reply').length;
}

function addReplyButtonListener(id){
    getReplyButton(id).on('click', function(){
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
    getEditButton(id).on('click', function(){
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
    setFormTextAreaInitialValue(editForm, currentTextElement.text()) // sets current comment/reply text as edit-form's initial value
}

function setFormTextAreaInitialValue(form, text){
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
    $(button).on('click', function(){
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

function addShowLessCommentsButtonListener(){
    $('.show-less-comments').click(function(event){
        event.preventDefault();
        let visibleComments = visibleCommentsCount(); // visible comments before removing
        // visibleComments - 1 instead of visibleComments, forces to remove more comments, till next previousBreakpoint after every click.
        // That's because removeExtraComments() has configured not to remove anything if when called, visible comments equal breakpoint number
        // (only while visible comments num is greater than breakpoint number).
        // Thats because, if for example we have 11 visible comments and delete one, removeExtraComments() is called via manageVisibleComments,
        // and because now visible comments equal breakpoint number (10), 10 comments stay visible. When clicking on this button, if there are for example
        // 18 visible comments, and we pass visibleComments as argument to getPreviousBreakpoint(), getPreviousBreakpoint() will return 15,
        // so 3 comments would be removed. Thats what we want! But, on second click, there are 15 visible comments, and getPreviousBreakpoint()
        // again returns 15, so removeExtraComments does nothing -> thats the reason we pass 'visibleComments - 1' to getPreviousBreakpoint().
        // Now it returns next (lower) previous breakpoint (because visibleComments - 1 is 14, so it calculates previous breakpoint which is 10), 
        // and removeExtraComments() removes 5 more comments.
        removeExtraComments(visibleComments, getPreviousBreakpoint(visibleComments - 1));
        // After removing extra comments, num of visible comments has changed, so we call again visibleCommentsCount().
        if(visibleCommentsCount() < 6) { $(this).hide() }
        showLoadMoreCommentsButton();
        updateLoadMoreCommentsButton();
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

    addLoadMoreCommentsButtonListener,
};