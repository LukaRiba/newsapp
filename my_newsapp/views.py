from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Article, Category
from .utils import get_random_status_none_categories_ids
from .forms import ArticleForm, ImageFormSet

# defines context used by navigation which has to be shared between views
class NavigationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

#comment
    # Komentar se odnosi na prijašnju implementaciju - pobledati prijašnje commit-e
    # Zanimljivo je da kada sam isto ovo definirao unutar get_context_data() metode
    # HomeView-a, prymary_category i secondary_category objekti nisu mogli biti učitani unutar template-a -
    # kod if statement-a   {% if primary_category %} , iako je postojao Category instanca sa statusom 'P',
    # if bi uvijek vraćao false ?? Čak i ako bi koristio filter() umjesto get() i onda u templateu
    # {% if prymary_category.exists() %} ili {% if primary_category.all %}, uvijek false ??? Nakon što sam istu stvar definirao u 
    # get_context_data() metodi u Mixin-u, kojeg sam onda proslijedio HomeView-u, {% if primary_category %} u templateu RADI ??!!
#endcomment
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
#endcomment
class HomeViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        rand_ids = get_random_status_none_categories_ids()

        if Category.objects.filter(status='P').exists():
            if Category.objects.filter(status='S').exists():
                context['primary_category'] = Category.objects.get(status='P')
                context['secondary_category'] = Category.objects.get(status='S')
                context['other_articles'] =  Article.objects.filter(category__status=None).order_by('?')
            else:
                context['primary_category'] = Category.objects.get(status='P')
                context['secondary_category'] = Category.objects.get(id=rand_ids.pop())
                context['other_articles'] =  Article.objects.filter(category__pk__in=rand_ids).order_by('?')
        else:
            context['primary_category'] = Category.objects.get(id=rand_ids.pop())
            context['secondary_category'] = Category.objects.get(id=rand_ids.pop())
            context['other_articles'] =  Article.objects.filter(category__pk__in=rand_ids).order_by('?')
        return context

class HomeView(NavigationContextMixin, HomeViewMixin, TemplateView):
    template_name = 'my_newsapp/home.html'

#comment
    # Rješenje za korištenje 2 queriset-a u ListView-u: 
    # !!! U MEĐUVREMENU SAM PRIMJENIO GORE DEFINIRANI MIXIN ZA RJEŠENJE TOG PROBLEMA, POGLEDAJ NA KRAJU KOMENTARA
    # KAKO JE OVAJ VIEW (PRIJE SE ZVAO HOMEVIEW) IZGLEDAO - KORISTIO JE 2 QUERYSETA BEZ EXTENDANJA MIXIN-A !!!
    #    ListView MORA imati svoj queryset - definiramo get_queryset() metodu koja će vratiti
    #    taj glavni queryset, bez kojeg ListView ne radi.
    #    Sada, overrideamo get_context_data(), gdje u dictionary context dodamo što god želimo, u ovom slučaju 
    #    queryset Category modela, i dodamo naš glavni queryset pozivom get_queryset() metode.
    #    Sada u template-u jednostavno pristupamo queryset-ovima: {% for category in categories %} , tj. 
    #    {% for article in articles %}. 'categories' i 'articles' su key-evi context dictionary-a koje smo definirali
    #    u get_context_data
    #           
    #           class HomeView(generic.ListView):
    #           template_name = 'my_newsapp/home.html'
    #
    #           def get_queryset(self):
    #               return Article.objects.all()
    #
    #           def get_context_data(self, *args, **kwargs):
    #               context = super(HomeView, self).get_context_data(*args, **kwargs)
    #               context['categories'] = Category.objects.all()
    #               context['articles'] = self.get_queryset()
    #               return context
    #endcomment
class LatestArticlesView(NavigationContextMixin, ListView):

    template_name = 'my_newsapp/latest_articles.html'
    context_object_name = 'articles'
    model = Article
    paginate_by = 5

class CategoryView(NavigationContextMixin, ListView):
    template_name = 'my_newsapp/category.html'
    context_object_name = 'articles'
    paginate_by = 2

    def get_queryset(self):
        # gett-a Category instancu na temelju slug-a u url-u i vraća QuerySet artikala iz te kategorije
        category = Category.objects.get(slug=self.kwargs['slug'])
        return category.articles.all()

class ArticleDetailView(NavigationContextMixin, DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article

class CreateArticleView(NavigationContextMixin, LoginRequiredMixin, CreateView):
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
    #endcomment
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formset = ImageFormSet()
        return render(request, self.template_name, {'form': form, 'image_formset': formset})

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        formset = ImageFormSet(data=request.POST, files=request.FILES)
        
        if  form.is_valid and formset.is_valid():
            # Set current user as article author
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

        return render(request, self.template_name, {'form': form, 'image_formset': formset})