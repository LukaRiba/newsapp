from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit, HTML

from .models import Article


class CreateArticleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('title', autocomplete='off'),
            Field('short_description', style="max-height: 100px;"),
            Field('first_part'),
            Field('second_part'),
            Field('category'),
            Fieldset("Choose images for your article",
                Field('thumbnail_image'),
                Field('first_image'),
                Field('second_image'),
            )
        )
        self.helper.field_class = 'mb-3'
        self.helper.add_input(Submit('submit', 'Publish'))

    class Meta:
        model = Article
        # fields = '__all__'
        fields = ('title', 'short_description', 'first_part', 'second_part', 'category', 'thumbnail_image', 'first_image', 'second_image')