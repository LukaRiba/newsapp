// 'let' keyword changed to 'var' for some older browsers don't support 'let'

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
        var textarea = $(this).find('textarea');
        createComment(textarea);
    });
}

function addReplyFormSubmitListener(form){
    $(form).on('submit', function(event){
        event.preventDefault();
        var parentId = $(this).parent().attr('id') // comment model instance id (owner of replies, their ForeignKey) AND id of DOM comment div element
        var textarea = $(this).find('textarea'); 
        createReply(textarea, parentId);
    });
}

function addListenersToCommentsButtons(){
    $('.comment').each(function(){
        var commentId = $(this).attr('id');
        addShowRepliesButtonListener(commentId);
        addReplyButtonListener(commentId);
        addEditButtonListener(commentId);
        // Delete button works with Bootstrap Modal component
    });
}

function addListenersToRepliesButtons(){
    $('.reply').each(function(){
        var replyId = $(this).attr('id');
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
    var button = getShowRepliesButton(id);
    if (button.text() === 'Show replies'){
        button.text('Hide replies'  + ' ');
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
    var form = $('#edit-form-' + id );
    // select <p> element which holds comment/reply text
    var currentTextElement = form.siblings('.text');
    currentTextElement.animate({ height: 'toggle', opacity: 'toggle' }, 'fast');
    form.animate({ height: 'toggle', opacity: 'toggle' }, 'fast');
    form.find('textarea').val(currentTextElement.text());
}

function addEditFormListeners(form){
    addEditFormSubmitListener(form);
    addEditFormCancelButtonListener($(form).find('.cancel-button'))
}

function addEditFormSubmitListener(form){
    $(form).on('submit', function(event){
        event.preventDefault();
        var url = $(this).attr('action');
        var textarea = $(this).find('textarea'); 
        var id = url.split('/')[2];
        updateCommentOrReply(url, textarea, id);
    });
}

function addEditFormCancelButtonListener(button){
    $(button).click(function(){
        // id of the form which contains the button, returns for example 'edit-form-544'
        var id = $(this).parents('.edit-form').attr('id');
        // splits id to get only number contained in it
        toggleEditForm(id.split('-')[2]);
    }); 
}

function addDeleteFormSubmitListener(form) {
    $(form).on('submit', function(event){
        event.preventDefault();
        var url = $(this).attr('action');
        var id = url.split('/')[2];
        deleteCommentOrReply(url, id);
    });
}

function createComment(textarea){
    $.ajax({
        url : '/comments/add_comment/',
        type : "POST",
        data : { 
            text: textarea.val()
        }, 
        success : function(newComment) {
            addComment(newComment);
            resetCommentForm(textarea);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function addComment(comment){
    $('#comments').prepend(comment);
    fadeIn(); 
    addReplyButtonListener(newCommentId());
    addEditButtonListener(newCommentId());
    addEditFormListeners('#edit-form-' + newCommentId());
    addReplyFormSubmitListener('#reply-form-' + newCommentId());
    addDeleteFormSubmitListener('#delete-form-' + newCommentId());
}

function fadeIn(){
    $('.comment').first().hide().fadeIn(1000)
}

function newCommentId() {
    var newComment =  $('.comment').first();
    return newComment.attr('id');
}

function resetCommentForm(textarea) {
    textarea.val(''); // remove the value from the input
    if (isFirstComment()) removeNoCommentsMessage();
}

function isFirstComment() {
    return $('.comment').length === 1;
}

function removeNoCommentsMessage() {
    $('#no-comments-yet-message').remove();
}

function reportError(xhr,errmsg) {
    $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}

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
    var showRepliesbutton = $('<button class="show-replies" id="show-replies-' + 
        parentId + '">Hide replies</button>')
    $('#no-replies-message-' + parentId).after(showRepliesbutton).remove() 
}

function newReplyId(parentId) {
    var newReply =  $('#replies-' + parentId).children().first();
    return newReply.attr('id');
}

function fadeIn(parentId){
    $('#replies-' + parentId + ' .reply').first().hide().fadeIn(1000)
}

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
    var target = getTarget(id);
    var updatedText = target.find('.text').text(response);
    $('#edit-form-' + id).toggle();
    updatedText.fadeIn(2000);
}

function getTarget(id) {
    return $('#edit-button-' + id).parent() //find target comment/reply through delete-button
}

function deleteCommentOrReply(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            showResponseMessage(id, response)
            removeCommentOrReply(id);
            $(".modal").modal("hide");
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function showResponseMessage(id, response) {
    var target = $(getTarget(id));
    target.children().html('');
    // show() because if edit form opened while deleting, .text element, here response, would remain hidden
    target.children('.text').show().html(response);
}

function getTarget(id) {
    return $('#delete-button-' + id).parent() //find target comment/reply through delete-button
}

function removeCommentOrReply(id) {
    $(getTarget(id)).fadeTo(2000, 0.00, function(){ 
        $(this).slideUp(500, function() { 
            removeShowRepliesButtonIfLastReply($(this));
            $(this).remove();
            displayNoCommentsYetMessageIfLastCommentDeleted(); 
        });
    });
}

function removeShowRepliesButtonIfLastReply(reply){
    if( isLastReply(reply) ){
        var parent = getParent(reply);
        displayNoRepliesYetMessage(parent);
    }
}

function isLastReply(reply){
    return getParent(reply).find('.reply').length === 1;
}

function getParent(reply){
    return $(reply).parents('.comment');
}

function displayNoRepliesYetMessage(comment){
    var commentId = comment.attr('id');
    var message = '<span class="no-replies-message" id="no-replies-message-' + commentId + '">No replies yet</span>'
    comment.find('.show-replies').remove();
    comment.find('.text').after(message)
}

function displayNoCommentsYetMessageIfLastCommentDeleted(){
    if( LastCommentDeleted() ){
        $('#comments').prepend('<p id="no-comments-yet-message">No comments yet.</p>')
    }
}

function LastCommentDeleted(){
    return $('.comment').length === 0;
}

// from https://realpython.com/django-and-ajax-form-submissions/
// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

