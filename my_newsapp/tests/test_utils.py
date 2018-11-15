import tempfile
import io
from unittest.mock import patch, mock_open

from django.test import TestCase, override_settings

from my_newsapp.utils import (get_status_none_categories_random_ids, content_type, field_values, 
    get_test_files_dir_path, get_test_file)
from my_newsapp.factories import CategoryFactory, ArticleFactory, ImageFactory, FileFactory

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class UtilsTests(TestCase):

    def test_get_status_none_categories_random_ids(self):
        primary = CategoryFactory(status='P')
        secondary = CategoryFactory(status='S')
        none_categories = CategoryFactory.create_batch(size=10)

        none_ids = get_status_none_categories_random_ids()
        another_none_ids = get_status_none_categories_random_ids()

        # check that returned lists are not equal (because elements are in different order):
        while none_ids == another_none_ids:
            # it is possible that function returns lists with equal ordered elements two times in a row (but very
            # unlikely). If that happens, call it again and proceed when lists are not equal.
            another_none_ids = get_status_none_categories_random_ids()
        self.assertNotEqual(none_ids, another_none_ids)

        # check that returned lists contain equal elements (ids)
        self.assertEqual(sorted(none_ids), sorted(another_none_ids))

        # check that status none categories ids are in lists returned by function.
        # check only one as they contain equal elements (if we are here, assertion above has passed)
        for category in none_categories:
            self.assertIn(category.id, none_ids)

        # check that there is not primary.id, nor secondary.id in returned list
        self.assertFalse(primary.id in none_ids or secondary.id in none_ids)
    
    def test_content_type(self):
        file_path = 'my_newsapp/tests/test_files/test_pdf_file.pdf'
        file_content_type = 'application/pdf'

        self.assertEqual(content_type(file_path), file_content_type)

    def test_get_test_files_dir_path(self):
        with self.settings(BASE_DIR='/base_dir/'):
            self.assertEqual(get_test_files_dir_path(), '/base_dir/my_newsapp/tests/test_files/')

    @patch('my_newsapp.utils.get_test_files_dir_path', return_value='/test_files/')
    @patch('my_newsapp.utils.content_type', return_value='text/plain')
    @patch('builtins.open', new_callable=mock_open, read_data=io.BytesIO(b'test data').read())
    def test_get_test_file(self, m_open, m_content_type, m_get_test_files_dir_path):
        filename = 'fake_test_file.txt'
        # as name of file object returned by real open() function returns file path
        file_path = m_open().name = f'{m_get_test_files_dir_path()}{filename}' 
        simple_uploaded_file = get_test_file(filename)

        assert type(simple_uploaded_file).__name__ == 'SimpleUploadedFile'
        assert simple_uploaded_file.name == filename # SimpleUploadedFile cuts the path and maintains just name of the file
        assert simple_uploaded_file.read() == b'test data'
        assert simple_uploaded_file.content_type == 'text/plain'

        m_open.assert_called_with(file_path, 'rb')
        m_content_type.assert_called_with(file_path)
        m_get_test_files_dir_path.assert_called_with()

    def test_field_values(self):
        article = ArticleFactory()
        ImageFactory.create_batch(size=2, article=article)
        FileFactory.create_batch(size=2, article=article)
        field_value_dict = field_values(article)

        self.maxDiff = None
        self.assertEqual(field_value_dict, {
            'images': str(article.images.all()),
            'files': str(article.files.all()),
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'text': article.text,
            'short_description': article.short_description,
            'pub_date': article.pub_date,
            'author': article.author,
            'category': article.category,
            'comments': str(article.comments.all())        
        })