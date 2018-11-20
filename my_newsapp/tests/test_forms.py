import tempfile

from django.test import TestCase, override_settings

from my_newsapp.forms import ArticleForm, ImageForm, FileForm, ImageFormSet, FileFormSet, LoginForm
from my_newsapp.models import User
from my_newsapp.utils import get_test_file
from my_newsapp.tests.factories import ArticleFactory, ImageFactory, CategoryFactory

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class ArticleFormTests(TestCase):
    
    def setUp(self):
        self.category = CategoryFactory()
        self.data = {
            'title': 'Test Article',
            'short_description': 'This is a test article.',
            'text': 'This is a text of test article',
            'category': self.category.id
        }

    def test_empty_fields(self):
        form = ArticleForm(data={})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'title': ['This field is required.'], 
            'short_description': ['This field is required.'], 
            'text': ['This field is required.'], 
            'category': ['This field is required.']
        })

    def test_article_with_entered_title_already_exists(self):
        ArticleFactory(title='Test Article')
        form = ArticleForm(data=self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'title': ['Article with this Title already exists.']})

    def test_valid_data(self):
        form = ArticleForm(data=self.data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

class ImageFormTests(TestCase):
    
    def setUp(self):
        self.description = {'description': 'This is an image description.'}
        self.valid_image = get_test_file('test_image.png')
        self.invalid_image = get_test_file('test_image.cdr')

    def test_no_image_no_description(self):
        form = ImageForm(data={}, files={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data, {})
        self.assertEqual(form.files, {})

    def test_invalid_image_format(self):
        form = ImageForm(data={}, files={'image': self.invalid_image})
        self.assertFalse(form.is_valid())
        self.assertRaises(KeyError) # no key 'image' in cleaned_data
        self.assertEqual(form.cleaned_data, {'description': None}) # no image because of invalid format.
        self.assertEqual(form.errors, {
            'image': ['Upload a valid image. The file you uploaded was either not an image or a corrupted image.'],
            '__all__': ['Image cannot be uploaded. Valid formats are bmp, gif, png, jpg and jpeg.']}
        )

    def test_valid_image_no_description(self):
        form = ImageForm(data={}, files={'image': self.valid_image})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data, {})
        self.assertEqual(str(form.files), "{'image': <SimpleUploadedFile: test_image.png (image/png)>}")

    def test_valid_image_with_description(self):
        form = ImageForm(data=self.description, files={'image': self.valid_image})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data, {'description': 'This is an image description.'})
        self.assertEqual(str(form.files), "{'image': <SimpleUploadedFile: test_image.png (image/png)>}")

    def test_no_image_with_description(self):
        form = ImageForm(data=self.description, files={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.data, {'description': 'This is an image description.'})
        self.assertEqual(form.files, {})
        self.assertEqual(form.errors, {'__all__': ['You cannot have description if image is not choosen.']})

class FileFormTests(TestCase):
    
    def setUp(self):
        self.valid_file = get_test_file('test_pdf_file.pdf')
        self.invalid_file = get_test_file('test_JPG.jpg')
    
    def test_no_file(self):
        form = FileForm(files={})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.files, {})

    def test_valid_file_format(self):
        form = FileForm(files={'file': self.valid_file})

        self.assertTrue(form.is_valid())
        self.assertEqual(str(form.files), "{'file': <SimpleUploadedFile: test_pdf_file.pdf (application/pdf)>}")

    def test_invalid_file_format(self):
        form = FileForm(files={'file': self.invalid_file})

        self.assertFalse(form.is_valid())
        self.assertRaises(KeyError) # no key 'file' in cleaned_data
        self.assertEqual(form.cleaned_data, {}) # no file because of invalid format.
        self.assertEqual(form.errors, {'file': 
            ["File extension 'jpg' is not allowed. Allowed extensions are: 'pdf, doc, docx, xls, xlsx, ppt, pptx, zip'."]}
        )

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class ImageInlineFormSetTests(TestCase):
    
    def setUp(self):
        self.image_1 = get_test_file('test_image.png')
        self.image_2 = get_test_file('test_image_2.png')
        self.data = {
            'images-TOTAL_FORMS': '1', 
            'images-INITIAL_FORMS': '0', 
            'images-MIN_NUM_FORMS': '0', 
            'images-MAX_NUM_FORMS': '20', 
            'images-0-description': '', 
        }
        self.files = {}

    def test_1_form_no_image_no_description(self):
        formset = ImageFormSet(self.data, self.files)

        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), ['You have to upload at least one image.'])

    def test_1_form_image_uploaded_no_description(self):
        self.files.update({'images-0-image': self.image_1})

        formset = ImageFormSet(self.data, self.files)

        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), [])

    def test_2_form_one_image_uploaded_in_second_form(self):
        self.data.update({
            'images-TOTAL_FORMS': '2',
            'images-1-description': '', 
        })
        self.files.update({
            'images-1-image': self.image_1
        })

        formset = ImageFormSet(self.data, self.files)

        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) # 2 image_forms 2 dicts
        self.assertEqual(formset.non_form_errors(), [])

    def test_2_forms_with_duplicate_images_updated(self):
        self.data.update({
            'images-TOTAL_FORMS': '2',
            'images-1-description': '', 
        })
        self.files.update({
            'images-0-image': self.image_1,
            'images-1-image': self.image_1
        })

        formset = ImageFormSet(self.data, self.files)

        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) # 2 image_forms 2 dicts
        self.assertEqual(formset.non_form_errors(), [
            'You have uploaded duplicate image files. Image files have to be unique.'
        ])

    def test_2_forms_with_different_images(self):
        self.data.update({
            'images-TOTAL_FORMS': '2',
            'images-1-description': '', 
        })
        self.files.update({
            'images-0-image': self.image_1,
            'images-1-image': self.image_2
        })

        formset = ImageFormSet(self.data, self.files)

        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) 
        self.assertEqual(formset.non_form_errors(), [])
    
    def test_no_image_uploaded_when_instance_already_has_image_which_is_not_selected_for_deletion(self):
        formset = ImageFormSet(self.data, self.files)

        # create formset instance and its image
        formset.instance = ArticleFactory()
        ImageFactory(article=formset.instance)

        # no images selected for deletion
        formset.selected_images = []

        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), [])

    def test_no_image_uploaded_when_instance_already_has_image_which_is_selected_for_deletion(self):
        formset = ImageFormSet(self.data, self.files)

        # create formset instance and its image
        formset.instance = ArticleFactory()
        ImageFactory(article=formset.instance)

        # image selected for deletion (its str(id) is in self.selected_images)
        formset.selected_images = [str(formset.instance.images.first().id)]

        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), [
            'Article must have at least one image. Upload new one if deleting all.'
        ])

    def test_no_image_uploaded_when_instance_already_has_two_images_of_which_one_is_selected_for_deletion(self):
        formset = ImageFormSet(self.data, self.files)

        # create formset instance and its image
        formset.instance = ArticleFactory()
        ImageFactory.create_batch(size=2, article=formset.instance)

        # first image selected for deletion (its str(id) is in self.selected_images)
        formset.selected_images = [str(formset.instance.images.first().id)]

        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), [])
    
class FileInlineFormSetTests(TestCase):
    
    def setUp(self):
        self.file_1 = get_test_file('test_doc_file.doc')
        self.file_2 = get_test_file('test_pdf_file.pdf')
        self.data = {
            'files-TOTAL_FORMS': '2', 
            'files-INITIAL_FORMS': '0', 
            'files-MIN_NUM_FORMS': '0', 
            'files-MAX_NUM_FORMS': '20', 
        }
        self.files = {}

    def test_2_forms_no_files_uploaded(self):
        formset = FileFormSet(data=self.data, files=self.files)
        self.assertTrue(formset.is_valid())

    def test_2_form_valid_file_uploaded_in_second_form(self):
        self.files.update({
            'files-1-file': self.file_1
        })
        formset = FileFormSet(data=self.data, files=self.files)
        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) 
        self.assertEqual(formset.non_form_errors(), [])

    def test_2_forms_duplicate_files_uploaded(self):
        self.files.update({
            'files-0-file': self.file_1,
            'files-1-file': self.file_1
        })

        formset = FileFormSet(data=self.data, files=self.files)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) 
        self.assertEqual(formset.non_form_errors(), [
            'You have uploaded duplicate files. Files have to be unique.'
        ])

    def test_2_forms_different_files_uploaded(self):
        self.files.update({
            'files-0-file': self.file_1,
            'files-1-file': self.file_2
        })

        formset = FileFormSet(data=self.data, files=self.files)
        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}]) 
        self.assertEqual(formset.non_form_errors(), [])
         
class LoginFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_empty_fields(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'username': ['This field is required.'],
            'password': ['This field is required.']
        })

    def test_invalid_username(self):
        form = LoginForm(data={'username': 'wrongname', 'password': 'testpass123'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': ['Please enter a correct username and password. Note that both fields may be case-sensitive.'],
        })

    def test_invalid_password(self):
        form = LoginForm(data={'username': 'testuser', 'password': '12345'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': ['Please enter a correct username and password. Note that both fields may be case-sensitive.'],
        })

    def test_valid_username_and_password(self):
        form = LoginForm(data={'username': 'testuser', 'password': 'testpass123'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})
    