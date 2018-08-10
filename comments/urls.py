from django.conf.urls import url

from . import views

app_name = 'comments'

# Tablica regex-a : https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views
urlpatterns = [
    url(r'^all/$', views.comments, name='comments'),
    url(r'^add_comment/$', views.add_comment, name='add-comment'),
    url(r'^add_reply/$', views.add_reply, name='add-reply'),
]