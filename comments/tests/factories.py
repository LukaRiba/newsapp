from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import factory

from comments.models import Comment
from my_newsapp.tests.factories import UserFactory

class CommentFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Comment

    author = factory.SubFactory(UserFactory)
    text = factory.Faker('text', max_nb_chars=50)
    pub_date = factory.Faker('past_datetime', tzinfo=timezone.utc)
    content_type = ContentType.objects.get(model='article')
    object_id = None # must be set in CommentFactory constructor
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
