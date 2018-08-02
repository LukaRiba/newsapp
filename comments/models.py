from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth.models import User

class Comment(models.Model):
    author = models.ForeignKey(User, related_name='comments', on_delete=models.DO_NOTHING)
    text = models.TextField(blank=True)
    pub_date = pub_date = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    replies = GenericRelation('self')

    def __str__(self):
        return self.text