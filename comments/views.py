from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models import F
from django.contrib.contenttypes.models import ContentType

from .models import Comment
from .forms import CommentForm, ReplyForm
from .decorators import require_ajax
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
    context = {
        'comments': Comment.objects.filter(parent_id=None),
        'replies': Comment.objects.filter(parent_id__exact=F('object_id')),
        'comment_form': CommentForm(),
        'reply_form': ReplyForm()
    }
    return render(request, 'comments/base.html', context)

@require_POST
@require_ajax
def add_comment(request):    
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.instance.content_type_id = ContentType.objects.get(model='article').id
        form.instance.object_id = Article.objects.get(id=1).id
        form.save()
        context = {'comments': Comment.objects.all()[0:1], 'reply_form': ReplyForm()}
        return render(request, 'comments/comments.html', context)
        
@require_POST
@require_ajax
def add_reply(request):
    form = ReplyForm(request.POST)
    parent_id = request.POST.get('parentId')
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.instance.content_type_id = ContentType.objects.get(model='comment').id
        form.instance.object_id = form.instance.parent_id = parent_id
        form.save()
        context = {'reply': Comment.objects.latest('pub_date'), 'create_reply': True} # bool just for check in template
        return render(request, 'comments/replies.html', context)