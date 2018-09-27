import preventArticleUpdateIfNoImages from './edit_article.js';

$(function() {
    // ImageFormset settings
    $('.image-form').formset({
        prefix: 'images',
        formCssClass: 'image-form', // important becaouse of two formsets, must be different for each
        addText: 'Add image',
        deleteText: 'Remove',
        // Image-form with uploaded image can be removed. So, it is important to check here too 
        removed: preventArticleUpdateIfNoImages
    });

    // FileFormset settings
    $('.file-form').formset({
        prefix: 'files',
        formCssClass: 'file-form',
        addText: 'Add file',
        deleteText: 'Remove'
    });

    displayFileName('.image-formset', 'image', ['bmp', 'gif', 'png', 'jpg', 'jpeg']);
    displayFileName('.file-formset', 'file', ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip']);
});

// for displaying names of choosen images and files
function displayFileName(selector, type, allowedExtensions){
    $(selector).on('change', 'input[type="file"]', function(e){
        var fileName = e.target.value.split( '\\' ).pop(); // gets filename from the path
        var fileExtension = fileName.split('.').pop() // gets file extension
        $(this).next('div').children('span').html(fileName) //Selects span next to Choose image label and sets fileName as text (html)
        
        // Check if not allowed files choosen
        if ( !(allowedExtensions.indexOf(fileExtension) > -1) ){
        // display warning message
        $(selector).children('.errors').prepend(
            '<ul><li style="color: brown">Files with extension .' + fileExtension + ' are not allowed</li></ul>'); 
        // clear file input
        $(this).val('');
        // remove file name
        $(this).next('div').children('span').html('No ' + type + ' choosen');
        }
        else{
            if( $(selector).find('.errors ul').length > 0 )
                $(selector).find('.errors ul').remove();
        }    
    });  
}