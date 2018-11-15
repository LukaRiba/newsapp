from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import factory

from comments.models import Comment
from my_newsapp.factories import ArticleFactory

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
    content_type = ContentType.objects.get(model=comment_owner.__class__.__name__)
    object_id = comment_owner.id
