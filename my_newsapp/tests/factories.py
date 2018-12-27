from django.contrib.auth.models import User
from django.utils import timezone

import factory

from my_newsapp.models import Category, Article, Image, File

def create_slug(sentence):
    return '-'.join(sentence.split(' ')).lower()

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User 
        django_get_or_create = ('username', 'password')

    username = factory.Sequence(lambda n: 'user-%d' % n)
    password = factory.Faker('password', length=10)

class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Category 
        django_get_or_create = ('title', 'slug', 'image', 'status')

    slug = factory.Sequence(lambda n: 'category-%d' % n)
    title = factory.LazyAttribute(lambda obj: '{0}'.format(obj.slug.title()))
    image = factory.django.ImageField()
    status = None

class ArticleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Article 
        django_get_or_create = ('title', 'slug', 'text', 'short_description', 'pub_date', 'author', 'category')

    title = factory.Faker('sentence')
    slug = factory.LazyAttribute(lambda obj: '{0}'.format(create_slug(obj.title)))
    text = factory.Faker('text')
    short_description = factory.Faker('text', max_nb_chars=50)
    # Without tzinfo RuntimeWarning is raised: DateTimeField Article.pub_date received anaive datetime
    # while time zone support is active. 
    pub_date = factory.Faker('past_datetime', tzinfo=timezone.utc)
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)

class ImageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Image 
        django_get_or_create = ('image', 'description', 'article') # image field is not included here

    image = factory.django.ImageField()
    description = factory.Faker('text', max_nb_chars=30)
    article = factory.SubFactory(ArticleFactory)

class FileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = File 
        django_get_or_create = ('file', 'article')

    file = factory.django.FileField()
    article = factory.SubFactory(ArticleFactory)
