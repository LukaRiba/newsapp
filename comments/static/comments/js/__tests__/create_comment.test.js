import * as fn from '../create_comment.js'

"use strict";

//#region comment
// For some reason, probably because of jQuery fadeIn implementation, jest time mocking (jest.UseFakeTimers, jest.runAllTimers...)
// doesnt work as it shoult - when i call jest.advanceTimersByTime(1000) after calling fn.fadeIn, and then checkOpacityIsCloseTo,
// test fails because opacity is ~0.01 - time didn't advance in jquery fadeIn function (called inside fn.fadeIn) for 1000 ms as 
// it should (then opacity will be close to 1 and test will pass). So, here I use setTimeout and call checkOpacityIsCloseTo and
// checkOpacityBetweenOneAndZero  as callbacks.
//#endregion
xtest('fadeIn hides first comment, and then fades it in 1000ms', (done) => {
    // Set up our document body
    document.body.innerHTML =
        '<div id="1" class="comment">first comment</div>' +
        '<div id="2" class="comment">second comment</div>' +
        '<div id="3" class="comment">third comment</div>';

    // Run function
    fn.fadeIn();
    //#region comment
    // IMPORTANT fn.fadeIn is asynchronous (it has jquery's fadeIn(1000) func inside), but checkOpacityIsCloseTo doesn't
    // wait 1000 ms - it will be called imediately after fn.fadeIn - meaning element will not be faded in when we check 
    // opacity with expect. So, here we check that element was actually hidden first - we see that in object recieved by except():
    //   Received:
    //   object: {"0": <div class="comment" id="1" style="opacity: 0.012041619030626283; display: block;">first comment</div>, "length": 1} 
    // We see that fadeIn(1000) was called inside fn.fadeIn as opacity is not 0 and has started raising - after 0.012 seconds, expect
    // inside checkOpacityIsCloseTo(0.01) finished execution, and test passes as we expect opacity to be close to 0.01.
    //#endregion 
    checkOpacityIsCloseTo('#1', 0) // runs before fn.fadeIn finishes fading
    checkOpacityIsCloseTo('#2', 1) // second comment not affected
    checkOpacityIsCloseTo('#3', 1) // third comment not affected

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
    setTimeout(checkOpacityBetweenOneAndZero.bind(this,'#1'), 500); // after 500ms opacity should be around 0.5
    setTimeout(checkOpacityIsCloseTo.bind(this,'#1', 1, true), 1000); // after 1000ms, it should be near 1
    
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
});

//#region comment
// this is more simpler implementation using jquery stop() method (done argument has to be removed from test func).
// It stops fadeIn effect - more precisely, fadeIn finishes imediately when arguments are true, true. So is the same as we
// move time forward for 1000ms, when fadeIn is finished. Read: https://api.jquery.com/stop/. Because the time is fast 
// forwarded, like jest.advanceTimersByTime was called, it doesnt have to wait for 1000 ms like above implementation.
// For example, above will run in ~1100ms, and this one in  ~100ms.
//#endregion
test('fadeIn hides first comment, and then fades it in 1000ms', () => {
    // Set up our document body
    document.body.innerHTML =
        '<div id="1" class="comment">first comment</div>' +
        '<div id="2" class="comment">second comment</div>' +
        '<div id="3" class="comment">third comment</div>';

    fn.fadeIn(); //run
    expect(getOpacity('#1')).toBeCloseTo(0, 1)
    expect(getOpacity('#2')).toBeCloseTo(1, 1) // second comment not affected
    expect(getOpacity('#3')).toBeCloseTo(1, 1) // third comment not affected
    $('#1').stop(true, true); // jump to end of animation (fadiIn(1000) called in fn.fadeIn)
    expect(getOpacity('#1')).toBeCloseTo(1, 1)

    function getOpacity(selector){
        return parseFloat($(selector).css('opacity'));
    }
});

test('newCommentId returns id attr value of first comment', () => {
    // Set up our document body
    document.body.innerHTML =
        '<div id="1" class="comment">first comment</div>' +
        '<div id="2" class="comment">second comment</div>' +
        '<div id="3" class="comment">third comment</div>';

    expect(fn.newCommentId()).toBe('1');
});
