from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import FileExtensionValidator
from django.conf import settings

from autoslug import AutoSlugField

from comments.models import Comment

CATEGORY_RELEVANCE_CHOICES = (
    ('P', 'Primary'),
    ('S', 'Secondary'),
)

class CategoriesQuerySet(models.QuerySet):
    def has_primary(self):
        return self.filter(status='P').exists()

    def get_primary(self):
        return self.get(status='P')

    def has_secondary(self):
        return self.filter(status='S').exists()
    
    def get_secondary(self):
        return self.get(status='S')

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, unique=True, populate_from='title') 
    image = models.ImageField()
    status = models.CharField(max_length=1, choices=CATEGORY_RELEVANCE_CHOICES, unique=True, blank=True, null=True)

    objects = CategoriesQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('my_newsapp:category', kwargs={'slug': self.slug})   

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(null=True, default=None, populate_from='title')
    text = models.TextField()
    short_description = models.TextField(max_length=300)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='articles', on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE)
    comments = GenericRelation(Comment)

    def get_absolute_url(self):
        return reverse(
            'my_newsapp:article-detail', 
            kwargs={'category': self.category.slug,'id':self.id, 'slug': self.slug}
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-pub_date']

class Image(models.Model):
    image = models.ImageField(
        validators=[FileExtensionValidator(['bmp', 'gif', 'png', 'jpg', 'jpeg'])], 
        blank=True, 
        null=True
    )
    description = models.CharField(max_length=200, blank=True, null=True)
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.image}' 

class File(models.Model):
    file = models.FileField(
        upload_to='files/', 
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'])],  
        blank=True, 
        null=True
    )                            
    article = models.ForeignKey(Article, related_name='files', on_delete=models.CASCADE)

    CONTENT_TYPE_ICON_PAIRS = (
        ('application/pdf', 'pdf.png'),
        ('application/zip', 'zip.jpg'),
        ('application/msword', 'doc_docx.png'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'doc_docx.png'),
        ('application/vnd.ms-powerpoint', 'ppt_pptx.png'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'ppt_pptx.png'),
        ('application/vnd.ms-excel', 'xls_xlsx.png'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xls_xlsx.png'),
    )

    def get_type_icon(self):
        for pair in self.CONTENT_TYPE_ICON_PAIRS:
            content_type, icon = pair
            if content_type == self.content_type():
                return f'my_newsapp/file_type_icons/{icon}'

    def content_type(self):
        from magic import Magic
        mime = Magic(mime=True)
        return mime.from_file(self.path())

    def path(self):
        return f'{settings.MEDIA_ROOT}{str(self.file)}'

    def name(self):
        return self.__str__()

    def __str__(self):
        return str(self.file).split('/')[-1]