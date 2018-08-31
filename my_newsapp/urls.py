from django.conf.urls import url
#from django.contrib.auth import views as auth_views

from . import views

app_name = 'my_newsapp'

# Tablica regex-a : https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views
urlpatterns = [
    url(r'^login/$', views.MyNewsLoginView.as_view(), name='login'),
    url(r'^logout/$', views.MyNewsLogoutView.as_view(), name='logout'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^latest-articles/$', views.LatestArticlesView.as_view(), name='latest-articles'),
    url(r'^create-article/$', views.CreateArticleView.as_view(), name='create-article'),
    url(r'^(?P<slug>[-\w]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^(?P<category>[\w-]+)/(?P<id>\d+)/(?P<slug>[\w-]+)/$', views.ArticleDetailView.as_view(), name='article-detail')
]