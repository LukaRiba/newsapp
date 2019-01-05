import {loadMoreComments} from '../../../static/comments/js/load_comments';
import {runMockServer, stopMockServer} from './server_mock/server';

//range(10) -> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
//range(5, 12) -> [5, 6, 7, 8, 9, 10, 11, 12]
//range(5, 1) -> [5, 4, 3, 2, 1]
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
    let response = '';
    for ( let i in range(numOfCommentstoLoad) ) {
        response += `<div class="comment" id="${--lastRenderedCommentId}"></div>\n`
    }
    return response;
}

function writeToMockFile(headers, data, httpMethod, url) {
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

describe('loadMoreComments', () => {
    // prepare response headers
    const headers = [
        'HTTP/1.1 200 OK',
        'Content-Type: text/html; charset=utf-8',
    ].join('\n');

    beforeAll( () => {
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
        window.comments = { owner_id: 1 }

        runMockServer();
    })

    afterAll( () => {
        stopMockServer();
    })

    it(`adds comments recieved in response after last rendered comment; 
        updates .load-more-commetns button when there are more comments to load; 
        shows .show-less-comments button`, done => {
        
        // prepare response data (comments)
        const data = generateResponseData(16, 10);
        
        writeToMockFile(
            headers, 
            data,
            'GET',
            'comments/load-more-comments/'
        );

        loadMoreComments(16, 10);

        setTimeout( () => {
            // check that recieved comments are added to the DOM
            for (let id of range(15, 6)) {
                expect(document.body.innerHTML.includes(
                    `<div class="comment" id="${id}"></div>`
                    )).toBe(true);
            }
            // check that .load-more-comments button text has been updated
            expect($('.load-more-comments').text()).toEqual('Load 5 more Comments');
            // check that .show-less-comments button is shown
            expect($('.show-less-comments').css('display')).toEqual('inline-block');
            done();
        }, 500)
    })

    it('hides .load-more-comments button when there is no more comments to load', done => {
        // Now 15 comments are visible, 5 more to load
        const data = generateResponseData(6, 5);
        writeToMockFile(
            headers, 
            data,
            'GET',
            'comments/load-more-comments/'
        );

        loadMoreComments(6, 5);

        setTimeout( () => {
            // check that .load-more-comments button text has been hidden
            expect($('.load-more-comments').css('display')).toEqual('none');
            // check once more that recieved comments are added to the DOM
            for (let id of range(5, 1)) {
                expect(document.body.innerHTML.includes(
                    `<div class="comment" id="${id}"></div>`
                    )).toBe(true);
            }
            done();
        }, 500)
    })
})