from django.contrib import admin

from .models import Category, Article, Image, File

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Image)
admin.site.register(File)
