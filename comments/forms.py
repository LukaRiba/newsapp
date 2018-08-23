from django.forms import ModelForm, Textarea

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

from .models import Comment

class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('text', placeholder='Your comment...', required=True),
            ButtonHolder(
                Submit('submit', 'Comment', css_class='button white btn-sm')
            )
        )

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'rows':2}),
        }

class ReplyForm(CommentForm):
    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field('text', placeholder='Your reply...', id='reply-text', required=True),
            ButtonHolder(
                Submit('submit', 'Reply', css_class='button white btn-sm')
            )
        )