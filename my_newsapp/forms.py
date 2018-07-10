from django.forms import ModelForm, ImageField, ClearableFileInput
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, HTML, Div



from .models import Article, Image

class ArticleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False #ne kreira <form> i </form> tagove, već se moraju ručno napisati u template-u

    class Meta:
        model = Article
        fields = ('title', 'short_description', 'text', 'category')

class ImageForm(ModelForm):
    

    class Meta:
        model = Image
        fields = ('image', 'description')

ImageFormSet = inlineformset_factory(Article, Image, form=ImageForm, extra=1,  can_delete=True)





