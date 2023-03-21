from django.forms import ModelForm, BaseInlineFormSet, TextInput, FileInput, ValidationError, Textarea
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from .models import Article, Image, File

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'short_description', 'text', 'category')
        widgets = {
            'title': TextInput(attrs={'autocomplete': 'off'}),
            'short_description': Textarea(attrs={'rows': 4}),
            'text': Textarea(attrs={'rows':20}),
        }

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # disables html required attribute in fields
        # self.use_required_attribute =  False

    def validate_text(self, text: str):
        return len(text) > 100

class ImageForm(ModelForm):

    class Meta:
        model = Image
        fields = ('image', 'description')
        widgets = {
            'image': FileInput(attrs={
                'accept': '.bmp, .gif, .png, .jpg, .jpeg',
                'class': 'image-input'
            }),
            'description': TextInput(attrs={
                'autocomplete': 'off',
                'class': 'textinput textInput form-control',
                'placeholder': 'Describe image'
            }),
        }

    def clean(self):
        super(ImageForm, self).clean()
        try:
            image = self.cleaned_data['image']
        except KeyError: # if format not supported, image is not uploaded and there is no 'image' key in cleaned data
            raise ValidationError('Image cannot be uploaded. Valid formats are bmp, gif, png, jpg and jpeg.')
        description = self.cleaned_data['description']
        # Check if there is description but no image
        if description and not image:
            raise ValidationError('You cannot have description if image is not choosen.', code='description_only')


class FileForm(ModelForm):

    class Meta:
        model = File
        fields = ('file',)
        widgets = {
            'file': FileInput(attrs={'accept': '.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .zip',})
        }

class ImageInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.selected_images = kwargs.pop('selected_images', None)
        super(ImageInlineFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        super(ImageInlineFormSet, self).clean()

        #  Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return

        if not any([ 'image' in key for key in self.files.keys() ]): # if no image has been uploaded.
            if not self.image_ids(): # if article has no images. Possible case in create-article view.
                raise ValidationError('You have to upload at least one image.')
            if self.all_images_selected_for_deletion(): # possible case in edit-article view
                raise ValidationError('Article must have at least one image. Upload new one if deleting all.')

        images = []
        for form in self.forms:
            try:
                image = form.cleaned_data['image']
                if image:
                    image_name = image.name
                    if image_name in images:
                        raise ValidationError(
                            'You have uploaded duplicate image files. Image files have to be unique.'
                        )
                    images.append(image_name)
            # Ako uploadamo sliku u npr. drugoj formi, a u prvoj ne, KeyError will raise za prvu formu
            except KeyError:
                pass

    # str(image_id) bacause 'image-checkbox[]' stores values as strings, not as integers.
    def all_images_selected_for_deletion(self):
        for image_id in self.image_ids():
            try: # when clean() is called from EditArticleView post() method
                if not str(image_id) in self.request.POST.getlist('image-checkbox[]'):
                    return False
            except AttributeError: # when clean() is called second time, in case of invalid image_formset when post() returns get()
                if not str(image_id) in self.selected_images:
                    return False
        return True

    def image_ids(self):
        return [image.id for image in self.instance.images.all()]

ImageFormSet = inlineformset_factory(Article, Image, form=ImageForm, formset=ImageInlineFormSet,
                                     extra=1, max_num=20,  can_delete=True)

class FileInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super(FileInlineFormSet, self).clean()
        # Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return

        files = []
        for form in self.forms:
            try:
                file = form.cleaned_data['file']
                # Check for duplicate files
                file_name = file.name
                if file_name in files:
                    raise ValidationError(
                        'You have uploaded duplicate files. Files have to be unique.'
                    )
                files.append(file_name)
            except KeyError:
                pass

FileFormSet = inlineformset_factory(Article, File, form=FileForm, formset=FileInlineFormSet,
                                     extra=1, max_num=20,  can_delete=True)

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # disables html required attribute in fields
        # self.use_required_attribute = False
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            )
