from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from .models import Category, Article, Image, File

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Field order in detail (change) view
    fields =  ('author', 'category', 'title', 'short_description', 'text')
    # Fields shown in list view
    list_display = ('id', 'title', 'pub_date_reformated', 'author_link', 'category_link') #, 'comments_link')

    def pub_date_reformated(self, obj):
        return obj.pub_date.strftime('%b %d, %Y')
    pub_date_reformated.short_description = 'published'
    pub_date_reformated.admin_order_field = 'pub_date'

    def author_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:auth_user_change', args=(obj.author.pk,)),
            obj.author
        ))
    #region    
     # without this in admin list view will be AUTHOR_LINK instead AUTHOR, because we passed method author_link in
     # list_diplay. With this column name is set to AUTHOR. MUST be set above method definition, or
     # "NameError: name 'author_link' is not defined" will be raised.
    author_link.short_description = 'author' 

    def category_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:my_newsapp_category_change', args=(obj.category.pk,)),
            obj.category          
        ))
    category_link.short_description = 'category' 

    def comments_link(self, obj):
        pass
    
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(File)
