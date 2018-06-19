from django.views import generic
 
from .models import  Article, Category

# defines context used by navigation which has to be shared between views
class NavigationContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

#comment
    # Zanimljivo je da kada sam isto ovo definirao unutar get_context_data() metode
    # HomeView-a, prymary_category i secondary_category objekti nisu mogli biti učitani unutar template-a -
    # kod if statement-a   {% if primary_category %} , iako je postojao Category instanca sa statusom 'P',
    # if bi uvijek vraćao false ?? Čak i ako bi koristio filter() umjesto get() i onda u templateu
    # {% if prymary_category.exists() %} ili {% if primary_category.all %}, uvijek false ??? Nakon što sam istu stvar definirao u 
    # get_context_data() metodi u Mixin-u, kojeg sam onda proslijedio HomeView-u, {% if primary_category %} u templateu RADI ??!!
#endcomment
class HomeViewMixin:
     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['primary_category'] = Category.objects.get(status='P')
        context['secondary_category'] = Category.objects.get(status='S')
        return context


class HomeView(NavigationContextMixin, HomeViewMixin, generic.ListView):
    template_name = 'my_newsapp/home.html'
    context_object_name = 'rand_articles'

    def get_queryset(self):
        return Article.objects.filter(category__status=None).order_by('?')

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
class LatestArticlesView(NavigationContextMixin, generic.ListView):

    template_name = 'my_newsapp/latest_articles.html'
    context_object_name = 'articles'
    model = Article

class CategoryView(NavigationContextMixin, generic.ListView):
    template_name = 'my_newsapp/category.html'
    context_object_name = 'category'
    
    # gett-a Category instancu na temelju slug-a u url-u
    def get_queryset(self):
        return Category.objects.get(slug=self.kwargs['slug']) 

class ArticleDetailView(NavigationContextMixin, generic.DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article
