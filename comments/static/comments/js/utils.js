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
    $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}

export {
    updateCommentsCounter,
    getCommentsCount,
    getCommentsCounter,
    reportError
};
