import os

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Article, Category, File
from .utils import get_status_none_categories_random_ids
from .forms import ArticleForm, ImageFormSet, FileFormSet, LoginForm
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
        return self.categories.get(id=rand_ids.pop()) if rand_ids else None

    def get_secondary_category(self, rand_ids):
        if self.categories.has_secondary():
            return self.categories.get_secondary()
        return self.categories.get(id=rand_ids.pop()) if rand_ids else None

    # returns empty QuerySet if there are no articles in category, or no rand_ids (no category)
    def get_other_articles(self, rand_ids):
        other_articles = Article.objects.filter(category__pk__in=rand_ids)
        if other_articles.count() < 6:
            return other_articles
        else:
            return other_articles[:6]

class FormsetsContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context.update({
                'image_formset': ImageFormSet(self.request.POST, self.request.FILES),
                'file_formset': FileFormSet(self.request.POST, self.request.FILES)
            })
        else:
            context.update({
                'image_formset': ImageFormSet(),
                'file_formset': FileFormSet()
            })
        return context

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

@method_decorator(never_cache, name='dispatch')
class ArticleDetailView(NavigationContextMixin, CommentsContextMixin, DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article

class CreateArticleView(LoginRequiredMixin, NavigationContextMixin, FormsetsContextMixin, CreateView):
    template_name = 'my_newsapp/create_article.html'
    form_class = ArticleForm
    success_msg = 'You created a new Article'
    login_url = 'my_newsapp:login'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES)
        file_formset = FileFormSet(request.POST, request.FILES)

        if self.are_valid(form, image_formset, file_formset):
            self.create_article(request, form, image_formset, file_formset)
            messages.info(self.request, self.success_msg)
            return HttpResponseRedirect(form.instance.get_absolute_url())
        return super(CreateArticleView, self).get(request, *args, **kwargs)

    def are_valid(self, *forms):
        return all([form.is_valid() for form in forms])

    def create_article(self, request, form, image_formset, file_formset):
        form.save(commit=False)
        form.instance.author = self.request.user
        image_formset.instance = file_formset.instance = form.save()
        image_formset.save()
        file_formset.save()

class EditArticleView(LoginRequiredMixin, NavigationContextMixin, FormsetsContextMixin, UpdateView):
    template_name = 'my_newsapp/edit_article.html'
    form_class = ArticleForm
    model = Article
    success_msg = 'Article updated'
    login_url = 'my_newsapp:login'

    def get_context_data(self, **kwargs):
        context = super(EditArticleView, self).get_context_data(**kwargs)
        context['image_formset'].instance = self.get_object()
        context['image_formset'].selected_images = self.request.POST.getlist('image-checkbox[]')
        return context

    def get_object(self, queryset=None):
        return Article.objects.get(id=self.kwargs['id'])

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        form = self.form_class(request.POST, instance=instance)
        image_formset = ImageFormSet(request.POST, request.FILES, instance=instance, request=request)
        file_formset = FileFormSet(request.POST, request.FILES, instance=instance)

        if self.are_valid(form, image_formset, file_formset):
            self.delete_selected_files_and_images(request)
            self.update_article(form, image_formset, file_formset)
            messages.info(self.request, self.success_msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        return super(EditArticleView, self).get(request, *args, **kwargs)

    def are_valid(self, *forms):
        return all([form.is_valid() for form in forms])

    def delete_selected_files_and_images(self, request):
        image_ids = request.POST.getlist('image-checkbox[]')
        file_ids = request.POST.getlist('file-checkbox[]')
        self.get_object().images.filter(pk__in=image_ids).delete()
        self.get_object().files.filter(pk__in=file_ids).delete()

    def update_article(self, *forms):
        for form in forms:
            form.save()


@method_decorator(require_http_methods(['POST']), name='dispatch')
class DeleteArticleView(LoginRequiredMixin, DeleteView):
    model = Article
    pk_url_kwarg = 'id'
    login_url = 'my_newsapp:login'
    success_url = reverse_lazy('my_newsapp:home')

class MyNewsLoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'my_newsapp/login.html'
    redirect_authenticated_user = True

class MyNewsLogoutView(auth_views.LogoutView):
    next_page = 'my_newsapp:login'

def download_file(request, id):
    target = get_object_or_404(File, id=id)
    file_path = os.path.join(target.path())
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=target.content_type())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


class ExportToXLSXView(View):
    # function for exporting data to xlsx file
    def export_to_xlsx(self, queryset, fields, filename):
        return export_xlsx(queryset, fields, filename)
