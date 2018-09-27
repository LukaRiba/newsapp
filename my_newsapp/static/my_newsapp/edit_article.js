$(function(){
    // scrolls to top of the form when page is accessed from article-detail-pages, maintains scroll in case
    // of invalid forms. 
    if ( !(document.referrer.includes('edit-article/')) ) {
        window.scrollTo(0, 250);
    }

    storeOriginalFileNames();
    
    resizeObserver.observe(document.querySelector('.current-files-and-images'));

    // After checking/unchecking checkboxes or after uploading images, disables/enables submit button
    // if necessary
    $('form').on('change', '.image-input, .image-checkbox', function(){
        preventArticleUpdateIfNoImages();
    });

});

/*---------- Handling filenames overflow ----------*/

const resizeObserver = new ResizeObserver(entries => {
    entries.forEach(entry => {
        entry.target.querySelectorAll('.images-list li, .files-list li').forEach((li, index) => {
            cutFileNameIfOverflow(li, JSON.parse(localStorage.getItem('originalFileNames'))[index]);
        });
    });
});

function storeOriginalFileNames(){
    let originalFileNames = [];
    $('.images-list li, .files-list li').each(function(){
        originalFileNames.push(getFileName($(this)));
    });
    // localStorage only supports strings. Use JSON.stringify() and JSON.parse().
    localStorage.setItem('originalFileNames', JSON.stringify(originalFileNames));
}

function getFileName(selector){
    return $(selector).text().trim();
}

function cutFileNameIfOverflow(fileNameElement, fileName){
    let elementWidth = $(fileNameElement).width();
    let extension = getExtension(fileName);
    let fileNameWithoutExtension = getFileNameWithoutExtension(fileName);
    let fileNameCharacters = fileNameWithoutExtension.split('');

    while(getTextWidth(fileName, '400 16px Arial') > elementWidth){
        fileNameCharacters.pop();
        fileName = fileNameCharacters.join('') + '...' + extension;
    }
    $(fileNameElement).text(fileName);
}

function getExtension(fileName){
    let splited = fileName.split('.');
    return splited[splited.length - 1];
}

function getFileNameWithoutExtension(fileName){
    let splited = fileName.split('.');
    splited.pop(); // removes last element (extension)
    return splited.join('');
}

let getTextWidth = function(text, font) {
    let myCanvas = document.getElementById('canvas');
    let context = myCanvas.getContext('2d');
    context.font = font;
    
    let metrics = context.measureText(text);
    return metrics.width;
 }

 /*---------- Prevent that updated article has no image  ----------*/

 function preventArticleUpdateIfNoImages(){
    let submitButton = $('#submit-button');
    if( allImagesSelectedForDeletion() && !imageChoosenForUpload() ){
        if (submitButton.is(':disabled') === false){
            console.log('disabling button');
            displayWarningMessage();
            submitButton.prop('disabled', true);
        }
    } else {
        if (submitButton.is(':disabled') === true) {
            console.log('enabling button');
            removeWarningMessage();
            submitButton.prop('disabled', false);
        }
    }
}

function allImagesSelectedForDeletion(){
    let imageCheckboxes = document.querySelectorAll('.image-checkbox');
    for (let i = 0; i < imageCheckboxes.length; i++) {
        if (!imageCheckboxes[i].checked) return false;
    }
    console.log('All images selected for deletion');
    return true;
}

function imageChoosenForUpload(){
    let imageInputs = document.querySelectorAll('.image-input');
    for (let i = 0; i < imageInputs.length; i++) {
        if ( !(imageInputs[i].value === '') ) return true;
    }
    console.log('No images choosen for upload');
    return false;
}

function displayWarningMessage(){
    let warningMessage = '<p id="no-image-warning" style="color: brown">Article must have at least one image.</p>'
    $('#submit-button').before(warningMessage);
}

function removeWarningMessage(){
    $('#no-image-warning').remove();
}

export default preventArticleUpdateIfNoImages;



