import {getCommentsCount} from './utils.js';
import {addLoadMoreCommentsButtonListener,
        updateLoadMoreCommentsButton,
        getLastVisibleCommentId,
        visibleCommentsCount, 
        loadMoreComments} from './load_comments.js';

function manageVisibleComments(){
    let commentsCount = getCommentsCount();
    let visibleComments = visibleCommentsCount();
    let previousBreakPoint = getPreviousBreakpoint(visibleComments);
    let nextBreakPoint = getNextBreakPoint(visibleComments);
    // executes: 1. after creating new comment if conditions are matched, for comment creation increments visibleComments number.
    //              Also adds 'Load more comments button' if visibleComments === commentsCount
    //           2. After deleting comment while there are still more visible comments than breakpoint number. 
    //              Condition visibleComments === commentsCount is never reached in this case.  
    if(visibleComments > previousBreakPoint){
        if(visibleComments === commentsCount){ 
            // If there were less then 6 comments on page load, button element was not rendered in template. So, if comments are 
            // created and their num reach 6 AND if there is no button element already (in case there was, and we delete comments so there is
            // now less then 6 of them, button is hidded, NOT removed. So if we again create comments and reach 6, button will be just shown, not
            // new one added. Without this check, there will be 2 buttons, first showed, and second added and showed) 
            if(commentsCount === 6 && !LoadMoreCommentsButtonExists()){ addLoadMoreCommentsButton(); } 
            else { showLoadMoreCommentsButton(); }     
        }
        removeExtraComments(visibleComments, previousBreakPoint);
        // this function also removes button if there is no more comments to load from database
        updateLoadMoreCommentsButton();
    } 
    // executes: 1. after deleting comment if conditions are matched, for comment deletion decrements visibleComments number
    //           2. after comment creation if there are less than 6 total comments 
    else if(visibleComments < nextBreakPoint){
        if(commentsCount >= 5) // don't load anything if less than 5 comment in db
            loadMoreComments(getLastVisibleCommentId(), 1); // load 1 more comment
        // this function also removes button if there is no more comments to load from database
        updateLoadMoreCommentsButton();
    }
    toggleShowLessButton(); // shows/hides showLessButton if necessary.
}

// Calculates previous breakpoint comments number given visible comments number.
// For exaple, if num of visible comments is 22, it returns 15. If num of visible comments
// is 5 or less, breakpoint is 5 (minimum value)
function getPreviousBreakpoint(visibleCommentsCount){
    let minimumBreakpoint = 5;
    if(visibleCommentsCount > 5){
        while(!(isBreakPoint(visibleCommentsCount))){
            visibleCommentsCount--;
        }
        return visibleCommentsCount;
    }
    return minimumBreakpoint;
}

function getNextBreakPoint(visibleCommentsCount){
    while(!(isBreakPoint(visibleCommentsCount))){
        visibleCommentsCount++;
    }
    return visibleCommentsCount;
}

// returns true if there are 5, 10, 15, 20, 25, ... visible comments 
function isBreakPoint(visibleCommentsCount){
    return (visibleCommentsCount) % 5 === 0;
}

function showLoadMoreCommentsButton(){
    $('.load-more-comments').show();
}

function LoadMoreCommentsButtonExists(){
    return $('.load-more-comments').length > 0;
}

// If there are less than 6 comments for specified owner object, button is not created when page is loaded. 
// So it has to be added dinamically if comment number reaches 6 while creating them dinamically.
function addLoadMoreCommentsButton(){
    let button = '<button class="load-more-comments btn-md btn-primary mr-4">Load 1 more Comment</button>';
    $('#load-more-button-container').prepend(button);
    addLoadMoreCommentsButtonListener();
}

// If num of visible comments is greater than breakpoint number, for example 17, after adding new comment (now 18 visible comments), 
// removes bottom comments until previous breakpoint number (in this case 15) is reached; so 15 now comments are visible, 
// and 'Load 3 more comments' button. Similary, in case of comment deletion, there are 16 visible comments after deletion,
// so last one is removed, resulting with 15 visible comments, and 'Load 1 more comments' button. 
// If ater deleting comment, num of visible comments now equals breakpoint number (for example, visible comments are 11, after deleting
// there are 10, and breakpoint is 10(accquired via getPreviousBreakpoint)), 10 visible comments are maintained.
function removeExtraComments(visibleComments, wantedComments){
    while(visibleComments > wantedComments){  
        $('.comment').last().remove();
        visibleComments--;
    }
}

function toggleShowLessButton(){
    if(visibleCommentsCount() >= 6) { showShowLessButton() } 
    else if(visibleCommentsCount() === 5) { hideShowLessButton() } 
}

function showShowLessButton(){
    $('.show-less-comments').show();
}

function hideShowLessButton(){
    $('.show-less-comments').hide();
}

export {manageVisibleComments, 
        removeExtraComments, 
        toggleShowLessButton, 
        hideShowLessButton, 
        showLoadMoreCommentsButton,
        getPreviousBreakpoint}