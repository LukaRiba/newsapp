import os
import time
from random import shuffle

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

import factory

from .models import Category, Article, Image, File

def create_slug(sentence):
    return '-'.join(sentence.split(' ')).lower()

# Remove example.jpg and example.dat files created by factory.django.ImageField() and factory.django.FileField()
def remove_auto_generated_example_files():
    directories = [images_dir(), files_dir()]
    for directory in directories:
        for file in os.listdir(directory):
            if is_example_file_auto_generated_by_factory(file):
                os.remove('{0}{1}'.format(directory, file))

def images_dir():
    return settings.MEDIA_ROOT

def files_dir():
    return os.path.join(settings.MEDIA_ROOT, 'files/')

def is_example_file_auto_generated_by_factory(file):
    return file.startswith('example') and (time.time() > os.path.getmtime(media_path(file)) > time.time() - 10) 

def media_path(file):
    if file.endswith('.dat'):
        return '{0}{1}'.format(files_dir(), file)
    return '{0}{1}'.format(images_dir(), file)

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User 
        django_get_or_create = ('username', 'password')

    username = factory.Sequence(lambda num: 'user%d' % num)
    password = factory.Faker('password', length=10)


class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Category 
        django_get_or_create = ('title', 'slug', 'image', 'status')

    slug = factory.Sequence(lambda num: 'category-%d' % num)
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

def get_valid_image_format():
    valid_formats = ['bmp', 'gif', 'png', 'jpg', 'jpeg']
    shuffle(valid_formats)
    return valid_formats[0]

class ImageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Image 
        django_get_or_create = ('image', 'description', 'article') # image field is not included here

    #comment
        # for some reason, for model's image field (even when it is not included in django_get_or_create), factory
        # creates example.jpg image file and saves it to MEDIA_ROOT, even if in ImageFactory constructor arguments
        # are passed for different name and format of the image - and that different image is created too and used in tests!
        # So, two files are created - default arguments create example.jpg and provided ones another image which is
        # actually image of the image field. It must be a bug of some kind - default arguments are overriden, but 
        # image file is still created from default arguments and saved in MEDIA_ROOT folder, even if it is not
        # value of ImageField and so has nothing to do with created Image instance !!!?? So, when in test's tearDown()
        # method self.image.image.delete() and self.invalid_image.image.delete() are called, image files binded to
        # ImageField are deleted (we want that), but those default example.jpg-s are left in MEDIA_ROOT, so obvious
        # solution is to find them through os and remove them manually, also in tearDown().
    image = factory.django.ImageField()
    description = factory.Faker('text', max_nb_chars=30)
    article = factory.SubFactory(ArticleFactory)

class FileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = File 
        django_get_or_create = ('file', 'article')

    file = factory.django.FileField()
    article = factory.SubFactory(ArticleFactory)


    


    


    