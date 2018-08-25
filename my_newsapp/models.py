from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation

from autoslug import AutoSlugField

from comments.models import Comment

CATEGORY_RELEVANCE_CHOICES = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
)

class CategoriesQuerySet(models.QuerySet):
    def contain_instance_with_status_primary(self):
        return self.filter(status='P').exists()

    def contain_instance_with_status_secondary(self):
        return self.filter(status='S').exists()

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='title') 
    image = models.ImageField()
    status = models.CharField(max_length=1, choices=CATEGORY_RELEVANCE_CHOICES, unique=True, blank=True, null=True)

    objects = CategoriesQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'categories'

    #comment
        # metoda za dohvaćanje url-a. U urls.py smo url pattern-u argument 'name' definirali kao 'category': 
        #   url(r'^(?P<slug>[-\w]+)/$', views.CategoryView.as_view(), name='category'),
        # Sada, metoda reverse iz tog pattern-a generira url, te u kwargs dict sprema slug, koji je jednak slug-u iz url patterna -
        # dakle slug-u instance kategorije: biology, history itd. Sada, u CategoryView-u pristupamo tom slug-u sa self.kwargs['slug'], 
        # pomoću kojeg gettamo tu Category instancu:  Category.objects.get(slug=self.kwargs['slug'])
    def get_absolute_url(self):
        return reverse('my_newsapp:category', kwargs={'slug': self.slug})   

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='title')
    text = models.TextField()
    short_description = models.TextField(max_length=300)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='articles', on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE)
    comments = GenericRelation(Comment)

    def get_absolute_url(self):
        return reverse('my_newsapp:article-detail', kwargs={'category': self.category.slug,'id':self.id, 'slug': self.slug})

    def __str__(self):
        return self.title

    #comment
        # Ovime osiguravamo da su Articles u querysetu uvijek poredani tako da je prvi u setu onaj najrecentniji
        # Sada ne moramo to raditi prilikom gettanja queryseta, npr. Article.objects.all().order_by('-pub_date') i
        # ovakav poredak će biti default za sve Article querysetove
    class Meta:
        ordering = ['-pub_date']

class Image(models.Model):
    image = models.ImageField(blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.image


