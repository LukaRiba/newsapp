from django.conf.urls import url

from . import views

app_name = 'comments'

urlpatterns = [
    url(r'^create_comment/$', views.create_comment, name='create-comment'),
    url(r'^create_reply/$', views.create_reply, name='create-reply'),
    url(r'^(?P<pk>\d+)/edit/$', views.edit_comment_or_reply, name='edit'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete_comment_or_reply, name='delete')
]