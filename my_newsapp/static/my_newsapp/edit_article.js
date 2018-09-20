import './csrf.js'; // Import an entire module for side effects only, without importing anything. This runs the module's global code, but doesn't actually import any values.

$(function(){
    // scrolls to top of the form when page is accessed from article-detail-pages, maintains scroll in case
    // of invalid forms. 
    if ( !(document.referrer.includes('edit-article/')) ) {
        window.scrollTo(0, 250);
    }
    
    $('.file-delete-form').each(function(){
        addFileDeleteFormSubmitListener($(this));
    });

    $('.image-delete-form').each(function(){
        addFileDeleteFormSubmitListener($(this), true);
    });
});

function addFileDeleteFormSubmitListener(formElement, isImage=false ) {
    $(formElement).on('submit', function(event){
        event.preventDefault();
        let url = $(this).attr('action');
        let id = url.split('/')[3];
        deleteFile(url, id, isImage);
    });
}

function deleteFile(url, id, isImage){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
            isImage: isImage
        },
        success : function() {
            $(".modal").modal("hide");
            removeFileListItemFromDOM(id, isImage);
        },
        error : function(xhr,errmsg) { reportError(xhr,errmsg); }
    });
}

function removeFileListItemFromDOM(id, isImage){
    let fileListItem = getFileListItem(id, isImage);
    removeFileListItem(fileListItem);
}

function getFileListItem(id, isImage){
    if(isImage){
        return $('#image-' + id);
    } else return ('#file-' + id);
}

function removeFileListItem(fileListItem){
    let deleted = '<p><strong>Deleted</strong></p>';
    let item = $(fileListItem);
    if(isLastItem(item)){
        removeWithFadeOut();
    } else removeWithSlideUp();
    
    function removeWithSlideUp(){
        item.html(deleted).delay(500).slideUp(300, function(){
            $(this).remove();
            showNoFilesMessageIfNoMoreFiles();
        });
    }

    function removeWithFadeOut(){
        item.html(deleted).delay(500).fadeOut(300,function(){
            $(this).remove();
            showNoFilesMessageIfNoMoreFiles();
        });
    }
}
    
function isLastItem(item){
    return $(item).siblings().length === 0
}

function showNoFilesMessageIfNoMoreFiles(){
    if(noMoreFiles()){
        $('.no-files').show();
    }
    if(noMoreImages()){
        $('.no-images').show();
    }
}

function noMoreFiles(){
    return $('.current-files li').length === 0;
}

function noMoreImages(){
    return $('.current-images li').length === 0;
}

function reportError(xhr,errmsg) {
    $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
        " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
    console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
}