from django.conf.urls import url

from . import views

app_name = 'my_newsapp'

urlpatterns = [
    url(r'^home/', views.HomeView.as_view(), name='home'),
    url(r'^home/', views.CategoryView.as_view(), name='category'),
    url(r'^home/', views.ArticleDetailView.as_view(), name='article_detail')    
]