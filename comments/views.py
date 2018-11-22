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

# comment
    # Prije pisanja testova, nije postojalo
    # 'content_type=ContentType.objects.get(model=self.request.session['comments_owner_model_name'])' u
    # Comment.objects.filter(). No prilikom testiranja, imao sam situaciju gdje sam u testu kreirao 1 comment i 1
    # reply, pomoću CommentFactory-ja ondosno ReplyFactory-ja. Pošto se koristi testna baza, to su bila prva 2 Comment
    # objekta (reply je Comment objekt, postoji samo Comment model) u bazi, uz 1 Article objekt kojeg sam kreirao da
    # bude comment owner. E sad, Article objekt je prvi, dakle ima id=1. Comment objekt koji je prvi kreiran ima isto
    # id=1, i njegov content_object je article, prema tome Comment-ov object_id=article.id=1. Drugi Comment objekt je
    # reply, čiji je content_object prvi Comment. Kako je id prvog commenta 1, znači da je object_id replyja (drugi
    # comment object) = 1. I evo problema, imamo 2 Comment objekta sa istim object_id-om, iako je jedan od njih reply i
    # nebi trebao proći kroz filter, međutim kako mi filtriramo sve comment objekte čiji je object_id jednak
    # articleovom, a ovdje je i replijev object_id jednak articleovomm, reply prolazi filter i postaje comment, te test
    # ne prolazi zato jer testi- da response sadrži '1 comment', a on u biti sadrži '2 comments' jer je reply prošao
    # pod comment. Zato smo dodali i provjeru content_typea - jer sada reply neće proći pošto je njegov content_type
    # 'comment', a ne 'article'.
class CommentsContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(
            content_type=get_owner_content_type(self.request),
            object_id=self.request.session['comments_owner_id']
        )
        data = {
            'comments': comments,
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
    form.instance.content_type_id = get_owner_content_type(request).id
    form.instance.object_id = request.session['comments_owner_id']
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
    comments_owner_id = request.session['comments_owner_id']
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