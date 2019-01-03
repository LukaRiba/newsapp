from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Count, IntegerField, ExpressionWrapper

from .models import Comment
from my_newsapp.models import Article

# region
# Helper function for setting lookups in a generic way - Because same pattern was used between SimpleListFilter
# classes. We define queryset in a class, for example all users that have commented (comment authors), and then
# obj_attr which represents field of user we want to expose filter side bar. We pass obj_attr as a string, since we
# have to use obj.__dict__['attr'] to access object attribute as we cannot use dot notation. In URL query, id of the
# object is exposed.
# Without this fuction, lookup method of AuthorFilter class will be implemented like this:
#
#        authors = User.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)
#
#        def lookups(self, request, model_admin):
#           authors_tuples_list = []
#               for author in self.authors:
#                   authors_tuples_list.append( (author.id, _(author.username)) )
#               return authors_tuples_list 
#
# Now, using this helper, code can be shortened like this:
#
#        authors = User.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)
#        
#        def lookups(self, request, model_admin):
#            return set_lookups(self.authors, 'username')
#
# endregion
def set_lookups(queryset, obj_attr):
    tuples_list = []
    for obj in queryset:
        # append pair tuple to a list
        tuples_list.append( (obj.id, _(obj.__dict__[obj_attr])) ) 
    # we can return list of tuples (not neccessary tuple of tuples, like in above implementation from docs)
    return tuples_list

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
            return queryset.filter(parent__isnull=True)
        if self.value() == 'replies':
            return queryset.exclude(parent__isnull=True)

class AuthorFilter(admin.SimpleListFilter):
    title = _('author')
    parameter_name = 'author'
    authors = User.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)

    def lookups(self, request, model_admin):
        return set_lookups(self.authors, 'username')
    
    def queryset(self, request, queryset):
        for author in self.authors:
            if self.value() == str(author.id): # because id from URL query is string
                return queryset.filter(author=author.id)

class OwnerArticle(admin.SimpleListFilter):
    title = _('owner Article')
    parameter_name = 'owner'
    articles = Article.objects.annotate(comment_count=Count('comments')).filter(comment_count__gt=0)

    def lookups(self, request, model_admin):
        return set_lookups(self.articles, 'title')

    def queryset(self, request, queryset):
        content_type = ContentType.objects.get(model='article')
        for article in self.articles:
            if self.value() == str(article.id): # because id from URL query is string
                qs = queryset.filter(content_type=content_type, object_id=article.id)
                print('returning qs: ', qs)
                return qs

class ParentComment(admin.SimpleListFilter):
    title = _('parent (for replies)')
    parameter_name = 'parent'
    parent_comments = Comment.objects.annotate(replies_count=Count('replies')).filter(replies_count__gt=0)

    def lookups(self, request, model_admin):
        return set_lookups(self.parent_comments, 'text')
        
    def queryset(self, request, queryset):
        for parent in self.parent_comments:
            if self.value() == str(parent.id): # because id from URL query is string
                return queryset.filter(parent=parent.id)
        
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_filter = (CommentOrReplyFilter, AuthorFilter, ParentComment, OwnerArticle,)

    list_display = ('id', 'author_link', 'text', 'pub_date_reformated', 'owner_object',  'parent_link', 'replies_link') 
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

    def parent_link(self, obj):
        if obj.parent:
            return mark_safe('<a href="{}">{} : {}...</a>'.format(
                reverse('admin:comments_comment_change', args=(obj.parent.pk,)),
                obj.parent.id,
                obj.parent.__str__()[:50]
            ))
        return '-'
    parent_link.short_description = 'parent' 
    parent_link.admin_order_field = 'parent'

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

    def replies_link(self, obj):
        if obj.parent != None: # if obj is reply, display '-'
            return '-'
        if obj.replies.count() > 0: # if obj is comment - link & num of replies
            return mark_safe('<a href="{}{}">{}</a>'.format(
                reverse('admin:comments_comment_changelist'),
                '?parent={}'.format(obj.id),
                '{} Replies'.format(obj.replies.count())          
            ))
        return 'no Replies' # obj is comment,  but has no replies
    replies_link.short_description = 'replies'
    replies_link.admin_order_field = 'replies_count' 

    def get_queryset(self, request):
        qs = super(CommentAdmin, self).get_queryset(request)
        qs = qs.annotate(
            replies_count=ExpressionWrapper(
                Count('replies'), 
                output_field=IntegerField()
            )
        )
        return qs