import * as fn from '../utils.js'

test("getCommentsCount returns '#comments-count' element's text as a Number", () => {
    document.body.innerHTML = '<span id="comments-count">12</span>';
    expect(fn.getCommentsCount()).toBe(12);
})

test('getCommentsCounter returns element with id="comments-counter wrapped in jQuery object"', () => {
    document.body.innerHTML = '<p id="comments-counter">5 comments</p>';
    
    expect(fn.getCommentsCounter()).toBeInstanceOf(jQuery);
    expect(fn.getCommentsCounter().attr('id')).toBe('comments-counter');
    expect(fn.getCommentsCounter().text()).toBe('5 comments');
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

        fn.updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>1 comment</strong>')

        // add another one
        $('#1').before('<div id="2" class="comment">second comment</div>');
        $('#comments-count').text('2');
        
        fn.updateCommentsCounter();

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

        fn.updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>2 comments</strong>');

        // remove another one
        $('#2').remove();
        $('#comments-count').text('1');

        fn.updateCommentsCounter();

        expect($('#comments-counter').html()).toEqual('<strong>1 comment</strong>');

    })
})