from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError

from my_newsapp.models import Category, Article
from my_newsapp.factories import (CategoryFactory, ArticleFactory, ImageFactory, FileFactory,
                                  remove_auto_generated_example_image_files)
from my_newsapp.utils import get_test_file

class CategoryTests(TestCase):

    def setUp(self):
        CategoryFactory(slug='primary', status='P')
        CategoryFactory(slug='secondary', status='S')
        CategoryFactory.create_batch(size=8)

    def tearDown(self):
        remove_auto_generated_example_image_files()

    def test_category_object_created(self):
        self.assertEqual(Category.objects.count(), 10)

    def test_category_object_updated(self):
        category = Category.objects.get(title='Primary')
        category.title = 'Changed'
        category.save()    
        self.assertEqual(category.title, 'Changed')
        # comment
            # When used as a context manager, assertRaises() accepts the additional keyword argument msg.
            # The context manager will store the caught exception object in its exception attribute. 
            # This can be useful if the intention is to perform additional checks on the exception raised.
        with self.assertRaises(Category.DoesNotExist) as cm: 
            Category.objects.get(title='Primary')
            self.assertEqual(cm.exception.msg, 'Category matching query does not exist.')

    def test_category_object_deleted(self):
        category = Category.objects.get(title='Primary')
        category.delete()
        with self.assertRaises(Category.DoesNotExist) as cm: 
            Category.objects.get(title='Primary')
            self.assertEqual(cm.exception.msg, 'Category matching query does not exist.')

    def test_manager_method_has_primary(self):
        categories = Category.objects.all()
        self.assertTrue(categories.has_primary())

        categories.get(status='P').delete()
        self.assertFalse(categories.has_primary())

    def test_manager_method_get_primary(self):
        categories = Category.objects.all()
        self.assertEqual(categories.get_primary().status, 'P')

        categories.get(status='P').delete()
        with self.assertRaises(Category.DoesNotExist) as cm: 
            categories.get_primary()
            self.assertEqual(cm.exception.msg, 'Category matching query does not exist.')

    def test_manager_method_has_secondary(self):
        categories = Category.objects.all()
        self.assertTrue(categories.has_secondary())

        categories.get(status='S').delete()
        self.assertFalse(categories.has_secondary())

    def test_manager_method_get_secondary(self):
        categories = Category.objects.all()
        self.assertEqual(categories.get_secondary().status, 'S')

        categories.get(status='S').delete()
        with self.assertRaises(Category.DoesNotExist) as cm: 
            categories.get_secondary()
            self.assertEqual(cm.exception.msg, 'Category matching query does not exist.')

    def test_get_absolute_url_method(self):
        category = Category.objects.get(title='Primary')
        another_category = Category.objects.filter(status=None)[0]
        self.assertEqual(category.get_absolute_url(), '/news/primary/' )
        self.assertEqual(another_category.get_absolute_url(), another_category.slug.join(['/news/', '/']) )

    def test__str__method(self):
        category = Category.objects.get(title='Primary')
        self.assertEqual(category.__str__(), 'Primary')

class ArticleTests(TestCase):

    def setUp(self):
        ArticleFactory.create_batch(size=5)

    def test_get_absolute_url_method(self):
        article = Article.objects.all()[0]
        self.assertEqual(article.get_absolute_url(), 
            '/news/{0}/{1}/{2}/'.format(article.category.slug, article.id, article.slug))

    def test__str__method(self):
        article = Article.objects.all()[0]
        self.assertEqual(article.__str__(), article.title)

    def test_ordering(self):
        articles = Article.objects.all()
        for i in range( 0, articles.count() - 1):
            self.assertTrue(articles[i].pub_date > articles[i+1].pub_date)

class ImageTests(TestCase):

    def setUp(self):
        self.image = ImageFactory(image__filename='test_image.png', image__format='png')
        self.invalid_image = ImageFactory(image__filename='test_image.ico', image__format='ico')

    def tearDown(self): # look FileTests tearDown() for explanation
        self.image.image.delete()
        self.invalid_image.image.delete()
        remove_auto_generated_example_image_files() # look factories.ImageFactory for explanation
        
    def test_image_create_with_supported_extension(self):
        # comment
            # Here we assert that AssertionError will be raised by self.assertRaises(ValidationError, image.full_clean),
            # for in this case image.full_clean doesn't raise ValidationError because file extension is valid.
        with self.assertRaises(AssertionError) as raised:
            self.assertRaises(ValidationError, self.image.full_clean)
            self.assertEqual(raised.exception.msg, 'ValidationError not raised by full_clean')

    def test_image_create_with_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            self.invalid_image.full_clean()

    def test__str__method(self):
        self.assertEqual(self.image.__str__(), self.image.image)
        self.assertEqual(self.image.__str__(), 'test_image.png')

class FileTests(TestCase):

    def setUp(self):
        self.doc_file = FileFactory(file=get_test_file('test_doc_file.doc'))
        self.pdf_file = FileFactory(file=get_test_file('test_pdf_file.pdf'))
        self.unsupported_file = FileFactory(file=get_test_file('test_file.txt'))

    def tearDown(self):
        # comment
            # Deletes uploaded test files from MEDIA_ROOT. Here, delete() is called on FileField, not on instance!
            # pylint is underlineing but it is correct: "When you access a FileField on a model, you are given an 
            # instance of FieldFile as a proxy for accessing the underlying file."
            #   https://docs.djangoproject.com/en/1.11/ref/models/fields/#filefield-and-fieldfile
            # -> linting was disabled for this in seetings.json: "python.linting.pylintArgs": [ "--disable=E1101" ]
        self.doc_file.file.delete()
        self.pdf_file.file.delete()
        self.unsupported_file.file.delete()

    def test_file_create_with_supported_extension(self):
        with self.assertRaises(AssertionError) as raised:
            self.assertRaises(ValidationError, self.doc_file.full_clean)
            self.assertEqual(raised.exception.msg, 'ValidationError not raised by full_clean')

    def test_file_create_with_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            self.unsupported_file.full_clean()

    def test__str__method(self):
        self.assertEqual(self.doc_file.__str__(), 'test_doc_file.doc')

    def test_name_method(self):
        self.assertEqual(self.doc_file.name(), 'test_doc_file.doc')
        self.assertEqual(self.doc_file.name(), self.doc_file.__str__())
        
    def test_get_type_icon_method(self):
        self.assertEqual(self.doc_file.get_type_icon(),
            '{0}{1}'.format('my_newsapp/file_type_icons/', self.doc_file.CONTENT_TYPE_ICON_PAIRS[2][1]))
        self.assertEqual(self.pdf_file.get_type_icon(),
            '{0}{1}'.format('my_newsapp/file_type_icons/', self.pdf_file.CONTENT_TYPE_ICON_PAIRS[0][1]))
        
    def test_content_type_method(self):
        self.assertEqual(self.doc_file.content_type(), self.doc_file.CONTENT_TYPE_ICON_PAIRS[2][0])
        self.assertEqual(self.pdf_file.content_type(), self.pdf_file.CONTENT_TYPE_ICON_PAIRS[0][0])
                
    def test_path_method(self):
        self.assertEqual(self.doc_file.path(), 
            '{0}{1}'.format(settings.MEDIA_ROOT, 'files/test_doc_file.doc'))