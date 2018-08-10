from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from .models import Comment
from .forms import CommentForm, ReplyForm
from my_newsapp.models import Article

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

def comments(request):
    context = {}
    context['comments'] = Comment.objects.all()
    if request.POST:
        context['comment_form'] = CommentForm(request.POST)
        context['reply_form'] = ReplyForm(request.POST)
    else:
        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm()
    return render(request, 'comments/comments_base.html', context)

# dodati dekoratore za if request.method == POST, if request.is_ajax()
def add_comment(request):
    if request.method == 'POST':
        print('POST data: ', request.POST)
        form = CommentForm(request.POST)
        if form.is_valid() and request.is_ajax():
            form.save(commit=False)
            form.instance.author = request.user
            form.instance.content_type_id = ContentType.objects.get(model='article').id
            form.instance.object_id = Article.objects.get(id=1).id
            form.save()
            return render(request, 'comments/comments.html', {'comments': Comment.objects.all()[0:1]})
        



def add_reply(request):
    pass