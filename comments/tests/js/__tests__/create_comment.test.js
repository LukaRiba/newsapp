import {
    createComment,
    addComment,
    addEventListenersToComment,
    fadeInComment,
    newCommentId,
    resetCommentForm,
    firstCreated,
    removeNoCommentsMessage,
    incrementCommentsCount,
    addCommentsCounterToDOM,
    __RewireAPI__ as RewireAPI 
} from '../../../static/comments/js/create_comment';

// require('jquery-mockjax')($, window);

//#region
// this import and jest.mock are not necessary because we can mock these functions with RewireAPI. But, I will keep it for
// now for example of use. I've tested addEventListenersToComment in both ways for demonstration
//#endregion
    import * as main from '../../../static/comments/js/main';
    // #region comment
    // As addEventListenersToComment function from create_comment module, whose functions we are testing here,
    // calls these 5 functions from main module,so we mock these main module functions, because here in tests, we just want to 
    // check if addEventListenersToComment calls these functions. addEventListenersToComment is not mocked (no function
    // from create_comment is).
    // #endregion 
    jest.mock('../../../static/comments/js/main', () => ({
        addReplyButtonListener: jest.fn(),
        addEditButtonListener: jest.fn(),
        addEditFormListeners: jest.fn(),
        addReplyFormSubmitListener: jest.fn(),
        addDeleteFormSubmitListener: jest.fn()
    }))

"use strict";

//#region comment
// For some reason, probably because of jQuery fadeIn implementation, jest time mocking (jest.UseFakeTimers, jest.runAllTimers...)
// doesnt work as it shoult - when i call jest.advanceTimersByTime(1000) after calling fadeInComment, and then checkOpacityIsCloseTo,
// test fails because opacity is ~0.01 - time didn't advance in jquery fadeIn function (called inside fadeInComment) for 1000 ms as 
// it should (then opacity will be close to 1 and test will pass). So, here I use setTimeout and call checkOpacityIsCloseTo and
// checkOpacityBetweenOneAndZero  as callbacks.
//#endregion
test.skip('fadeInComment hides first comment, and then fades it in 1000ms', (done) => {
    // Set up our document body
    document.body.innerHTML =
        `<div id="3" class="comment">third comment</div> 
        <div id="2" class="comment">second comment</div> 
        <div id="1" class="comment">first comment</div>`;

    // Run function
    fadeInComment();
    //#region comment
    // IMPORTANT fadeInComment is asynchronous (it has jquery's fadeIn(1000) func inside), but checkOpacityIsCloseTo doesn't
    // wait 1000 ms - it will be called imediately after fadeInComment - meaning element will not be faded in when we check 
    // opacity with expect. So, here we check that element was actually hidden first - we see that in object recieved by except():
    //   Received:
    //   object: {"0": <div class="comment" id="1" style="opacity: 0.012041619030626283; display: block;">first comment</div>, "length": 1} 
    // We see that fadeIn(1000) was called inside fadeInComment as opacity is not 0 and has started raising - after 0.012 seconds, expect
    // inside checkOpacityIsCloseTo(0.01) finished execution, and test passes as we expect opacity to be close to 0.01.
    //#endregion 
    checkOpacityIsCloseTo('#3', 0) // runs before fadeInComment finishes fading
    checkOpacityIsCloseTo('#2', 1) // second comment not affected
    checkOpacityIsCloseTo('#1', 1) // third comment not affected

    //#region comment
    // Now, we run setTimeout passing checkOpacity as callback (bind method is used here to pass arguments to checkOpacity, which we
    // cannot do in normall way for callbacks) and set delay of 500/1000 ms, meaning our expect() func inside checkOpacity will run
    // after that time. So here we check that our comment's opacity is changing over time (it is cca 0.5 after 500ms, and 1 after 1000ms).
    // Important thing when we use asynchronous code, like callbacks we used here with setTimeout, we must pass 'done' argument to test function, 
    // and call done() in the last line of callback definition (checkOpacityIsCloseTo here). Explanation -> https://jestjs.io/docs/en/asynchronous.
    // We do not call also in checkOpacityBetweenOneAndZero, even if it is a callback, as then test will finish here, and line
    // setTimeout(checkOpacityIsCloseTo.bind(this,'#1', 1, true), 1000); will never run. It has to be passed only in callback that is last called 
    // in test. We execute it conditionaly in checkOpacityIsCloseTo, only when checkOpacityIsCloseTo is called as callback, with setting
    // runDune argument to true.
    //#endregion
    setTimeout(checkOpacityBetweenOneAndZero.bind(this,'#3'), 500); // after 500ms opacity should be around 0.5
    setTimeout(checkOpacityIsCloseTo.bind(this,'#3', 1, true), 1000); // after 1000ms, it should be near 1
    
    function checkOpacityBetweenOneAndZero(selector){
        let opacity = getOpacity(selector);
        expect(opacity).toBeGreaterThan(0);
        expect(opacity).toBeLessThan(1);
    }

    function getOpacity(selector){
        return parseFloat($(selector).css('opacity'));
    }

    function checkOpacityIsCloseTo(selector, expectedValue, runDone=false){
        expect(getOpacity(selector)).toBeCloseTo(expectedValue, 1); // 2nd arg is digit precision of expectedValue
        if(runDone){
            done();
        }
    }
})

//#region comment
// this is more simpler implementation using jquery stop() method (done argument has to be removed from test func).
// It stops fadeIn effect - more precisely, fadeIn finishes imediately when arguments are true, true. So is the same as we
// move time forward for 1000ms, when fadeIn is finished. Read: https://api.jquery.com/stop/. Because the time is fast 
// forwarded, like jest.advanceTimersByTime was called, it doesnt have to wait for 1000 ms like above implementation.
// For example, above will run in ~1100ms, and this one in  ~100ms.
//#endregion
test('fadeInComment hides first comment, and then fades it in 1000ms', () => {
    // Set up our document body
    document.body.innerHTML =
        `<div id="3" class="comment">third comment</div> 
        <div id="2" class="comment">second comment</div> 
        <div id="1" class="comment">first comment</div>`;

    fadeInComment(); //run
    expect(getOpacity('#3')).toBeCloseTo(0, 1)
    expect(getOpacity('#2')).toBeCloseTo(1, 1) // second comment not affected
    expect(getOpacity('#1')).toBeCloseTo(1, 1) // third comment not affected
    $('#3').stop(true, true); // jump to end of animation (fadiIn(1000) called in fadeIn)
    expect(getOpacity('#3')).toBeCloseTo(1, 1)

    function getOpacity(selector){
        return parseFloat($(selector).css('opacity'));
    }
})

test('newCommentId returns id attr value of last created comment', () => {
    // Set up our document body
    document.body.innerHTML =
        `<div id="3" class="comment">third created</div>
         <div id="2" class="comment">second created</div>
         <div id="1" class="comment">first created</div>`;
    expect(newCommentId()).toBe('3');
})

test('firstCreated returns true if there is one .comment element', () => {
    document.body.innerHTML = '';
    $('body').prepend('<div id="1" class="comment">first comment</div>'); //add new comment
    
    expect(firstCreated()).toBe(true);

    $('body').prepend('<div id="2" class="comment">second comment</div>'); //add new comment
    
    expect(firstCreated()).toBe(false);
})

test('addCommentsCounterToDOM adds "#comments-counter" element after #title element', () => {
    document.body.innerHTML = '<div id="title"></div>';
    
    addCommentsCounterToDOM();
    
    expect(document.body.innerHTML).toEqual(
        '<div id="title"></div><p id="comments-counter"><strong>1 comment</strong></p>');
})

test('removeNoCommentsMessage removes element with id="no-comments-yet-message"', () => {
    document.body.innerHTML = '<div id="no-comments-yet-message">No comments yet</div>';
    removeNoCommentsMessage();
    expect(document.body.innerHTML).toBe('');
})

test('resetCommentForm clears form textarea', () => {
    document.body.innerHTML = 
        `<form id="comment-form">
            <textarea>some text</textarea>
        </form>`

    let textarea = $('textarea');

    resetCommentForm(textarea);

    expect(textarea.val()).toEqual('');
})

test('incrementCommentsCount increments number in #comments-count element text', () => {
    document.body.innerHTML = '<div id="comments-count">0</div>';
    let count = $('#comments-count');

    incrementCommentsCount();
    expect(count.text()).toEqual('1');

    incrementCommentsCount();
    expect(count.text()).toEqual('2');
})

describe('addEventListenersToComment', () => {
    let id = 1; 

    beforeEach(() => {
        addEventListenersToComment(id);
    })

    test('calls addReplyButtonListener with argument "id"', () => {
        expect(main.addReplyButtonListener).toHaveBeenCalledWith(id);
    })

    test('calls addEditButtonListener with argument "id"', () => {
        expect(main.addEditButtonListener).toHaveBeenCalledWith(id);
    })

    test('calls addEditFormListeners with argument "#edit-form- + id"', () => {
        expect(main.addEditFormListeners).toHaveBeenCalledWith('#edit-form-' + id);
    })

    test('calls addReplyFormSubmitListener with argument "#reply-form- + id"', () => {
        expect(main.addReplyFormSubmitListener).toHaveBeenCalledWith('#reply-form-' + id);
    })

    test('calls addDeleteFormSubmitListener with argument "#delete-form- + id"', () => {
        expect(main.addDeleteFormSubmitListener).toHaveBeenCalledWith('#delete-form-' + id);
    })
})

// Implementation with Rewire. This way we don't need to import and mock functions from main.js module.
test('addEventListenersToComment', () => {
    let id = 1;
    // Test that addEventListenersToComment calls this five functions.
    RewireAPI.__with__({
        addReplyButtonListener: jest.fn(),
        addEditButtonListener: jest.fn(),
        addEditFormListeners: jest.fn(),
        addReplyFormSubmitListener: jest.fn(),
        addDeleteFormSubmitListener: jest.fn()
    })( () => {
        addEventListenersToComment(id);
        expect(RewireAPI.__get__('addReplyButtonListener')).toBeCalledWith(id);
        expect(RewireAPI.__get__('addEditButtonListener')).toBeCalledWith(id);
        expect(RewireAPI.__get__('addEditFormListeners')).toBeCalledWith('#edit-form-' + id);
        expect(RewireAPI.__get__('addReplyFormSubmitListener')).toBeCalledWith('#reply-form-' + id);
        expect(RewireAPI.__get__('addDeleteFormSubmitListener')).toBeCalledWith('#delete-form-' + id);
    })
})

describe('addComment', () => {
    it('prepends created comment (passed as argument) inside #comments div element', () => {
        document.body.innerHTML = '<div id="comments"></div>';

        addComment('<div>This is newly created comment</div>');

        expect(document.body.innerHTML).toEqual(
            '<div id="comments">' +
                '<div>This is newly created comment</div>' +
            '</div>'
        )
    })

    it('calls fadeInComment function', () => {
        // RewireAPI is explained in next test
        RewireAPI.__set__('fadeInComment', jest.fn());
        addComment();
        expect(RewireAPI.__get__('fadeInComment')).toBeCalledTimes(1);
        RewireAPI.__ResetDependency__('fadeInComment');
    })

    it('calls newCommentId functioon', () => {
        // Here, we use rewire to change newCommentId function to be mock function
        RewireAPI.__set__('newCommentId', jest.fn());
        //#region Then, here, when we call addComment, which calls newCommentId internally
        // addComment accepts argument, but it is irrelevant for this test, so we don't pass it.
        // If a function is called with missing arguments (less than declared), the missing values are set to: undefined.
        //#endregion
        addComment(); 
        //#region check that newCommentId was called by addComment.
        // And now here, we CAN check that addComment calls newCommentId.
        // IMPORTANT: We can check if function B has been called, within function A only if function B is mock function, 
        // as toBeCalled and similar matchers work only on mock functions. If we call expect(newCommentId).toBeCalledTimes(1) 
        // after running addComment, without previously set newCommentId  to be mock function, addComment will call actual 
        //newCommentId, and our test will fail: 
        //      jest.fn() value must be a mock function or spy.   // jest.fn() was expected to be passed to expect().
        //      Received:
        //          function: [Function newCommentId]   // this was recieved.
        //#endregion
        expect(RewireAPI.__get__('newCommentId')).toBeCalledTimes(1);
        // reset rewireing, restore original newCommentId implementation.
        RewireAPI.__ResetDependency__('newCommentId'); 

        // implementation using __with__. This way, we don't have to call __RestsDependency__.
        RewireAPI.__with__({
            newCommentId: jest.fn()
        })( () => {
            // within this function newCommentId is mocked
            addComment(); 
            expect(RewireAPI.__get__('newCommentId')).toBeCalledTimes(1);
        })
        // here newCommentId has is original one.
    })

    it('calls addEventListenersToComment', () => {
        //#region 
        // As addEventListenersToComment is passed newCommentId() as argument, here we mock nowCommentId and set
        // its return value to be 111 -> and than we check with expect that it was called with this value.
        //#endregion
        RewireAPI.__with__({
            newCommentId: jest.fn( () => 111), 
            addEventListenersToComment: jest.fn()
        })( () => {
            addComment();
            expect(RewireAPI.__get__('addEventListenersToComment')).toBeCalledTimes(1);
            expect(RewireAPI.__get__('addEventListenersToComment')).toBeCalledWith(111);
        })
    })
})

describe('createComment', () => {
    require('jquery-mockjax')($, window);
    // create textarea jquery object to pass as an argument to createComment
    const textarea = $('<textarea>Text of the Comment</textarea>');
    // display only warning mesages
    $.mockjaxSettings.logging = 1;

    it('calls $.ajax - sends request to /comments/create-comment/', () => {
        // mock $.ajax (if not mocked, it tries to send request to server, 
        // and error is thrown as there is no server listening).
        $.mockjax({
            url: '/comments/create-comment/',
        })
        
        createComment(textarea);

        // $.mockjax.mockedAjaxCalls() returns array of mocked ajax calls. Here, length should be 1
        // as createComment makes 1 call to $.ajax. 
        expect($.mockjax.mockedAjaxCalls().length).toEqual(1);
        // assert that ajax was called with coresponding options.
        expect($.mockjax.mockedAjaxCalls()[0]['url']).toEqual('/comments/create-comment/');
        expect($.mockjax.mockedAjaxCalls()[0]['type']).toEqual('POST');
        expect($.mockjax.mockedAjaxCalls()[0]['data']).toEqual({text: 'Text of the Comment'})

        $.mockjax.clear()        
    })
    
    describe('successful request', () => {
        afterEach( () => {
            $.mockjax.clear();
        })
        // we must use done argument as ajax call is asynchronous
        test("that ajax\'s success callback is called", done => {
            // bool to check of ajax's success callback was called
            let successCalled = false;

            $.mockjax({
                url: '/comments/create-comment/',
                responseTime: 10, // default is 500 ms
                responseText: 'response is successful',
                onAfterSuccess: function(){ // this function run after ajax's success callback
                    successCalled = true;
                }
            })
 
            // call function which calls ajax
            createComment(textarea);

            // as response takes 10 ms to be returned, assert after 20 ms
            setTimeout( () => {
                expect(successCalled).toEqual(true); // of success callback was called, this should pass
                done();
            }, 20); 
        })

        test('which functions success callback calls when first comment created', done => {
            // functions which are called by ajax's success callback
            let functions = ['addComment', 'firstCreated', 'removeNoCommentsMessage', 'addCommentsCounterToDOM',
                'resetCommentForm', 'incrementCommentsCount', 'updateCommentsCounter', 'manageVisibleComments'];
            
            // mock these functions so it can be asserted if they were called. Set firstCreated to return true, 
            // so removeNoCommentsMessage and addCommentsCounterToDOM should be called.
            for (let func of functions) 
                if(func === 'firstCreated')
                    RewireAPI.__set__(func, jest.fn( () => true));
                else 
                    RewireAPI.__set__(func, jest.fn());
            
            let response = '<div class="comment">Text of the Comment</div>';
            $.mockjax({
                url: '/comments/create-comment/',
                responseTime: 10,
                responseText: response
            })

            createComment(textarea);

            // wait for ajax call return response and call callback, then call done()
            setTimeout( () => {
                for (let func of functions)
                    if (func === 'addComment')
                        expect(RewireAPI.__get__(func)).toBeCalledWith(response);
                    else if (func === 'resetCommentForm')
                        expect(RewireAPI.__get__(func)).toBeCalledWith(textarea);
                    else
                        expect(RewireAPI.__get__(func)).toBeCalled();
                done();
            }, 50); 
        })

        test('which functions success callback calls if created comment is not the first one', done => {

            let functions = ['addComment', 'firstCreated', 'removeNoCommentsMessage', 'addCommentsCounterToDOM',
                'resetCommentForm', 'incrementCommentsCount', 'updateCommentsCounter', 'manageVisibleComments'];
            
            // mock functions so it can be asserted if they were called. firstCreated returns undefined (falsy), so
            // removeNoCommentsMessage and addCommentsCounterToDOM should not be called.
            for (let func of functions)
                RewireAPI.__set__(func, jest.fn())
            
            let response = '<div class="comment">Text of the Comment</div>';  
            $.mockjax({
                url: '/comments/create-comment/',
                responseTime: 10,
                responseText: response
            })

            createComment(textarea);

            // wait for ajax call return response and call callback, then call done()
            setTimeout( () => {
                for (let func of functions) 
                    if (func === 'removeNoCommentsMessage' || func === 'addCommentsCounterToDOM')
                        expect(RewireAPI.__get__(func)).not.toBeCalled();
                    else if (func === 'addComment')
                        expect(RewireAPI.__get__(func)).toBeCalledWith(response);
                    else if (func === 'resetCommentForm')
                        expect(RewireAPI.__get__(func)).toBeCalledWith(textarea);
                    else
                        expect(RewireAPI.__get__(func)).toBeCalled();
                done();
            }, 50);   
        })
    })

    describe('request error', () => {
        it('calls $.ajax\'s error callback which calls reportError', done => {
            let errorCalled = false;

            RewireAPI.__set__('reportError', jest.fn());

            $.mockjax({
                url: '/comments/create-comment/',
                responseTime: 10,
                status: 500,
                onAfterError: function(){ // this function run after ajax's error callback
                    errorCalled = true;
                }
            })

            createComment(textarea);

            setTimeout( () => {
                expect(errorCalled).toEqual(true);
                expect(RewireAPI.__get__('reportError')).toBeCalled();
                done();
            }, 20)
        })
    })
})