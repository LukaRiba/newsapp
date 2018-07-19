from django.forms import ModelForm, BaseInlineFormSet, TextInput, ValidationError, Textarea
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper

from my_newsapp.models import Article, Image

class ArticleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False #ne kreira <form> i </form> tagove, već se moraju ručno napisati u template-u

    class Meta:
        model = Article
        fields = ('title', 'short_description', 'text', 'category')
        widgets = {
            'title': TextInput(attrs={'autocomplete': 'off'}),
            'short_description': Textarea(attrs={'rows': 4}),
            'text': Textarea(attrs={'rows':20}),
        }

class ImageForm(ModelForm):
    
    class Meta:
        model = Image
        fields = ('image', 'description')
        widgets = {
            'description': TextInput(attrs={'autocomplete': 'off'}),
        }

#comment
    # After image = form.cleaned_data['image'], image is InMemoryUploadedFile type 
    # (<class 'django.core.files.uploadedfile.InMemoryUploadedFile'>). Zbog toga, ako bi u image listu appendali
    # image, provjera 'if image in images:' bi vratila False iako bi uploadali iste slike (duplikate) - očito 
    # InMemoryUploadedFile instance različite iako sadrže isti uploadani file. Zato gettamo file name:
    #    image.name -> type(image.name) == str , i sada, pošto provjeravamo da li se određeni string nalazi u 
    # images listi, provjera 'if image.name in images:' radi ispravno i vraća True ako uploadamo dva file-a
    # istog naziva.
class ImageInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super(ImageInlineFormSet, self).clean()
        # Don't bother validating the formset unless each form is valid on its own
        if any(self.errors):
            return
        # Check if image(s) uploaded 
        if not self.files:
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
                continue
        
ImageFormSet = inlineformset_factory(Article, Image, form=ImageForm, formset=ImageInlineFormSet, 
                                     extra=1, max_num=20,  can_delete=True)