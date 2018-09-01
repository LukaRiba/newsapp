from django.forms import ModelForm, Form, Textarea, CharField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Button

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
        self.auto_id = False
        self.helper.layout = Layout(
            Field('text', placeholder='Your reply...', required=True),
            ButtonHolder(
                Submit('submit', 'Reply', css_class='button white btn-sm')
            )
        )

class EditForm(Form):
    text = CharField(widget=Textarea(attrs={'rows':2}))

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        self.auto_id = False
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('text', required=True),
            ButtonHolder(
                Button('button', 'Cancel', css_class='button btn-secondary btn-sm cancel-button'),
                Submit('submit', 'OK', css_class='button white btn-sm')
            )
        )

    
