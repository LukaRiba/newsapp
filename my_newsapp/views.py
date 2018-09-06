from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .models import Article, Category
from .utils import get_status_none_categories_random_ids
from .forms import ArticleForm, ImageFormSet, LoginForm

from comments.views import CommentsContextMixin

# defines context used by navigation which has to be shared between views
class NavigationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class HomeViewMixin:
    categories = Category.objects.all()

    def get_context_data(self, *args, **kwargs):
        rand_ids = get_status_none_categories_random_ids()
        context = super().get_context_data(*args, **kwargs)
        home_context = {
            'primary_category': self.get_primary_category(rand_ids),
            'secondary_category': self.get_secondary_category(rand_ids),
            'other_articles': self.get_other_articles(rand_ids)
        }
        context.update(home_context)
        return context

    def get_primary_category(self, rand_ids):
        if self.categories.has_primary():
            return self.categories.get_primary()
        return self.categories.get(id=rand_ids.pop())

    def get_secondary_category(self, rand_ids):
        if self.categories.has_primary() and self.categories.has_secondary():
            return self.categories.get_secondary()
        return self.categories.get(id=rand_ids.pop())

    def get_other_articles(self, rand_ids):
        return Article.objects.filter(category__pk__in=rand_ids)[:5]
        
class HomeView(NavigationContextMixin, HomeViewMixin, TemplateView):
    template_name = 'my_newsapp/home.html'

class LatestArticlesView(NavigationContextMixin, ListView):
    template_name = 'my_newsapp/latest_articles.html'
    context_object_name = 'articles'
    model = Article
    paginate_by = 5

class CategoryView(NavigationContextMixin, ListView):
    template_name = 'my_newsapp/category.html'
    context_object_name = 'articles'
    paginate_by = 5

    # gett-a Category instancu na temelju slug-a u url-u
    def get_category(self):
        return Category.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return self.get_category().articles.all()

# comment
    # obavezno dekorirati metodu dispatch sa never_cache -> bez ovoga, browser sprema posjećene ArticleDetail stranice
    # u cache, te ih učitava iz cache-a ukoliko im pristupimo tako da stisnemo BACK ili FORWARD button na browseru.
    # To znači da se stranica ne load-a sa servera i samim time ne pokreće se dispatch() metoda, koja poziva get(). 
    # To znači da se request.session['comments_owner_id'] ne update-a, dakle vratili smo se na stranicu
    # article-a čiji je id npr 13, a request.session['comments_owner_id'] je ostao 25, od zadnje loadane stranice.
    # Zbog toga, ako kliknemo 'Load 10 more comments' button, ovaj će poslati ajax request load_more_comments funkciji
    # iz comments.views, koja će vratiti 10 komentara za article čiji je id 25, ali mi se nalazimo na stranici od
    # articlea čiji je id 13!! never_cache decorator osigurava da browser  ArticleDetail stranicu nikad ne sprema u 
    # cache, tako da kada kliknemo na BACK ili FORWARD button u browser-u, i promijenimo ArticleDetail stranicu, 
    # ona se mora uvijek učitati sa servera, i tako update-ati request.session['comments_owner_id']!.
    # Isto se moglo riješiti i na drugi način, tako da u urls.py, tako da as_view() metodu wrappamo u dekorator:
    #       from django.views.decorators.cache import never_cache
    #
    #       urlpatterns = [
    #       ...
    #       url(r'^(?P<category>[\w-]+)/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
    #           never_cache(views.ArticleDetailView.as_view()), name='article-detail')
    #       ...
    #      ]
@method_decorator(never_cache, name='dispatch')
class ArticleDetailView(NavigationContextMixin, CommentsContextMixin, DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article
    
    # Set href attribute of 'Login' anchor tag which is displayed instead comments if user is not logged in
    # This attribute is defined in comments.views.CommentsContextMixin
    login_url = '/news/login'
    # Override to add these variables to request.session, required for comments app
    def get(self, request, *args, **kwargs):
        self.request.session['comments_owner_model_name'] = self.model.__name__
        self.request.session['comments_owner_id'] = self.kwargs['id']
        return super(ArticleDetailView, self).get(request, *args, **kwargs)

class CreateArticleView(LoginRequiredMixin, NavigationContextMixin, CreateView):
    template_name = 'my_newsapp/create_article.html'
    form_class = ArticleForm
    success_msg = 'You created a new Article'
    login_url = 'my_newsapp:login'

    def get_context_data(self, **kwargs):
        context = super(CreateArticleView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['image_formset'] = ImageFormSet()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if  form.is_valid and formset.is_valid():
            form.save(commit=False)
            form.instance.author = self.request.user
            formset.instance = form.save()
            formset.save()    
            messages.info(self.request, self.success_msg)
            return HttpResponseRedirect(form.instance.get_absolute_url())
        return super(CreateArticleView, self).get(request, *args, **kwargs)

class MyNewsLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'my_newsapp/login.html'
    redirect_authenticated_user = True 

class MyNewsLogoutView(auth_views.LogoutView):
    next_page = 'my_newsapp:login'

