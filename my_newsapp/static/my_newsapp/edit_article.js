$(function(){
    // scrolls to top of the form when page is accessed from article-detail-pages, maintains scroll in case
    // of invalid forms. 
    if ( !(document.referrer.includes('edit-article/')) ) {
        window.scrollTo(0, 250);
    }

    cutFileNameIfOverflow('.files-list', '#file-69');
});

let getTextWidth = function(text, font) {
    let myCanvas = document.getElementById('canvas');
    let context = myCanvas.getContext("2d");
    context.font = font;
    
    let metrics = context.measureText(text);
    return metrics.width;
 }

function cutFileNameIfOverflow(container, fileNameElement){
    let maxWidth = $(container).width();
    let fileName = getFileName(fileNameElement);
    let extension = getExtension(fileName);
    let fileNameWithoutExtension = getFileNameWithoutExtension(fileName);
    let characters = fileNameWithoutExtension.split('');
    
    while(getTextWidth(fileName, '400 16px Arial') > maxWidth){
        characters.pop();
        fileName = characters.join('') + '...' + extension;
        console.log(fileName);
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

