from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import factory

from comments.models import Comment
from my_newsapp.tests.factories import ArticleFactory

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User 

    username = factory.Faker('name')
    password = factory.Faker('password', length=10)

#comment
    # Object to use as a GenericForeignKey. With this, content_type is set to 'article_type', and object_id
    # is comment_owner id. In tests, if we wont to create comments with different owner article, or many 
    # comments with same owner article, it is enough to create new article (a = ArticleFactory) and then
    # pass its id to CommentFactory constructor (CommentFactory(object_id=a.id))
comment_owner = ArticleFactory()

class CommentFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    text = factory.Faker('text', max_nb_chars=50)
    pub_date = factory.Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    content_type = ContentType.objects.get(model='article')
    object_id = comment_owner.id
    # comment
        # Gets content_object through content_type and object_id after creation of comment (Lazy attribute).
        # This is what GenericForeignKey does (see Comment model). Without setting content_object like this,
        # if we create comment passing some article id as object_id:
        #   comment = CommentFactory(object_id=article_instance.id),
        # content_object will not be assigned and in our tests when we call article_instance.comments.all()
        # we get empty queryset! If we print comment.content_object we get 'log entry' -> so we se that no object is 
        # assigned to thet field. When working with real model, content_object is assigned because
        # content_object is GenericForeignKey field, so we must also assign it here like this.
    content_object = factory.LazyAttribute(lambda obj: obj.content_type.get_object_for_this_type(pk=obj.object_id))


class ReplyFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    text = factory.Faker('text', max_nb_chars=50)
    pub_date = factory.Faker('past_datetime', start_date='-30d', tzinfo=timezone.utc)
    content_type = ContentType.objects.get(model='comment')
    object_id = factory.LazyAttribute(lambda obj: obj.parent.id)
    content_object = factory.LazyAttribute(lambda obj: obj.content_type.get_object_for_this_type(pk=obj.object_id))
    parent = factory.SubFactory(CommentFactory)
