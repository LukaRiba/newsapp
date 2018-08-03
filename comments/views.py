from .models import Comment
from .forms import CommentForm, ReplyForm

class CommentContextMixin:

    def get_context_data(self, model_name, object_id, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(content_type_id__model=model_name, object_id=object_id)
        if self.request.POST:
            context['comment_form'] = CommentForm(self.request.POST)
            context['reply_form'] = ReplyForm(self.request.POST)
        else:
            context['comment_form'] = CommentForm()
            context['reply_form'] = ReplyForm()
        return context