from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from autoslug import AutoSlugField

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='title') 

    #comment
    # metoda za dohvaćanje url-a. U urls.py smo url pattern-u arg name definirali jao 'category': 
    #   url(r'^(?P<slug>[-\w]+)/$', views.CategoryView.as_view(), name='category'),
    # Sada, metoda reverse iz tog pattern-a generira url, te u kwargs sprema dict sprema slug, koji je jednak slug-u iz url patterna -
    # dakle slugu instance kategorije: biology, history itd. Sada, u CategoryView-u pristupamo tom slug-u sa   self.kwargs['slug'], kojeg
    # spremamo u varijablu koju koristimo za filtraciju Article instanci, i tako dobivamo articlese samo za određenu kategoriju
    #endcomment
    def get_absolute_url(self):
        return reverse('my_newsapp:category', kwargs={'slug': self.slug})   

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='title')
    text = models.TextField()
    short_description = models.TextField(max_length=300)
    image = models.ImageField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='articles', on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('my_newsapp:article-detail', kwargs={'category': self.category.slug, 'slug': self.slug})

    def __str__(self):
        return self.title



    
