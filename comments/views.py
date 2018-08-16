from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType

from .models import Comment
from .forms import CommentForm, ReplyForm
from .decorators import require_ajax

class CommentsContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(object_id=self.request.session['comments_owner_id'])
        data = {
            'comments': comments,
            'comment_form': CommentForm(),
            'reply_form': ReplyForm()
            }
        context.update(data)
        return context

@require_POST
@require_ajax
def add_comment(request):    
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.instance.content_type_id = ContentType.objects.get(
            model=request.session['comments_owner_model_name']).id
        form.instance.object_id = request.session['comments_owner_id']
        form.save()
        context = {
            'comments': Comment.objects.all()[0:1],
             'reply_form': ReplyForm()
            }
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
        context = {
            'reply': Comment.objects.latest('pub_date'),
             'create_reply': True  # bool just for check in template
             } 
        return render(request, 'comments/replies.html', context)