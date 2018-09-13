"""my_news URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^news/', include('my_newsapp.urls')),
    url(r'^comments/', include('comments.urls')),
]

#comment
    # Za uploadane fileove - media - moramo definirati url na ovaj način; + dodamo if statement za DEBUG 
    # https://docs.djangoproject.com/en/2.0/howto/static-files/#serving-files-uploaded-by-a-user-during-development
    # https://stackoverflow.com/questions/49096239/django-imagefield-not-uploading-the-image?rq=1
    # dobro objašnjeno: https://overiq.com/django/1.10/handling-media-files-in-django/
if settings.DEBUG:
    import debug_toolbar
    # because url() instances must be in one list
    urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
    # we add static after list
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    print(urlpatterns)

