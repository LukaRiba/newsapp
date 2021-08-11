import tempfile

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse

from my_newsapp.models import Category, Article
from my_newsapp.tests.factories import CategoryFactory, ArticleFactory, ImageFactory, FileFactory
from my_newsapp.utils import get_test_file

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CategoryTests(TestCase):

    def setUp(self):
        CategoryFactory(slug='primary', status='P')
        CategoryFactory(slug='secondary', status='S')
        CategoryFactory.create_batch(size=8)

    def test_category_object_created(self):
        self.assertEqual(Category.objects.count(), 10)

    def test_category_object_updated(self):
        category = Category.objects.get(title='Primary')
        category.title = 'Changed'
        category.save()    
        self.assertEqual(category.title, 'Changed')
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
        self.assertEqual(category.get_absolute_url(), reverse('my_newsapp:category', kwargs={'slug': 'primary'}))

    def test__str__method(self):
        category = Category.objects.get(title='Primary')
        self.assertEqual(category.__str__(), 'Primary')

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class ArticleTests(TestCase):

    def setUp(self):
        ArticleFactory.create_batch(size=5)

    def test_get_absolute_url_method(self):
        article = Article.objects.all()[0]
        self.assertEqual(article.get_absolute_url(), 
            reverse('my_newsapp:article-detail', kwargs={'category': article.category.slug, 'id': article.id, 'slug': article.slug})
        )

    def test__str__method(self):
        article = Article.objects.all()[0]
        self.assertEqual(article.__str__(), article.title)

    def test_ordering(self):
        articles = Article.objects.all()
        for i in range( 0, articles.count() - 1):
            self.assertTrue(articles[i].pub_date > articles[i+1].pub_date)

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class ImageTests(TestCase):

    def setUp(self):
        self.image = ImageFactory(image__filename='test_image.png', image__format='png')
        self.invalid_image = ImageFactory(image__filename='test_image.ico', image__format='ico')

    def tearDown(self): 
        self.image.image.delete()
        self.invalid_image.image.delete()
        
    def test_image_create_with_supported_extension(self):
        with self.assertRaises(AssertionError) as raised:
            self.assertRaises(ValidationError, self.image.full_clean)
            self.assertEqual(raised.exception.msg, 'ValidationError not raised by full_clean')

    def test_image_create_with_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            self.invalid_image.full_clean()

    def test__str__method(self):
        self.assertEqual(self.image.__str__(), self.image.image)
        self.assertEqual(self.image.__str__(), 'test_image.png')

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class FileTests(TestCase):

    def setUp(self):
        self.doc_file = FileFactory(file=get_test_file('test_doc_file.doc'))
        self.pdf_file = FileFactory(file=get_test_file('test_pdf_file.pdf'))
        self.unsupported_file = FileFactory(file=get_test_file('test_file.txt'))

    def tearDown(self):
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