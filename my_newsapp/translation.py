from modeltranslation.translator import register, TranslationOptions
from .models import Article

@register(Article)
class CommentTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'text', 'short_description')
    description = "Article translation"
