from django.views import generic
 
from .models import  Article, Category

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
class HomeView(generic.ListView):
    template_name = 'my_newsapp/home.html'
    
    def get_queryset(self):
        return Article.objects.all().order_by('-pub_date')

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['categories'] = Category.objects.all()
        context['articles'] = self.get_queryset()
        return context

class CategoryView(generic.ListView):
    template_name = 'my_newsapp/category.html'
    
    def get_queryset(self):
        return Category.objects.all()

class ArticleDetailView(generic.DetailView):
    template_name = 'my_newsapp/article_detail.html'
    model = Article




    
    

