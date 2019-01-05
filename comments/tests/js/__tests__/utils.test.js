import {
    updateCommentsCounter,
    getCommentsCount,
    getCommentsCounter,
    reportError,
    getShowRepliesButton,

    getLastRenderedCommentId,
    updateLoadMoreCommentsButton,
    renderedCommentsCount,
} from '../../../static/comments/js/utils'

test("getCommentsCount returns '#comments-count' element's text as a Number", () => {
    document.body.innerHTML = '<span id="comments-count">12</span>';
    expect(getCommentsCount()).toBe(12);
})

test('getCommentsCounter returns element with id="comments-counter wrapped in jQuery object"', () => {
    document.body.innerHTML = '<p id="comments-counter">5 comments</p>';
    
    expect(getCommentsCounter()).toBeInstanceOf(jQuery);
    expect(getCommentsCounter().attr('id')).toBe('comments-counter');
    expect(getCommentsCounter().text()).toBe('5 comments');
})

describe('updateCommentsCounter tests', () => {
    test('updates #comments-counter html when comment is created', () => {
        document.body.innerHTML =
            '<span id="comments-count">0</span>' +
            '<h4 id="title">Comments</h4>' + 
            // this element is added by create_comment.addCommentsCounterToDOM.
            // Here we put it in manually.
            '<p id="comments-counter"></p>';

        // add new comment and increment #comments-count text - this hapeens
        // by calling incrementCommentsCount in createComment's ajax call success callback, before
        // updateCommentsCounter call. So, here we have increment comments count manually after adding comment.
        $('body').add('<div id="1" class="comment">first comment</div>');
        $('#comments-count').text('1');

        updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>1 comment</strong>')

        // add another one
        $('#1').before('<div id="2" class="comment">second comment</div>');
        $('#comments-count').text('2');
        
        updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>2 comments</strong>')
    })

    test('updates #comments-counter html when comment is deleted', () => {
        document.body.innerHTML = 
            '<span id="comments-count">3</span>' + 
            '<h4 id="title">Comments</h4>' +
            '<p id="comments-counter"><strong>3 comment</strong></p>' + 
            '<div id="3" class="comment">third comment</div>' +
            '<div id="2" class="comment">second comment</div>' +
            '<div id="1" class="comment">first comment</div>';

        // remove comment and decrement #comments-count text - this happens
        // by calling decrementCommentsCount in delete.js.So, here we have 
        // decrement comments count manually after removing comment.
        $('#3').remove();
        $('#comments-count').text('2');

        updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>2 comments</strong>');

        // remove another one
        $('#2').remove();
        $('#comments-count').text('1');

        updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>1 comment</strong>');

    })
})

test('reportError displays error message in the DOM and logs jqXHR status and responseText', () => {
    document.body.innerHTML = '<div id="error-log"></div>';
    // set up jqXHR object
    let jqXHR = $.ajax();
    jqXHR.status = 500;
    jqXHR.responseText = 'Internal server error';
    // set up errmsg 
    let errmsg = 'error';
    
    console.log = jest.fn();

    reportError(jqXHR, errmsg);

    expect(document.body.innerHTML).toEqual(
        "<div id=\"error-log\">" + 
            "<div class=\"alert-box alert radius data-alert\">" + 
                "Oops! We have encountered an error: error <a href=\"#\" class=\"close\">×</a>" + 
            "</div>" + 
        "</div>"
    )
    // The first argument of the first call to the function
    expect(console.log.mock.calls[0][0]).toBe(jqXHR.status + ": " + jqXHR.responseText);
})

test('getShowRepliesButton returns #show-replies-{parentId} element', () => {
    let parentId = 111;
    document.body.innerHTML = '<button id="show-replies-111"></button>';

    let button = getShowRepliesButton(parentId);

    expect(button).toBeInstanceOf(jQuery);
    expect(button.attr('id')).toEqual('show-replies-111');
})

test('getLastRenderedCommentId', () => {
    document.body.innerHTML = `
        <div>
          <div class="comment" id="6"></div>        
          <div class="comment" id="5"></div>        
          <div class="comment" id="4"></div>        
          <div class="comment" id="3"></div>        
          <div class="comment" id="2"></div>        
          <div class="comment" id="1"></div>        
        </div>`
    expect(getLastRenderedCommentId()).toEqual('1');
})

test('renderedCommentsCount', () => {
    document.body.innerHTML = `
            <div class="comment"></div>        
            <div class="comment"></div>        
            <div class="comment"></div>`
            
    expect(renderedCommentsCount()).toEqual(3);
})

describe('updateLoadMoreCommentsButton', () => {
    beforeAll( () => {
        document.body.innerHTML = `
        <p id="comments-count">20</p>
          <div>
            <div class="comment"></div>        
            <div class="comment"></div>        
            <div class="comment"></div>        
            <div class="comment"></div>        
            <div class="comment"></div>        
          </div>
        <button class="load-more-comments"></button>`
    })

    it('displays "Load 10 more Comments" if there is 10 or more remaining comments', () => {
        // state: 20 total - 5 rendered = 15 comments remaining
        updateLoadMoreCommentsButton();
        expect($('.load-more-comments').text()).toEqual('Load 10 more Comments');

        $('#comments-count').text(15);
        // state: 15 total - 5 rendered = 10 comments remaining
        updateLoadMoreCommentsButton();
        expect($('.load-more-comments').text()).toEqual('Load 10 more Comments');

    })

    it('displays "Load (2-9) more comments" if there is 2 to 9 remaining comments', () => {
        for (let totalComments = 14; totalComments >= 7; totalComments--) {
            let remaining = totalComments - 5; // 5 rendered comments
            $('#comments-count').text(totalComments);
            // state: totalComments - 5 rendered = remaining comments
            // 1st iteration: 14 - 5 = 9 remaining
            // 2nd iteration: 13 - 5 = 8 remaining
            // ... last iter:  7 - 5 = 2 remaining
            updateLoadMoreCommentsButton();
            expect($('.load-more-comments').text()).toEqual(`Load ${remaining} more Comments`);
        }
    })

    it('displays "Load 1 more Comment" if there is 1 remaining comment', () => {
        $('#comments-count').text(6);
        // state: 6 total - 5 rendered = 1 comment remaining
        updateLoadMoreCommentsButton();
        expect($('.load-more-comments').text()).toEqual('Load 1 more Comment');
    })
})

