from django.views.generic.list import ListView
 
from .models import  Article

class HomeView(ListView):
    context_object_name = "article_list"
    template_name = 'my_newsapp/home.html'

    def get_queryset(self):
        return Article.objects.all().order_by('-pub_date')

        
    

