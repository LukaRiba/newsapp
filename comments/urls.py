from django.conf.urls import url

from . import views

app_name = 'comments'

urlpatterns = [
    url(r'^create-comment/$', views.create_comment, name='create-comment'),
    url(r'^create-reply/$', views.create_reply, name='create-reply'),
    url(r'^(?P<pk>\d+)/edit/$', views.edit, name='edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),
    url(r'^load-more-comments/$', views.load_more_comments, name='load-more-comments'),
]