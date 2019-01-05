//functions for adding listeners (testing no needed)



//other functions (tested)

function updateCommentsCounter(){
    let commentsCount = getCommentsCount();
    let text;
    commentsCount === 1 ? text = ' comment' : text = ' comments';
    getCommentsCounter().html('<strong>' + commentsCount + text + '</strong>');
}

function getCommentsCount(){
    return Number($('#comments-count').text());
}

function getCommentsCounter(){
    return $('#comments-counter');
}

function reportError(xhr,errmsg) {
    $('#error-log').html('<div class="alert-box alert radius data-alert">Oops! We have encountered an error: ' + errmsg +
        ' <a href="#" class="close">&times;</a></div>'); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}

function getShowRepliesButton(parentId){
    return $('#show-replies-' + parentId);
}

function getLastRenderedCommentId(){
    return ($('.comment').last().attr('id'));
}

function updateLoadMoreCommentsButton(){
    let button = $('.load-more-comments');
    let remainingComments = getCommentsCount() - renderedCommentsCount(); 
    if (remainingComments === 0) {
        button.hide();
    } else if(remainingComments === 1) {
        button.text('Load 1 more Comment');
    } else if(remainingComments < 10) {        
        button.text('Load ' + remainingComments + ' more Comments');
    } else if(remainingComments >= 10) {
        button.text('Load ' + 10 + ' more Comments');
    }  
}

function renderedCommentsCount(){
    return $('.comment').length;
}

export {
    updateCommentsCounter,
    getCommentsCount,
    getCommentsCounter,
    reportError,
    getShowRepliesButton,
    getLastRenderedCommentId,
    updateLoadMoreCommentsButton,
    renderedCommentsCount,
};
