from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from .models import Article, Category
from .utils import get_status_none_categories_random_ids
from .forms import ArticleForm, ImageFormSet

from comments.views import CommentsContextMixin

# defines context used by navigation which has to be shared between views
class NavigationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

#comment
    # Ovaj komentar se odnosi na prijašnju implementaciju - pobledati prijašnje commit-e
    # Zanimljivo je da kada sam isto ovo definirao unutar get_context_data() metode
    # HomeView-a, prymary_category i secondary_category objekti nisu mogli biti učitani unutar template-a -
    # kod if statement-a   {% if primary_category %} , iako je postojao Category instanca sa statusom 'P',
    # if bi uvijek vraćao false ?? Čak i ako bi koristio filter() umjesto get() i onda u templateu
    # {% if prymary_category.exists %} ili {% if primary_category.all %}, uvijek false ??? Nakon što sam istu stvar definirao u 
    # get_context_data() metodi u Mixin-u, kojeg sam onda proslijedio HomeView-u, {% if primary_category %} u templateu RADI ??!!
#comment
    # get_context_data() prvo sprema id-e Category instanci čiji je status = None u listu - redosljed je
    # svaki put randomiziran (unutar get_random_status_none_categories_ids() funkciju iz utils.py).
    # U 1. slučaju ako postoje i Primary i Secondary kategorija, njih se sprema u kontext putem status atributa ,
    # a ostale kategorije, odnosno artikle koje filtriramo iz kategorija, gett-amo isto prema statusu(u ovom slučaju None)
    # U 2. slučaju, definirana je samo Primarna kategorija - nju gettamo preko status atributa. Sada imamo id-e ostalih kategorija random,
    # i jedan moramo izabrati za secondary_category koja će na home pageu zauzimati mjesto sekundarne kategorije. Jednostavno, nju
    # gett-amo preko id argumenta kojem dodajemo vrijednost koji pop-amo iz rand_ids liste. Sada u listi više nema tog id-a, i listu
    # možemo koristiti za gettanje Article objectsa putem category__pk__in=rand_ids (možemo predati listu vrijednosti - some_attribute__in=some_list).
    # Sigurni smo da se artikli 'secondary_category' neće pojaviti među 'other_articles' pošto se id 'secondary_category' više ne nalazi u
    # rand_ids, pošto smo da pop-ali
    # U 3. slučaju nisu definirane ni P ni S kategorije, tako da sve gett-amo preko id-a iz rand_ids liste. Sada, kao i u drugom slučaju,
    # 'primary_category' nalazimo preko id-a iz rand_list kojeg pop-amo i osiguravamo da se ta kategorija ne nađe u nekom drugom kontekstu.
    # isto tako pop-amo i za 'secondary_category', te preostale id-e koristime za gett-anje ostalih kategorija čije articles-e koristimo za 'other_articles'
    # NAPOMENA : metodu get_random_status_none_categories_ids() sam prvo definirao u HomePageMixin-u i get_context_data() nije radio.
    # kada bi get_random_status_none_categories_ids() pozvao unutar get_context_data dobivao bih iznimke kod npr. id=rand_ids.pop() 
    # 'nonetype object has no attribute pop()' ili za category__pk__in=rand_ids 'nonetype object is not iterable' ili sl. Zašto? Neznam točno
class HomeViewMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        rand_ids = get_status_none_categories_random_ids()
        categories = Category.objects.all()

        if categories.contain_instance_with_status_primary():
            context['primary_category'] = categories.get(status='P')
            if categories.contain_instance_with_status_secondary():
                context['secondary_category'] = categories.get(status='S')
                context['other_articles'] =  Article.objects.filter(category__status=None)[:5]
            else:
                context['secondary_category'] = categories.get(id=rand_ids.pop())
                context['other_articles'] =  Article.objects.filter(category__pk__in=rand_ids)[:5]
        else:
            context['primary_category'] = categories.get(id=rand_ids.pop())
            context['secondary_category'] = categories.get(id=rand_ids.pop())
            context['other_articles'] =  Article.objects.filter(category__pk__in=rand_ids)[:5]
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

class ArticleDetailView(NavigationContextMixin, CommentsContextMixin, DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article
    
    # Override to add these variables to request.session, required for comments app
    def get(self, request, *args, **kwargs):
        self.request.session['comments_owner_model_name'] = self.model.__name__
        self.request.session['comments_owner_id'] = self.kwargs['id']
        return super(ArticleDetailView, self).get(request, *args, **kwargs)

class CreateArticleView(LoginRequiredMixin, NavigationContextMixin, CreateView):
    template_name = 'my_newsapp/create_article.html'
    form_class = ArticleForm
    success_msg = 'You created a new Article'

    #comment
        # <<<  When you upload a file it's passed through request.FILES, so you must also pass it to you FormSet  >>>
        # VEOMA VAŽNO - Kada forma koju koristimo u formset-u ima FileField/ImageField, moramo u slučaju POST
        # request-a prilikom inicijaliziranja FormSet objekta:
        #   ImageFormSet(self.request.POST, files=self.request.FILES)
        # uz self.request.POST moramo dodati i drugi argument, files=self.request.FILES, jer se inače slike neće
        # spremiti u memoriju, odnosno neće biti dostupne u form.cleaned_data dictionary-u (kao da input[type=file]
        # ne postoji), tj. cleaned_data će biti prazan, i shodno tome neće se spremiti u bazu.

        #'image_formset' sam definirao u get_context_data() na ovaj način, jer get() metoda superklase
        # poziva get_context_data(), i taj context koristi u template-u. Ukoliko ovo ne napravim, create_article.html
        # template nezna za formset. Mogao bih (što je i bilo prethodno rješenje), override-ati i get() metodu,
        # i returnati render(request, self.template_name, {'form': form, 'image_formset': formset}), s time da prethodno
        # definiram form = self.form_class i formset = ImageFormSet(), i isto to returnam u slučaju da ne prođe
        # uvijet u post() metodi (tj. returnam override-anu get() metodu). Problem kod ovog rješenja je to što se sada
        # iz context-a gubi 'categories' definiran u NavigationContextMixin-u, i Categories dropdown je prazan !!
        # Dakle, ovim rješenjem dodajemo 'image_context' u context tako što overrideam-o get_context_data(), i onda se
        # renderira i 'categories' i 'image_formset' (iz get_context_data()) i 'form' što je po defaultu iz
        # form_class = ArticleForm. 
        #endcomment
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
            # Save created Article instance to db and bind formset to it
            formset.instance = form.save()
            # Save Image instances (created through formset) to db
            formset.save()    
            # Show success message on created article detail view
            messages.info(self.request, self.success_msg)
            # redirect to detail view of created article
            return HttpResponseRedirect(form.instance.get_absolute_url())
        return super(CreateArticleView, self).get(request, *args, **kwargs)
