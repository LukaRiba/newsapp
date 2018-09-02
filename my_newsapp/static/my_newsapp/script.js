// removes dropdown-item background color bug when dragging it - STILL WORKS ONLY ON DROPDOWN SUBMENU (listing articles)
$("a.dropdown-item")
    .on('dragend', function(){
        $("ul.navbar-nav li.nav-item.dropdown").removeClass('show');
        $("li.nav-item.dropdown a.nav-link").attr('aria-expanded', "false" );
        $("li.nav-item.dropdown div").removeClass('show');
    }
);

window.addEventListener('scroll',function() {
    //When scroll changes, it is saved on localStorage.
    localStorage.setItem('scrollPosition',window.scrollY);
},false);

if(isDetailPage()) {
    window.scrollTo(0, 250);
} else scrollToSavedPosition();

function isDetailPage(){
    return document.getElementById('DetailPage');
}

function scrollToSavedPosition(){
    if(localStorage.getItem('scrollPosition') !== null) {
        window.scrollTo(0, localStorage.getItem('scrollPosition'));
    } 
}

//#region comment
/*
Scroll to top when accessing category pages from home page and latest-articles page, through links in
article previews (a elements with "scroll-to-top" class) - if accessing through navigation links, scroll position is mantained
Event listeners are added to these links, and when clicked, in localStorage is stored 'scrollToTop: true' key-value pair.
So, when category page loads, it checks for scrollToTop in localStorage, and if it exists, page is scrolled to top, and
imediatelly after, scrollToTop is removed from localStorage
*/
//#endregion
var scrollToTopLinks = document.querySelectorAll('.scroll-to-top');

scrollToTopLinks.forEach(function(element){
    element.addEventListener('click', function(){
        localStorage.setItem('scrollToTop', true);
    })
});

