from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views

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

