$(function() {

    
    $('#comment-form').on('submit', function(){
        event.preventDefault();
        let textarea = $(this).find('textarea');
        createComment(textarea);
    });

    // AJAX for comment
    function createComment(textarea){
        $.ajax({
            url : URL, // the endpoint - URL variable is defined in main html (inside script tag), in this case detail.html
            type : "POST", // http method
            data : { 
                text: textarea.val()
            }, // data sent with the post request

            // handle a successful response
            success : function(json) {
                textarea.val(''); // remove the value from the input
                console.log(json); // log the returned json to the console
                showComment(json);
            },

            // handle a non-successful response
            error : function(xhr,errmsg) {
                $('##error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    }

    $('.reply-button').each(function(i){
        $(this).on('click', function(){
            $('#reply-form-' + (i+1)).toggle(); // i+1 because i starts with 0, but first id is reply-form-1. 
        });
    })
 
    $('.reply-form').each(function(){
        let parentId = $(this).parent().children().first().text() // comment model instance id (owner of replies, their ForeignKey)
        let parentDOMId = $(this).parent().attr('id').split('-').pop() // id of div element with class .comment (reply-form and replies are his DOM children)
        $(this).on('submit', function(event){
            event.preventDefault();
            let textarea = $(this).find('textarea'); // text of the reply
            createReply(parentId, parentDOMId, textarea);
        });
    });

    // AJAX for reply
    function createReply(parentId, parentDOMId, textarea){
        console.log("create reply is working!") // sanity check
        $.ajax({
            url : URL, // the endpoint - URL variable is defined in main html (inside script tag), in this case detail.html
            type : "POST", // http method
            data : { 
                parent_id: parentId, 
                text: textarea.val()
            }, // data sent with the post request

            // handle a successful response
            success : function(json) {
                textarea.val(''); // remove the value from the input
                console.log(json); // log the returned json to the console
                showReply(json, parentDOMId);
            },

            // handle a non-successful response - dodati u comments.html div sa #error-log
            error : function(xhr,errmsg) {
                $('#error-log').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        })
    };

    // adds new reply to the top of .replies div.
    function showReply(json, parentDOMId){
        let author = '<p class="margin-bottom-0"><strong>' + json.author + '</strong></p>';
        let pubDate = '<p class="pub-date margin-bottom-5">' + json.pub_date + '</p>';
        let text = ' <p class="margin-bottom-20">' + json.text + '</p>';
        let newReply = '<div id="' + json.reply_id + '" class="reply">' + author + pubDate + text + '</div>';
        $('#replies-' + parentDOMId).prepend(newReply); // Add new reply div to the DOM
        $('#' + json.reply_id).hide().fadeIn(1000); // Select added reply through id, then hide it and immediately fadeIn - for FadeIn effect
    }

    // This function gets cookie with a given name
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    let csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        let host = document.location.host; // host + port
        let protocol = document.location.protocol;
        let sr_origin = '//' + host;
        let origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});