// removes dropdown-item background color bug when dragging it
$("a.dropdown-item")
    .on('dragend', function(){
        $("ul.navbar-nav li.nav-item.dropdown").removeClass('show');
        $("li.nav-item.dropdown a.nav-link").attr('aria-expanded', "false" );
        $("li.nav-item.dropdown div").removeClass('show');
        }
    )