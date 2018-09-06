import {reportError} from './create_comment.js';
// import {} from './main.js';

function loadMoreComments(lastVisibleCommentId){
    $.ajax({
        url : '/comments/load_more_comments/',
        type : "POST",
        data : { 
            lastVisibleCommentId: lastVisibleCommentId,
        }, 
        success : function(nextComments) {
            console.log('last visible id: ', lastVisibleCommentId);

            showMoreComments(lastVisibleCommentId, nextComments);
            console.log(getNextCommentsIds(lastVisibleCommentId));
            updateLoadMoreCommentsButtonText();
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function showMoreComments(lastVisibleCommentId, nextComments){
    $('#' + lastVisibleCommentId).after(nextComments);
}

function getNextCommentsIds(lastVisibleCommentId){
    var ids = [];
    var nextComments = $('#' + lastVisibleCommentId).nextAll('.comment'); 
    nextComments.each(function(){
        ids.push($(this).attr('id'));
    });
    return ids;
}

function updateLoadMoreCommentsButtonText(){
    var button = $('.load-more-comments');
    var loadedComments = $('.comment').length;
    var remainingComments = commentsCount - loadedComments; 
    if (remainingComments === 0) {
        button.remove();
    } else if(remainingComments === 1) {
        button.text('Load 1 more Comment');
    } else if(remainingComments < 10) {        
        button.text('Load ' + remainingComments + ' more Comments');
    } else if(remainingComments > 10) {
        button.text('Load ' + 10 + ' more Comments');
    }  
}

export {loadMoreComments, updateLoadMoreCommentsButtonText};