from django.views import generic
 
from .models import  Article, Category

# defines context used by navigation which has to be shared between views
class NavigationContextMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


#comment
    # Rješenje za korištenje 2 queriset-a u ListView-u:
    #    ListView MORA imati svoj queryset - definiramo get_queryset() metodu koja će vratiti
    #    taj glavni queryset, bez kojeg ListView ne radi.
    #    Sada, overrideamo get_context_data(), gdje u dictionary context dodamo što god želimo, u ovom slučaju 
    #    queryset Category modela, i dodamo naš glavni queryset pozivom get_queryset() metode.
    #    Sada u template-u jednostavno pristupamo queryset-ovima: {% for category in categories %} , tj. 
    #    {% for article in articles %}. 'categories' i 'articles' su key-evi context dictionary-a koje smo definirali
    #    u get_context_data
#endcomment
class HomeView(NavigationContextMixin, generic.ListView):
    template_name = 'my_newsapp/home.html'
    
    def get_queryset(self):
        return Article.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        # context['categories'] = Category.objects.all()
        context['articles'] = self.get_queryset()
        return context

class CategoryView(NavigationContextMixin, generic.ListView):
    template_name = 'my_newsapp/category.html'
    context_object_name = 'category'
    
    # gett-a Category instancu na temelju slug-a u url-u
    def get_queryset(self):
        return Category.objects.get(slug=self.kwargs['slug']) 

   

class ArticleListView(NavigationContextMixin, generic.ListView):
    template_name = ''
    
    def get_queryset(self):
        return 9


class ArticleDetailView(NavigationContextMixin, generic.DetailView):
    template_name = 'my_newsapp/detail.html'
    model = Article
    



    
    

