from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest

from .models import Comment
from .forms import CommentForm, ReplyForm, EditForm
from .decorators import require_ajax

class CommentsContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(
            content_type=ContentType.objects.get(model=self.model.__name__),
            object_id=self.kwargs['id'] 
        )
        data = {
            'comments': comments,
            'owner_id': self.kwargs['id'],
            'owner_model': self.model.__name__,
            'comment_form': CommentForm(),
            'reply_form': ReplyForm(),
            'edit_form': EditForm(),
            'login_url': settings.LOGIN_URL
            }
        context.update(data)
        return context

def get_owner_content_type(request):
    return ContentType.objects.get(model=request.session['comments_owner_model_name'])

@login_required
@require_POST
@require_ajax
def create_comment(request):
    form = CommentForm(request.POST)
    if form.is_valid():
        save_comment_form(request, form)
        context = {
            # Returns created comment in one-element QuerySet (itterable object is required because template 
            # uses forloop tag). First comment in QuerySet is just created one, because of ordering = ['-pub_date'].
            'comments': Comment.objects.all()[0:1],
            'reply_form': ReplyForm(),
            'edit_form': EditForm()
            }
        return render(request, 'comments/comments.html', context)

def save_comment_form(request, form):
    form.save(commit=False)
    form.instance.author = request.user
    form.instance.content_type_id = ContentType.objects.get(model=request.POST['owner_model']).id
    form.instance.object_id = request.POST['owner_id']
    form.save()

@login_required
@require_POST
@require_ajax
def create_reply(request):
    form = ReplyForm(request.POST)
    parent_id = request.POST.get('parentId')
    if form.is_valid():
        save_reply_form(request, form, parent_id)
        context = {
            'reply': Comment.objects.latest('pub_date'),
            'edit_form': EditForm(),
            'create_reply': True  # bool for check in template
            } 
        return render(request, 'comments/replies.html', context)

def save_reply_form(request, form, parent_id):
    form.save(commit=False)
    form.instance.author = request.user
    form.instance.content_type_id = ContentType.objects.get(model='comment').id
    form.instance.object_id = form.instance.parent_id = parent_id
    form.save()

@login_required
@require_POST
@require_ajax
def edit(request, pk):
    target = get_object_or_404(Comment, pk=pk)
    form = EditForm(request.POST)
    if form.is_valid():
        target.text = form.cleaned_data['text']
        target.save()
        return HttpResponse(target.text)
        
@login_required
@require_POST
@require_ajax
def delete(request, pk):
    target = get_object_or_404(Comment, pk=pk)
    target.delete()
    return HttpResponse(status=204)

@require_ajax
def load_more_comments(request):
    last_visible = request.GET.get('lastVisibleCommentId')
    comments_to_load = int(request.GET.get('numOfCommentsToLoad'))
    comments_owner_id = request.GET.get('owner_id')
    # How much more comments is in database 
    remaining_comments = Comment.objects.filter(id__lt=last_visible, object_id=comments_owner_id)
    if remaining_comments.exists():
        context = {
            'load_more': True, # bool for check in template
            'next_comments': get_next_comments(remaining_comments, comments_to_load),
            'reply_form': ReplyForm(),
            'edit_form': EditForm()
            }
        return render(request, 'comments/comments.html', context)
    return HttpResponseBadRequest() # same as HttpResponse(status=400)
    
def get_next_comments(remaining_comments, comments_to_load):
    if remaining_comments.count() >= comments_to_load:
        return remaining_comments[:comments_to_load]
    return remaining_comments