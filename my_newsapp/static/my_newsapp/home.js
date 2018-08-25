// Kod je privremen i brzinski napisan - treba prepraviti i napisati bolje i ljepše funkcije
// za ovo !!!


// *****************************************************************************
// Sakrivanje otherArticles-a koji prelaze veličinu stupca:

let otherArticlesLeftColumn = document.querySelector('#otherArticlesLeftColumn');
let otherArticlesLeft = document.querySelectorAll('#otherArticlesLeftColumn .other-article');

let otherArticlesRightColumn = document.querySelector('#otherArticlesRightColumn');
let otherArticlesRight = document.querySelectorAll('#otherArticlesRightColumn .other-article');

hideOverflowed(otherArticlesLeftColumn, otherArticlesLeft, 30, 1);
hideOverflowed(otherArticlesRightColumn, otherArticlesRight, 30, 1);

// #region Hides child element(s) if owerflowing
    // container = parent element
    // elements = child elements
    // margin = add height to elements totalHeight
    // minElements = minimum number of child elements to be displayed, even if overflowing
    //#endregion
function hideOverflowed(container, elements, margin, minElements){
    let overflowing = elements.length - 1; 
    if (isElement(elements[overflowing])){
        while (totalHeight(elements) + margin > container.offsetHeight && overflowing > minElements) {
            elements[overflowing].style.display = 'none';
            overflowing --;
    }
    return;   
    } 
}

//Checks if object is HTMLElement
function isElement(obj) {
    try {
        //Using W3 DOM2 (works for FF, Opera and Chrome)
        return obj instanceof HTMLElement;
    }
    catch(e){
        //Browsers not supporting W3 DOM2 don't have HTMLElement and
        //an exception is thrown and we end up here. Testing some
        //properties that all elements have (works on IE7)
        return (typeof obj==="object") &&
        (obj.nodeType===1) && (typeof obj.style === "object") &&
        (typeof obj.ownerDocument ==="object");
    }
}

// Calculates total height of elements contained in a list (margins excluded)
function totalHeight(elements){
    let totalHeight = 0;
    for (let i = 0; i < elements.length; i++) {
        totalHeight += elements[i].offsetHeight;
    }
    return totalHeight;
}

//*****************************************************************************
// Cutting article's short descriptions

let articlePreviews = document.querySelectorAll('.article-preview');
let titles = document.querySelectorAll('.title');
let pubDates = document.querySelectorAll('.pub-date');
let shortDescriptions = document.querySelectorAll('.short-description');

for (let i = 0; i < articlePreviews.length; i++) {
    let availableHeight = articlePreviews[i].offsetHeight - (titles[i].offsetHeight + pubDates[i].offsetHeight);
    let computedLineHeight = window.getComputedStyle(shortDescriptions[i]).lineHeight;
    let lineHeight = lineHeightToNumber(computedLineHeight);
    shortDescriptions[i].style.height = String(Math.floor(availableHeight / lineHeight) * lineHeight) + 'px';
}

function lineHeightToNumber(lineHeight){
    return Number(lineHeight.split('px')[0]);
}