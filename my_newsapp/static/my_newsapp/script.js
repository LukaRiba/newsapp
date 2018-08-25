// removes dropdown-item background color bug when dragging it - STILL WORKS ONLY ON DROPDOWN SUBMENU (listing articles)
$("a.dropdown-item")
    .on('dragend', function(){
        $("ul.navbar-nav li.nav-item.dropdown").removeClass('show');
        $("li.nav-item.dropdown a.nav-link").attr('aria-expanded', "false" );
        $("li.nav-item.dropdown div").removeClass('show');
    }
);

//#region comment
/*
Zadržavanje scroll pozicije prilikom učitavanja stranica :
Storage objects are simple key-value stores, similar to objects, but they stay intact through page loads. 
The keys and the values are always strings (note that integer keys will be automatically converted to strings, 
just like what objects do). You can access these values like an object, or with the Storage.getItem() and Storage.setItem() methods. 
These three lines all set the colorSetting entry in the same way:

    localStorage.colorSetting = '#a4509b';
    localStorage['colorSetting'] = '#a4509b';
    localStorage.setItem('colorSetting', '#a4509b');
    Note: It's recommended to use the Web Storage API (setItem, getItem, removeItem, key, length) to prevent the pitfalls
    associated with using plain objects as key-value stores.

The two mechanisms within Web Storage are as follows:

    sessionStorage: maintains a separate storage area for each given origin that's available for the duration of the page session 
                    (as long as the browser is open, including page reloads and restores).
    localStorage:  does the same thing, but persists even when the browser is closed and reopened.

These mechanisms are available via the Window.sessionStorage and Window.localStorage properties (to be more precise, in supporting 
browsers the Window object implements the WindowLocalStorage and WindowSessionStorage objects, which the localStorage and sessionStorage 
properties hang off) — invoking one of these will create an instance of the Storage object, through which data items can be set, retrieved, 
and removed. A different Storage object is used for the sessionStorage and localStorage for each origin — they function and are controlled 
separately.
So, for example, initially calling localStorage on a document will return a Storage object; calling sessionStorage on a document 
will return a different Storage object. Both of these can be manipulated in the same way, but separately.
*/
//#endregion
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
let scrollToTopLinks = document.querySelectorAll('.scroll-to-top');

scrollToTopLinks.forEach(element => {
    element.addEventListener('click', () => {
        localStorage.setItem('scrollToTop', true);
    })
});
