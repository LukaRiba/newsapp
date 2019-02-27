from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, IntegerField, ExpressionWrapper
from modeltranslation.admin import TranslationAdmin

from .models import Category, Article, Image, File

# IMPORTANT:
# 1. For modeltranslation integration with admin to work, we must put 'modeltranslation' before 'django.contrib.admin'
#    in settings.INSTALLED_APPS 
# 2. We cannot use @admin.register decorator on ArticleAdmin class when inheriting from TranslationAdmin Both Article
#    and ArticleAdmin have to be registered with admin.site.register(Article, ArticleAdmin) - see below
class ArticleAdmin(TranslationAdmin): # inheriting from Translation Admin for adding translation fields in Article change views
    # Field order in detail (change) view
    fields =  ('author', 'category', 'title', 'short_description', 'text')
    # Fields shown in list view
    list_display = ('id', 'title', 'pub_date_reformated', 'author_link', 'category_link', 'comments_link')

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
    author_link.admin_order_field = 'author'    

    def category_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:my_newsapp_category_change', args=(obj.category.pk,)),
            obj.category          
        ))
    category_link.short_description = 'category' 
    category_link.admin_order_field = 'category'

    def comments_link(self, obj):
        if obj.comments.count() > 0:
            # link to comments list display with filters - owner is obj, type is comments (replies excluded)
            return mark_safe('<a href="{}{}">{}</a>'.format(
                reverse('admin:comments_comment_changelist'),
                '?owner={}&type={}'.format(obj.id, 'comments'),
                '{} Comments'.format(obj.comments.filter(parent=None).count())          
            ))
        return 'no Comments'
    comments_link.short_description = 'comments'
    comments_link.admin_order_field = 'comments_count' 

    def get_queryset(self, request):
        qs = super(ArticleAdmin, self).get_queryset(request)
        #region
        #
        # With annotate we can dynamically create new fields. Here, we use ExpressionWrapper with Count to create new
        # dynamic field, of type IntegerField, named comments_count, so now we can use it for ordering articles
        # according number of comments they own (comments_link.admin_order_field = 'comments_count'). Now our queryset
        # (it is originally Article.object.all() be case we used super()) has new field, dynamically created here, and
        # we can use it in our admin view.
        # We can even create new dynamic fields by calculating something from more existing fields, then we have to use
        # F and ExpressionWrapper. More here:
        #   https://docs.djangoproject.com/en/1.11/ref/models/expressions/#aggregate-expressions
        #   https://docs.djangoproject.com/en/1.11/ref/models/expressions/#using-f-with-annotations
        #
        #endregion
        qs = qs.annotate(
            comments_count=ExpressionWrapper(
                Count('comments'), 
                output_field=IntegerField()
            )
        )
        return qs.order_by('pub_date')

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(File)
