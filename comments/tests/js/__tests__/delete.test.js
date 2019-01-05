import {
    deleteCommentOrReply,
    showIsDeletedMessage,
    getTarget,
    isComment,
    removeCommentOrReplyFromDOM,
    isLastReply,
    getParentComment,
    removeShowRepliesButton,
    displayNoRepliesYetMessage,
    decrementCommentsCount,
    displayNoCommentsYetMessage,
    lastCommentDeleted,
    __RewireAPI__ as RewireAPI 
} from '../../../static/comments/js/delete';

import {oneLineTrim} from '../../../../node_modules/common-tags';

describe('deleteCommentOrReply', () => {
    require('jquery-mockjax')($, window);
    $.mockjaxSettings.logging = 1;
    let id = 1;
    let url = `/${id}/delete/`

    afterEach( () => {
        $.mockjax.clear();
    })

    it('calls $.ajax - sends request to /{id}/delete/', () => {
        $.mockjax({
            url: url,
        })

        deleteCommentOrReply(url, id);

        expect($.mockjax.mockedAjaxCalls().length).toEqual(1);
        expect($.mockjax.mockedAjaxCalls()[0]['url']).toEqual(`/${id}/delete/`);
        expect($.mockjax.mockedAjaxCalls()[0]['type']).toEqual('POST');
        expect($.mockjax.mockedAjaxCalls()[0]['data']).toEqual({id: id});
    })

    it('calls listed functions if request was sucessful', done => {
        $.mockjax({
            url: url,
            responseTime: 10,
        })

        for (let func of ['showIsDeletedMessage', 'removeCommentOrReplyFromDOM', 'hideDeleteModal']){
            RewireAPI.__set__(func, jest.fn());
        }

        deleteCommentOrReply(url, id);

        setTimeout(() => {
            expect(RewireAPI.__get__('showIsDeletedMessage')).toBeCalledWith(id);
            expect(RewireAPI.__get__('removeCommentOrReplyFromDOM')).toBeCalledWith(id);
            expect(RewireAPI.__get__('hideDeleteModal')).toBeCalled();
            done();
        },20)
    })
    
    it('calls reportError if request error', (done) => {
        $.mockjax({
            url: url,
            responseTime: 10,
            status: 500
        })

        RewireAPI.__set__('reportError', jest.fn());

        deleteCommentOrReply(url, id);

        setTimeout( () => {
            expect(RewireAPI.__get__('reportError')).toBeCalled();
            done();
        }, 20)
    })

})

describe('showIsDeleteMessage', () => {
    beforeAll( () => {
        document.body.innerHTML =
            `<div id="11" class="comment">
                <p class="text">This is comment</p>
                <p class="author">Author: J. J.</p>
                <p class="pub-date">On 12/12/2000</p>
                <button class="del-button" id="delete-button-11">Delete</button>
            </div>
            <div id="12" class="reply">
                <p class="text">This is reply</p>
                <p class="author">Author: J. J.</p>
                <p class="pub-date">On 12/13/2000</p>
                <button class="del-button" id="delete-button-12">Delete</button>
            </div>`

        showIsDeletedMessage(11);
        showIsDeletedMessage(12);
    })

    it('deletes children elements text content, except of .text element', () => {
        for (let cls of ['author', 'pub-date', 'del-button']){
            expect($('#11').find(cls).text()).toEqual('');
            expect($('#12').find(cls).text()).toEqual('');
        }
            
        expect($('#11').find('.text').text()).not.toEqual('');
        expect($('#12').find('.text').text()).not.toEqual('');
    })

    it('changes comment\'s .text child element html if comment is deleted', () => {
        expect($('#11').find('.text').html()).toEqual(
            '<div><br><p style="color: rgb(124, 0, 0)"><strong>Comment deleted</strong></p></div>'
        );
    })

    it('changes reply\'s .text child element html if reply is deleted', () => {
        expect($('#12').find('.text').html()).toEqual(
            '<div><br><p style="color: rgb(124, 0, 0)"><strong>Reply deleted</strong></p></div>'
        );
    })


})

test('getTarget returns comment/reply element through its delete-button', () => {
    document.body.innerHTML =
        `<div id="11" class="comment">
            <button id="delete-button-11"></button>
            <div id="12" class="reply">
                <button id="delete-button-12"></button>
            </div>
        </div>`

    expect(getTarget(11)).toBeInstanceOf(jQuery);
    expect(getTarget(11).hasClass('comment')).toBe(true);
    expect(getTarget(12)).toBeInstanceOf(jQuery);
    expect(getTarget(12).hasClass('reply')).toBe(true);
})

test('isComment returns true if element has class "comment"', () => {
    // as it gets element through getTarget function, we set up document body like this
    document.body.innerHTML =
        `<div id="11" class="comment">
            <button id="delete-button-11"></button>
            <div id="12" class="reply">
                <button id="delete-button-12"></button>
            </div>
        </div>`

    expect(isComment(11)).toBe(true);
    expect(isComment(12)).toBe(false);
})

describe('removeCommentOrReplyFromDOM', () => {
    beforeAll( () => {
        document.head.innerHTML =
            `<style>
                .comment, .reply {
                    height: 100px;
                }
            </style>`
        // #delete-button-{id} is included for each comment/reply because getTarget function uses it to get
        // target comment/reply.
        document.body.innerHTML = oneLineTrim`
            <div id="comments-count">2</div>
            <div id="comments-counter">2 comments</div>
            <div id="comments">
                <div class="comment" id="2">
                <div class="edit-form"></div>
                    <button class="show-replies"></button>
                    <div id="replies-2">
                        <div class="reply" id="6">
                            <div id="delete-button-6"></div>
                        </div>
                        <div class="reply" id="5">
                            <button id="delete-button-5"></button>
                        </div>
                    </div>
                    <div id="delete-button-2"></div>
                </div>
                <div class="comment" id="1">
                    <div class="edit-form"></div>
                    <button class="show-replies"></button>
                    <div id="replies-1">
                        <div class="reply" id="4">
                            <div id="delete-button-4"></div>
                        </div>
                        <div class="reply" id="3"> 
                            <div id="delete-button-3"></div>
                        </div>
                    </div>
                    <button id="delete-button-1"></button>
                </div>
            </div>`;
    })

    it('fades out target (comment or reply) in 700 ms, and then slides it up in 500 ms', done => {
        const targetOpacity = (id) => {
            return parseFloat($('#' + id).css('opacity'));
        };
        const targetHeight = (id) => {
            return parseFloat($('#' + id).css('height'));
        };

        let id = 3;

        removeCommentOrReplyFromDOM(id);

        expect(targetOpacity(id)).toBeCloseTo(1, 1);
        
        setTimeout( () => {
            expect(targetOpacity(id)).toBeLessThan(0.5);
            expect(targetOpacity(id)).toBeGreaterThan(0.2);
        }, 350)

        setTimeout( () => {
            expect(targetOpacity(id)).toBeLessThan(0.1);
        }, 600)

        setTimeout( () => {
            expect(targetOpacity(id)).toEqual(0);
            expect(targetHeight(id)).toBeGreaterThan(95); // as sometimes slideUp has already started little before 700 ms
        }, 700)

        setTimeout( () => {
            expect(targetHeight(id)).toBeLessThan(60);
            expect(targetHeight(id)).toBeGreaterThan(30);
        }, 950)

        setTimeout( () => {
            expect(targetHeight(id)).toBeLessThan(10);
        }, 1100)

        setTimeout( () => {
            // as after animations end target is removed from DOM, its height is now undefined,
            // so function targetHeight returns NaN as it runs parseFloat over undefined.
            expect(targetHeight(id)).toBe(NaN);
            done();
        }, 1300)
    })

    describe('if target is reply', () => {
        it('only removes the reply if it\'s not the last one', () => {
            // removeCommentOrReplyFromDOM runned in previous test deleted reply with id=3, which was not
            // the last one
            expect($('#3').length).toEqual(0);
        })

        it('removes comment\'s show-replies button and adds \'No replies yet\' message, and then removes reply ' +
           'if it\'s the last one', () => {
            // reply with id=4 is now last reply of comment with id=1, as reply with id=3 was deleted in first test.
            removeCommentOrReplyFromDOM(4);

            $('#4').finish(); // finish all animations immediately
            
            expect($('#replies-1 .reply').length).toEqual(0); // no replies in #replies-1 div
            expect($('#1 button .show-replies').length).toEqual(0); // show.replies button removed
            expect($('#1 .no-replies-message').length).toEqual(1); // 'No replies yet' message added
            expect($('#1').html()).toEqual(oneLineTrim`
                <div class="edit-form"></div>
                <span class="no-replies-message" id="no-replies-message-1">No replies yet</span>
                <div id="replies-1">

                </div>
                <button id="delete-button-1"></button>`
            );
        })
    })

    describe('if target is comment', () => {
        describe('if comment is not the last one', () => {
            beforeAll( () => {
                RewireAPI.__set__('manageVisibleComments', jest.fn());
                removeCommentOrReplyFromDOM(1);
                $('#1').finish(); // finish all animations immediately
            })

            it('decrements comments-count (calls decrementCommentCount)', () => {
                expect($('#comments-count').text()).toEqual('1');
            })

            it('updates #comments-counter (calls updateComentsCounter)', () => {
                expect($('#comments-counter').text()).toEqual('1 comment');
            })

            it('removes target comment', () => {
                expect($('#comments #1').length).toEqual(0); // comment is removed
                expect($('#comments .comment').length).toEqual(1); // 1 comment left
            })

            it('calls manageVisibleComments', () => {
                expect(RewireAPI.__get__('manageVisibleComments')).toHaveBeenCalledTimes(1);
            })
        })

        describe('if comment is the last one, additionally..', () => {
            it('..displays \'No comments yet message\' and removes #comments-counter from DOM', () => {
                removeCommentOrReplyFromDOM(2);
                $('#2').finish();

                expect($('#comments-counter').length).toEqual(0);
                expect($('#no-comments-yet-message').length).toEqual(1);
                expect(document.body.innerHTML).toEqual(oneLineTrim`
                    <div id="comments-count">0</div>
                    <div id="comments">
                        <p id="no-comments-yet-message">No comments yet.</p>
                    </div>`
                )
            })
        })
    })
})

test('isLastReply returns true if passed .reply element is the only one left inside parent comment\'s div', () => {
    document.body.innerHTML =
        `<div id="1" class="comment">
            <div id="replies-1">
                <div id="2" class="reply"></div>
            </div>
        </div>`

    expect(isLastReply($('#2'))).toBe(true);

    // add one more reply
    $('#1 #replies-1').prepend('<div id="3" class="reply"></div>');

    expect(isLastReply($('#2'))).toBe(false);
})

test('getParentComment returns parent comment jq element of jq reply element passed as argument', () => {
    document.body.innerHTML =
        `<div id="3" class="comment">
            <div id="4" class="reply"></div>
        </div>
        <div id="1" class="comment">
            <div id="2" class="reply"></div>
        </div>`

    expect(getParentComment($('#2'))).toBeInstanceOf(jQuery);
    expect(getParentComment($('#2')).attr('id')).toEqual('1');
    expect(getParentComment($('#2')).hasClass('comment')).toBe(true);
})

test('removeShowRepliesButton removes show-replies button of comment passed as argument', () => {
    document.body.innerHTML = 
        `<div id="1" class="comment">
            <button class="show-replies"></button>
        </div>`

    removeShowRepliesButton($('#1'));

    expect($('.show-replies').length).toEqual(0);
})

test('displayNoRepliesYetMessage inserts \'No replies yet\' message after comment\' edit-form', () => {
    document.body.innerHTML = oneLineTrim`
        <div id="1" class="comment">
            <div class="edit-form"></div>
        </div>`;

        displayNoRepliesYetMessage($('#1'));

        expect(document.body.innerHTML).toEqual(oneLineTrim`
            <div id="1" class="comment">
                <div class="edit-form"></div>
                <span class="no-replies-message" id="no-replies-message-1">No replies yet</span>
            </div>`
        );
})

test('decrementCommentsCount decrements number inside #comments-count content by 1', () => {
    document.body.innerHTML = '<div id="comments-count">3</div>';

    decrementCommentsCount();

    expect($('#comments-count').text()).toEqual('2');
})

test('displayNoCommentsYetMessage prepends \'No comments yet\' message inside  #comment element', () => {
    document.body.innerHTML = '<div id="comments"></div>';

    displayNoCommentsYetMessage();

    expect(document.body.innerHTML).toEqual(oneLineTrim`
        <div id="comments">
            <p id="no-comments-yet-message">No comments yet.</p>
        </div>`
    );
})

test('lastCommentDeleted  returns true if there are no .comment elements in the DOM', () => {
    document.body.innerHTML = 
        `<div id="comments">
            <div id="1" class="comment"></div>
        </div>`

    expect(lastCommentDeleted()).toBe(false);

    $('.comment').remove();

    expect(lastCommentDeleted()).toBe(true);
})