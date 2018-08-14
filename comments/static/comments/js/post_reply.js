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
        error : function(xhr,errmsg) {
            $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });
}

function hideReplyForm(textarea, parentId) {
    textarea.val(''); // remove submitted text from the textarea
    $('#reply-form-' + parentId).hide();
}

function addReply(reply, parentId){
    $('#replies-' + parentId).prepend(reply); 
}

// Fades in first .reply element (just created) from parent #replies div
function fadeIn(parentId){
    $('#replies-' + parentId + ' .reply').first().hide().fadeIn(1000)
}

export default createReply;