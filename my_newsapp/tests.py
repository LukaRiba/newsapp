from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .forms import ImageFormSet

# Popis assert metoda -> https://docs.python.org/2/library/unittest.html#unittest.TestCase.debug
#                     -> https://docs.djangoproject.com/en/1.11/topics/testing/tools/#assertions
class CreateArticleFormTests(TestCase):

    def test_imageformset_1_form_no_image_uploaded(self):
        data = {
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '', 
            'images-0-description': 'img1 description',
        }
        files = {}
        formset = ImageFormSet(data, files)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}])
        self.assertEqual(formset.non_form_errors(), 
                         ['You have to upload at least one image.'])

    def test_imageformset_2_forms_with_valid_data(self):
        # https://docs.python.org/2/library/functions.html#open - mode argument 'rb' in open() method explained
        img = open('/Users/luka/Downloads/git_pic.jpg', 'rb')
        img2 = open('/Users/luka/Downloads/Images/car.png', 'rb')
        data = {
            'images-TOTAL_FORMS': '2',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '', 
            'images-0-description': 'img1 description',
            'images-1-description': 'img2 description'
        }
        files = {
            'images-0-image': SimpleUploadedFile(img.name, img.read()),
            'images-1-image': SimpleUploadedFile(img2.name, img2.read())
        }
        #comment
        # Kod testiranja bilo koje forme, samim time i formset-a, ukoliko forma sadrži FileField,
        # kod instanciranja se fileov-i prosljeđuju kao poseban dictionary, uz post data dictionary. Vidimo dolje
        # primjer konstruktora za BaseInlineFormset:
        #   class BaseInlineFormSet(BaseModelFormSet):
        #        """A formset for child objects related to a parent."""
        #        def __init__(self, data=None, files=None, instance=None,
        #                     save_as_new=False, prefix=None, queryset=None, **kwargs):
        # U biti, isto to činimo kada inicijaliziramo FormSet u view-u, pa bound-amo data-u tako što
        # konstruktoru damo argumente request.Post (data) i request.FILES - to se tada odnosi na data i file-ove
        # koje je user ispunio/dodao u stvarnu formu na CreateArticleView-u:
        #     [...]
        #     context['image_formset'] = ImageFormSet(self.request.POST, files=self.request.FILES)
        #     [...]
        #  Isto moramo simulirati u test-u, kao tu.
        #endcomment
        formset = ImageFormSet(data, files)
        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}])
        self.assertEqual(formset.non_form_errors(), [])

    def test_imageformset_2_forms_with_duplicate_uploaded_images(self):
        img = open('/Users/luka/Downloads/git_pic.jpg', 'rb')
        uploaded_img = SimpleUploadedFile(img.name, img.read())
        data = {
            'images-TOTAL_FORMS': '2',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '', 
            'images-0-description': 'img1 description',
            'images-1-description': 'img2 description'
        }
        files = {
            'images-0-image': uploaded_img,
            'images-1-image': uploaded_img
        }
        formset = ImageFormSet(data, files)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}])
        self.assertEqual(formset.non_form_errors(), 
                         ['You have uploaded duplicate image files. Image files have to be unique.'])

    def test_imageformset_2_forms_first_empty_second_valid(self):
        img = open('/Users/luka/Downloads/git_pic.jpg', 'rb')
        data = {
            'images-TOTAL_FORMS': '2',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '', 
            'images-0-description': '',
            'images-1-description': 'img2 description'
        }
        files = {
            'images-1-image': SimpleUploadedFile(img.name, img.read())
        }
        formset = ImageFormSet(data, files)
        self.assertTrue(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}])
        self.assertEqual(formset.non_form_errors(), [])

    def test_imageformset_2_forms_first_valid_second_description_only(self):
        img = open('/Users/luka/Downloads/git_pic.jpg', 'rb')
        data = {
            'images-TOTAL_FORMS': '2',
            'images-INITIAL_FORMS': '0',
            'images-MAX_NUM_FORMS': '', 
            'images-0-description': 'Description only',
            'images-1-description': 'img description'
        }
        files = {
            'images-1-image': SimpleUploadedFile(img.name, img.read())
        }
        formset = ImageFormSet(data, files)
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.errors, [{}, {}])
        self.assertEqual(formset.non_form_errors(), ['You cannot have description if image is not choosen'])



    


