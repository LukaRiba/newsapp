"""this URL Configuration is used only for comments app testing"""

from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

from .views import CommentsOwnerView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^owner/(?P<id>\d+)/comments/$', CommentsOwnerView.as_view(), name='comments-test'),
    url(r'^comments/', include('comments.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    # because url() instances must be in one list
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns


