$(function(){
    // scrolls to top of the form when page is accessed from article-detail-pages, maintains scroll in case
    // of invalid forms. 
    if ( !(document.referrer.includes('edit-article/')) ) {
        window.scrollTo(0, 250);
    }

    storeOriginalFileNames();

    // cut filenames if owerflow
    handleFileNamesOverflow();

    // cut filenames if owerflow on window resize
    $( window ).resize(function() {
        handleFileNamesOverflow();
      });
});

function storeOriginalFileNames(){
    let originalFileNames = [];
    $('.files-list li, .images-list li').each(function(){
        originalFileNames.push(getFileName($(this)));
    });
    // localStorage only supports strings. Use JSON.stringify() and JSON.parse().
    localStorage.setItem('originalFileNames', JSON.stringify(originalFileNames));
}

function handleFileNamesOverflow(){
    $('.files-list li, .images-list li').each(function(i){
        cutFileNameIfOverflow($(this), JSON.parse(localStorage.getItem('originalFileNames'))[i]);
    });
}

function cutFileNameIfOverflow(fileNameElement, fileName){
    let elementWidth = $(fileNameElement).width();
    let extension = getExtension(fileName);
    let fileNameWithoutExtension = getFileNameWithoutExtension(fileName);
    let characters = fileNameWithoutExtension.split('');
    
    while(getTextWidth(fileName, '400 16px Arial') > elementWidth){
        characters.pop();
        fileName = characters.join('') + '...' + extension;
    }
    $(fileNameElement).text(fileName);
}

function getExtension(fileName){
    let splitList = fileName.split('.');
    return splitList[splitList.length - 1];
}

function getFileName(selector){
    return $(selector).text().trim();
}

function getFileNameWithoutExtension(fileName){
    let splitList = fileName.split('.');
    splitList.pop(); // removes last element (extension)
    return splitList.join('');
}

let getTextWidth = function(text, font) {
    let myCanvas = document.getElementById('canvas');
    let context = myCanvas.getContext('2d');
    context.font = font;
    
    let metrics = context.measureText(text);
    return metrics.width;
 }

