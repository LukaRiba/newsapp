import {
    createReply,
    hideReplyForm,
    addReply,
    addShowRepliesButtonOrChangeItsText,
    isFirstReply,
    addShowRepliesButton,
    newReplyId,
    fadeInReply,
    __RewireAPI__ as RewireAPI
} from '../create_reply'

// use as id of fictive parent comment, as functions use it as argument
const parentId = 111;

describe('createReply', () => {
    require('jquery-mockjax')($, window);
    const textarea = $('<textarea>Text of the Reply</textarea>');
    $.mockjaxSettings.logging = 1;

    afterEach( () => {
        $.mockjax.clear();
    })

    it('calls $.ajax - sends request to /comments/create-reply/', () => {
        $.mockjax({
            url: '/comments/create-reply/'
        })

        createReply(textarea, parentId);

        expect($.mockjax.mockedAjaxCalls().length).toEqual(1);
        expect($.mockjax.mockedAjaxCalls()[0]['url']).toEqual('/comments/create-reply/');
        expect($.mockjax.mockedAjaxCalls()[0]['type']).toEqual('POST');
        expect($.mockjax.mockedAjaxCalls()[0]['data']).toEqual({text: 'Text of the Reply', parentId: 111});
    })

    it('calls listed functions if request was successful', (done) => {
        let response = '<div class="reply">Text of the Reply</div>';
        $.mockjax({
            url: '/comments/create-reply/',
            responseTime: 10,
            responseText: response
        })

        for (let func of ['hideReplyForm', 'addReply', 'fadeInReply']){
            RewireAPI.__set__(func, jest.fn());
        }

        createReply(textarea, parentId);

        setTimeout(() => {
            expect(RewireAPI.__get__('hideReplyForm')).toBeCalledWith(textarea, parentId);
            expect(RewireAPI.__get__('addReply')).toBeCalledWith(response, parentId);
            expect(RewireAPI.__get__('fadeInReply')).toBeCalledWith(parentId);
            done();
        },20)
    })

    it('calls reportError if request error', (done) => {
        $.mockjax({
            url: '/comments/create-reply/',
            responseTime: 10,
            status: 500
        })

        RewireAPI.__set__('reportError', jest.fn());

        createReply(textarea, parentId);

        setTimeout( () => {
            expect(RewireAPI.__get__('reportError')).toBeCalled();
            done();
        }, 20)
    })

})

test('hideReplyForm clears form\'s textarea and hides reply-form', () => {
    document.body.innerHTML = 
        `<div id="reply-form-111"> 
            <textarea>Text of the reply</textarea> 
        </div>`;
        
    let textarea = $('textarea');

    hideReplyForm(textarea, parentId);

    expect($('#reply-form-111').css('display')).toEqual('none');
    expect(textarea.val()).toEqual('');
})

describe('addReply', () => {
    let reply = '<div class="reply">This is reply</div>';

    it('shows #replies-{parentId} element and prepends created reply to it', () => { 
        document.body.innerHTML = '<div id="replies-111" style="display: none;"></div>'

        addReply(reply, parentId);

        expect($('#replies-111').css('display')).toEqual('block'); // shows #replies-111 
        expect($('#replies-111 .reply').first().text()).toEqual('This is reply'); // prepends reply to #replies-111
    })

    it('calls these functions', () => {
        
        RewireAPI.__with__({
            addShowRepliesButtonOrChangeItsText: jest.fn(),
            addEditButtonListener: jest.fn(),
            addEditFormListeners: jest.fn(),
            addDeleteFormSubmitListener: jest.fn()
        })( () => {
            addReply();
            for (let func of [
                'addShowRepliesButtonOrChangeItsText', 
                'addEditButtonListener',
                'addEditFormListeners',
                'addDeleteFormSubmitListener'
            ]){ expect(RewireAPI.__get__(func)).toBeCalledTimes(1); }
        })
    })
})

describe('addShowRepliesButtonOrChangeItsText', () => {
    it('calls addShowRepliesButton if created reply is the first one', () => {
        document.body.innerHTML = '<div id="replies-111"></div>';

        $('#replies-111').prepend('<div class="reply"></div>'); // add first reply
        
        RewireAPI.__with__({
            addShowRepliesButton: jest.fn()
        })( () => {
            addShowRepliesButtonOrChangeItsText(parentId);
            expect(RewireAPI.__get__('addShowRepliesButton')).toBeCalledWith(parentId);
        })
        
    })

    it('changes show-replies button text to \'Hide replies\' if created reply is not the first one', () => {
        document.body.innerHTML = 
            `<button id="show-replies-111">Show 1 reply</button>
             <div id="replies-111"> 
                 <div class="reply"></div> 
             </div>`;
        
        $('#replies-111').prepend('<div class="reply"></div>'); // add second reply

        addShowRepliesButtonOrChangeItsText(parentId);

        expect($('#show-replies-111').text()).toEqual('Hide replies');
    })
})

test('isFirstReply returns true if created reply is the first one', () => {
    document.body.innerHTML = 
        `<div id="replies-111">
            <div class="reply"></div>
        </div>`;

    expect(isFirstReply(parentId)).toEqual(true);

    $('#replies-111').prepend('<div class="reply"></div>')

    expect(isFirstReply(parentId)).toEqual(false);
})

describe('addShowRepliesButton', () => {
    it('adds show-replies button to DOM and removes #no-replies-message', () => {
        document.body.innerHTML = '<div id="no-replies-message-111">No replies yet</div>'

        addShowRepliesButton(parentId);

        expect($('#no-replies-message-111').length).toEqual(0); // message is removed
        expect($('#show-replies-111').length).toEqual(1); // button is added
        expect(document.body.innerHTML).toEqual('<button class="show-replies" id="show-replies-111">Hide replies</button>')
    })

    it('calls addShowRepliesButtonListener', () => {
        RewireAPI.__with__({
            addShowRepliesButtonListener: jest.fn()
        })( () => {
            addShowRepliesButton(parentId);
            expect(RewireAPI.__get__('addShowRepliesButtonListener')).toBeCalledWith(parentId);
        })
    })
})

test('newReplyId returns id of the comment\'s latest reply', () => {
    document.body.innerHTML = 
        `<div id="replies-111"> 
            <div id="114" class="reply"></div> 
            <div id="113" class="reply"></div> 
            <div id="112" class="reply"></div> 
        </div>`;

    expect(newReplyId(parentId)).toEqual('114');
})

test('fadeInReply hides last comment\'s reply and then fades it in 1000ms', () => {
    // Set up our document body
    document.body.innerHTML =
        `<div id="replies-111"> 
            <div id="114" class="reply"></div> 
            <div id="113" class="reply"></div> 
            <div id="112" class="reply"></div> 
         </div>`;

    fadeInReply(parentId); 
    expect(getOpacity('#114')).toBeCloseTo(0, 1) 
    expect(getOpacity('#113')).toBeCloseTo(1, 1) // not affected
    expect(getOpacity('#112')).toBeCloseTo(1, 1) // not affected
    $('#114').stop(true, true); // jump to end of animation (fadiIn(1000) called in fadeIn)
    expect(getOpacity('#114')).toBeCloseTo(1, 1)

    function getOpacity(selector){
        return parseFloat($(selector).css('opacity'));
    }
})