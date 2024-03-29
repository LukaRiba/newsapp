from django.conf.urls import url

from . import views

app_name = 'my_newsapp'

urlpatterns = [
    url(r'^login/$', views.MyNewsLoginView.as_view(), name='login'),
    url(r'^logout/$', views.MyNewsLogoutView.as_view(), name='logout'),
    url(r'^latest-articles/$', views.LatestArticlesView.as_view(), name='latest-articles'),
    url(r'^create-article/$', views.CreateArticleView.as_view(), name='create-article'),
    url(r'^(?P<slug>[-\w]+)/$', views.CategoryView.as_view(), name='category'),
    url(r'^(?P<category>[\w-]+)/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        views.ArticleDetailView.as_view(), name='article-detail'),
    url(r'^edit-article/(?P<id>\d+)/$', views.EditArticleView.as_view(), name='edit-article'),
    url(r'^download-file/(?P<id>\d+)/$', views.download_file, name='download-file'),
    url(r'^delete-article/(?P<id>\d+)/$', views.DeleteArticleView.as_view(), name='delete-article'),
    url(r'^export-article/(?P<id>\d+)/$', views.ExportToXLSX.as_view(), name='export-article'),
    url(r'^$', views.HomeView.as_view(), name='home'),
]
