import {loadMoreComments} from '../../../static/comments/js/load_comments';
import {runMockServer, stopMockServer} from './server_mock/server';
import {forwardPort80To9001, removePortForwarding} from './server_mock/port_forwarding';

describe('loadMoreComments', () => {  
    // prepare response headers
    const headers = [
        'HTTP/1.1 200 OK',
        'Content-Type: text/html; charset=utf-8',
    ].join('\n');

    beforeAll( done => {
        window.comments = { owner_id: 1 }
        runMockServer();
        forwardPort80To9001( () => done())
    })

    afterAll( done => {
        stopMockServer();
        removePortForwarding( () => done()); 
    })

    it(`adds comments recieved in response after last rendered comment; 
        updates .load-more-commetns button when there are more comments to load; 
        shows .show-less-comments button`, done => {
        
        document.body.innerHTML = `
            <p id="comments-count">20</p>
              <div>
              <div class="comment" id="20"></div>        
              <div class="comment" id="19"></div>        
              <div class="comment" id="18"></div>        
              <div class="comment" id="17"></div>        
              <div class="comment" id="16"></div>        
              </div>
            <button class="load-more-comments">Load 10 more comments</button>
            <button class="show-less-comments" style="display: none;">Show less</button>`
        
        // prepare response data (comments)
        const responseData = generateResponseData(16, 10);
        
        writeToMockFile(
            'comments/load-more-comments/',
            'GET',
            headers, 
            responseData,
        );
    
        console.log('BEFORE:\n', document.body.innerHTML);
        loadMoreComments(16, 10);
        setTimeout( () => {
            console.log('RESULT:\n', document.body.innerHTML);
            // check that recieved comments are added to the DOM
            expect(document.body.innerHTML.includes(responseData)).toBe(true);
            // check that .load-more-comments button text has been updated
            expect($('.load-more-comments').text()).toEqual('Load 5 more Comments');
            // check that .show-less-comments button is shown
            expect($('.show-less-comments').css('display')).toEqual('inline-block');
            done();
        }, 500)
    })

    it('hides .load-more-comments button when there is no more comments to load', done => {
        document.body.innerHTML = `
            <p id="comments-count">10</p>
              <div>
              <div class="comment" id="10"></div>        
              <div class="comment" id="9"></div>        
              <div class="comment" id="8"></div>        
              <div class="comment" id="7"></div>        
              <div class="comment" id="6"></div>        
              </div>
            <button class="load-more-comments">Load 5 more comments</button>
            <button class="show-less-comments" style="display: none;">Show less</button>`
            
        const responseData = generateResponseData(6, 5);
        
        writeToMockFile(
            'comments/load-more-comments/',
            'GET',
            headers, 
            responseData
        );
        
        console.log('BEFORE:\n', document.body.innerHTML);
        loadMoreComments(6, 5);
        setTimeout( () => {
            console.log('RESULT:\n', document.body.innerHTML);
            // check that .load-more-comments button text has been hidden
            expect($('.load-more-comments').css('display')).toEqual('none');
            // check once more that recieved comments are added to the DOM
            expect(document.body.innerHTML.includes(responseData)).toBe(true);
            // check .show-less-comments button is shown
            expect($('.show-less-comments').css('display')).toEqual('inline-block');
            done();
        }, 500)
    })
})

//#region
/**
 * range(10) -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
 * range(5, 12) -> [5, 6, 7, 8, 9, 10, 11, 12] 
 * range(5, 1) -> [5, 4, 3, 2, 1]
 */
//#endregion
function range(_from, to) {
    if (to === undefined)
        return Array.from({length: _from}, (_, index) => index + 1);
    if (_from > to) 
        return Array.from({length: -(to - _from - 1) }, (_, index) => -(index - _from)); 
    return Array.from({length: to - _from + 1}, (_, index) => index + _from);
}

//#region 
/**
 * For example, generateResponse(16, 10) returns:
 *      <div class="comment" id="15"></div>
 *      <div class="comment" id="14"></div>
 *      <div class="comment" id="13"></div>
 *      <div class="comment" id="12"></div>
 *      <div class="comment" id="11"></div>
 *      <div class="comment" id="10"></div>
 *      <div class="comment" id="9"></div>
 *      <div class="comment" id="8"></div>
 *      <div class="comment" id="7"></div>
 *      <div class="comment" id="6"></div>
 */
//#endregion
function generateResponseData(lastRenderedCommentId, numOfCommentstoLoad) {
    let response = '\n';
    for ( let i in range(numOfCommentstoLoad) ) {
        response += `<div class="comment" id="${--lastRenderedCommentId}"></div>\n`
    }
    return response;
}

function writeToMockFile(url, httpMethod, headers, data) {
    const fs = require('fs');
    const path = require('path');

    const mockFilePath = path.resolve(
        `./comments/tests/js/__tests__/server_mock/${url}${httpMethod}.mock`
    );
                                  // data to write
    fs.writeFile(mockFilePath, `${headers}\n\n${data}`, function(err) {
        if(err)
            return console.log(err);
    }); 
}