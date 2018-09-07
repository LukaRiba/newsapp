from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .models import Comment
from .forms import CommentForm, ReplyForm, EditForm
from .decorators import require_ajax

class CommentsContextMixin:
    login_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(object_id=self.request.session['comments_owner_id'])
        data = {
            'comments': comments,
            'comment_form': CommentForm(),
            'reply_form': ReplyForm(),
            'edit_form': EditForm(),
            'login_url': self.login_url
            }
        context.update(data)
        return context

@login_required
@require_POST
@require_ajax
def create_comment(request):    
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.instance.content_type_id = ContentType.objects.get(
            model=request.session['comments_owner_model_name']).id
        form.instance.object_id = request.session['comments_owner_id']
        form.save()
        context = {
            # Returns created comment in an one-element QuerySet (itterable object is required because template 
            # uses forloop tag). First comment in QuerySet is just created one, because of ordering = ['-pub_date'].
            # Probably not good solution because it all() on possibly large db table. Maybe is better with filter()
            # against pub_date - Comment.objects.filter(pub_date__lte=timezone.now() - timezone.timedelta(minutes=1) ?
            'comments': Comment.objects.all()[0:1],
            'reply_form': ReplyForm(),
            'edit_form': EditForm()
            }
        return render(request, 'comments/comments.html', context)

@login_required
@require_POST
@require_ajax
def create_reply(request):
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
            'edit_form': EditForm(),
            'create_reply': True  # bool for check in template
            } 
        return render(request, 'comments/replies.html', context)

@login_required
@require_POST
@require_ajax
def edit_comment_or_reply(request, pk):
    target = get_object_or_404(Comment, pk=pk)
    form = EditForm(request.POST)
    if form.is_valid():
        target.text = form.cleaned_data['text']
        target.save()
        return HttpResponse(target.text)
        
@login_required
@require_POST
@require_ajax
def delete_comment_or_reply(request, pk):
    target = get_object_or_404(Comment, pk=pk)
    target.delete()
    if target.is_reply():
        return HttpResponse('<div><br><p style="color: rgb(124, 0, 0)"><strong>Reply deleted</strong></p></div>')
    return HttpResponse('<div><br><p style="color: rgb(124, 0, 0)"><strong>Comment deleted</strong></p></div>')

@require_ajax
def load_more_comments(request):
    last_visible = request.GET.get('lastVisibleCommentId')
    comments_owner_id = request.session['comments_owner_id']
    remaining_comments = Comment.objects.filter(id__lt=last_visible, object_id=comments_owner_id)
    if remaining_comments.count() >= 10:
        next_comments = remaining_comments[:10]
    else:
        next_comments = remaining_comments
    context = {
        'load_more': True, # bool for check in template
        'next_comments': next_comments,
        'reply_form': ReplyForm(),
        'edit_form': EditForm()
        }
    return render(request, 'comments/comments.html', context)
    
    