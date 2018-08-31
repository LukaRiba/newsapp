from django.conf.urls import url

from . import views

app_name = 'comments'

urlpatterns = [
    url(r'^add_comment/$', views.add_comment, name='add-comment'),
    url(r'^add_reply/$', views.add_reply, name='add-reply'),
    url(r'^(?P<pk>\d+)/delete/$', views.delete_comment_or_reply, name='delete')
]