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
            }),
        }

class FileForm(ModelForm):
    
    class Meta:
        model = File
        fields = ('file',)
        widgets = {
            'file': FileInput(attrs={
                'accept': '.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .zip',
            })
        }

class ImageInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super(ImageInlineFormSet, self).clean()

        # Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return

        # comment
            # the line: 'if not self.files:' is not good solution because it checks for files in request.FILES for
            # files, and if we upload files in file_formset, but not in image_formset, this contition will ge false,
            # because there are self.files as both image_formset and file_formset are passed same file dict (request.POST)
            # in constructors inside CreateArticleView.
        if not any([ 'image' in key for key in self.files.keys() ]): # if no image has been uploaded
            if not self.instance.images.all(): # check if article already has image (if editing article)
                raise ValidationError('You have to upload at least one image.')

        images = []
        for form in self.forms:
            try:
                image = form.cleaned_data['image']
                description = form.cleaned_data['description']
                # Check if there is description but no image
                if description and not image:
                    raise ValidationError('You cannot have description if image is not choosen')
                # Check for duplicate images
                image_name = image.name
                if image_name in images:
                    raise ValidationError(
                        'You have uploaded duplicate image files. Image files have to be unique.'
                    )
                images.append(image_name)
            # Ako uploadamo sliku u npr. drugoj formi, a u prvoj ne, KeyError will raise za prvu formu
            except KeyError: 
                pass
        
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
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),    
            )