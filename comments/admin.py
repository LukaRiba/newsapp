from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Comment
from my_newsapp.models import Article

class CommentOrReplyFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('comment/reply')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('comments', _('comments')),
            ('replies', _('replies')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'comments':
            return queryset.exclude(content_type=ContentType.objects.get(model__exact='comment'))
        if self.value() == 'replies':
            return queryset.filter(content_type=ContentType.objects.get(model='comment'))

class AuthorFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('author')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'author'
    # queryset returns users who have commented at least once (authors of more than 0 comments)
    authors = User.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)

    def lookups(self, request, model_admin):
        authors_tuples_list = []
        for author in self.authors:
            # append tuple to a list
            authors_tuples_list.append( (author.username, _(author.username)) )
        # we can return list of tuples (not neccessary tuple of tuples, like in above implementation from docs)
        return authors_tuples_list

    def queryset(self, request, queryset):
        for author in self.authors:
            if self.value() == author.username:
                return queryset.filter(author=author.id)

class OwnerArticle(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('owner Article')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'owner'
    # queryset returns articles who are owners of at least 1 comment
    articles = Article.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)

    def lookups(self, request, model_admin):
        articles_tuples_list = []
        for article in self.articles:
            articles_tuples_list.append( (article.title, _(article.title)) )
        return articles_tuples_list

    def queryset(self, request, queryset):
        content_type = ContentType.objects.get(model='article')
        for article in self.articles:
            if self.value() == article.title:
                return queryset.filter(content_type=content_type, object_id=article.id)

class ParentComment(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('parent Comment (for replies)')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parent'
    # queryset returns articles who are owners of at least 1 comment
    parent_comments = Comment.objects.annotate(replies_count=Count('replies')).filter(replies_count__gt=0)

    def lookups(self, request, model_admin):
        parent_tuples_list = []
        for parent in self.parent_comments:
            # append tuple to a list
            parent_tuples_list.append( (parent.text, _(parent.text)) )
        # we can return list of tuples (not neccessary tuple of tuples, like in above implementation from docs)
        return parent_tuples_list

    def queryset(self, request, queryset):
        for parent in self.parent_comments:
            if self.value() == parent.text:
                return queryset.filter(parent=parent.id)
        
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_filter = (CommentOrReplyFilter, AuthorFilter, ParentComment, OwnerArticle,)

    list_display = ('id', 'text', 'author_link', 'owner_object', 'pub_date_reformated')#, 'replies_link') 
    parent_id = None
        
    def author_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:auth_user_change', args=(obj.author.pk,)),
            obj.author
        ))
    author_link.short_description = 'author' 
    # Allows sorting which is disabled on custom list_display fields, fields which are not actual db columns. 
    # Here we tell that pub_date_reformated custom list field use model's pub_date for sorting functionality.
    author_link.admin_order_field = 'author'

    def owner_object(self, obj):
        owner_model = obj.content_object.__class__.__name__.lower()
        owner_app = obj.content_object._meta.app_label
        return mark_safe('<a href="{}">{} - {}</a>'.format(
            reverse(f'admin:{owner_app}_{owner_model}_change', args=(obj.content_object.pk,)),
            owner_model.capitalize(),
            obj.content_object.__str__()          
        ))
    owner_object.short_description = 'owner'
    owner_object.admin_order_field = 'content_type'

    def pub_date_reformated(self, obj):
        return obj.pub_date.strftime('%b %d, %Y')

    pub_date_reformated.short_description = 'published'
    pub_date_reformated.admin_order_field = 'pub_date'