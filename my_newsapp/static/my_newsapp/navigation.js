$(function(){
    var resizeCallbackTimeout;

    // style appropriately on page load
    styleDropdownMenu(document.documentElement.clientWidth);

    // listen for resizing, and restyle if window size passes breakpoint.
    // callback executed 250 ms after resizing - on every resize, timeout is set, and then styleDropdownMenu is executed
    // when 250 ms passe. If we resize contuniously, meaning many resize events are happening one after another before 
    // 250 ms passes, with every resize call timeout is reset, so styleDropdownMenu won't execute untill we stop resizing, and
    // let 250 ms pass. This assures that styleDropdownMenu will execute after resizing is finished. Without timeout, it would
    // execute many times while resising, which is unnecessary.
    $(window).resize(function(){
        clearTimeout(resizeCallbackTimeout);
        resizeCallbackTimeout = setTimeout(styleDropdownMenu, 250);
    });

    $('.open-submenu-button').on({
        click: function (event) {
            event.stopPropagation();
            $(this).parent().next('.article-list-submenu').toggleClass('show');
        }
    });

    // hides articles list submenus (if oppened) when clicking on Category dropdown nav-link
    $('#navbarDropdownMenuLink').on('click', function(){
        $('.article-list-submenu').removeClass('show');
    });
});

function styleDropdownMenu(){
    if(isNormalMode()){
        normalNavbarStyle();
    } else collapsedNavbarStyle();
}

function isNormalMode(){
    return document.documentElement.clientWidth >= 991;
}

function normalNavbarStyle(){
    $('.article-list-submenu').removeClass('show'); // if submenus were opened (while expanding wondow from collapsed mode)
    if(hasCollapsedModeClasses()){
        toggleCollapsedModeClasses();
    }
    addNormalModeEventListeners();
}

// it is enough to check just one of four classes
function hasCollapsedModeClasses(){
    return $('.carret').hasClass('carret-down');
}

function toggleCollapsedModeClasses(){
    $('.open-submenu-button').toggleClass('disable-float-right');
    $('.carret').toggleClass('carret-down');
    $('.dropdown-submenu-link').toggleClass('pl-5');
    $('.dropdown-menu').toggleClass('p-0 m-0');
}

function addNormalModeEventListeners(){
    // open/close articles list submenu on moueover/mouseout (hover) on category name (dropdown-menu item)
    $('.dropdown-item').on({
        mouseover: function () {
            $(this).next('.article-list-submenu').addClass('show');
        },
        mouseout: function () {
            $(this).next('.article-list-submenu').removeClass('show');
        }
    });
    // as dropdown-item mouseout hides article-list-submenu, assure it stays open when mouse over it.
    $('.article-list-submenu').on({
        mouseover: function () {
            $(this).addClass('show');
        },
        mouseout: function () {
            $(this).removeClass('show');
        }
    });  
}

function collapsedNavbarStyle(){
    if(!hasCollapsedModeClasses()){
        toggleCollapsedModeClasses();
    }
    if(hasNormalModeEventListeners()){
        removeNormalModeEventListeners();
    }   
}

// it is enough to check just one of four event listeners
function hasNormalModeEventListeners(){
    var dropdownItemListeners = $._data($('.dropdown-item')[0], 'events');
    return dropdownItemListeners != undefined && 'mouseover' in dropdownItemListeners;
}

function removeNormalModeEventListeners(){
    $('.open-submenu-button').off('mouseout');
    $('.article-list-submenu').off('mouseout');
    $('.dropdown-item').off('mouseover');
    $('.dropdown-item').off('mouseout'); 
}