from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=100, unique=True)
    #slug = autoslug(populate_from=title)
    text = models.TextField()
    short_description = models.TextField(max_length=300)
    image = models.ImageField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, related_name='articles', on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.CASCADE)

    def __str__(self):
        return self.title



    
