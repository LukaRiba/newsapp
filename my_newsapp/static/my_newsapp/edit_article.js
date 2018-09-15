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
});

function addFileDeleteFormSubmitListener(form) {
    $(form).on('submit', function(event){
        event.preventDefault();
        let url = $(this).attr('action');
        let id = url.split('/')[3];
        deleteFile(url, id);
    });
}

function deleteFile(url, id){
    $.ajax({
        url : url,
        type : "POST",
        data : {
            id : id,
        },
        success : function(response) {
            $(".modal").modal("hide");
            removeFileListItemFromDOM(id, response);
        },
        error : function(xhr,errmsg) { console.log('ERROR'); }//reportError(xhr,errmsg); }
    });
}

function removeFileListItemFromDOM(id, response){
    let fileListItem = $('#file-' + id);
    fileListItem.text(response).fadeOut(500).remove();
}

// function addImageDeleteFormSubmitListener(form) {
//     $(form).on('submit', function(event){
//         event.preventDefault();
//         let url = $(this).attr('action');
//         let id = url.split('/')[2];
//         let isImage = true;
//         deleteCommentOrReply(url, id, isImage);
//     });
// }