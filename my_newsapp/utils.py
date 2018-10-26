import os
from random import shuffle

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from .models import Category

# returns ids of Category instances whose status field value is None. Ovo koristim u HomeViewMixin-u gdje definiram
# context za HomeView
def get_status_none_categories_random_ids():
    ids = []
    for category in Category.objects.filter(status=None):
        ids.append(category.id)
    shuffle(ids)
    return ids

def get_test_file(filename):
    file = open(os.path.join(settings.BASE_DIR, 'my_newsapp/tests/test_files/', filename), 'rb')
    return SimpleUploadedFile(file.name, file.read())

# returns a dictionary with model field names as keys, and with field values as values (all strings).
def field_values(instance):
    field_names = [field.name for field in instance._meta.get_fields()]
    # comment
        # 1.   For relational fields (images, files or comments - istances of models whose fk is Article model)
        #      getattr(self.article, field) returns RelatedManager object, so we have to add if statement for
        #      that fields to call all() method on getattr(self.article, field), which then returns QuerySet of
        #      related model instances.  
        # 2.   Without using str() method on getattr(instance, field).all(), image which is uploaded through self.client.post() 
        #      will be listed in self.initial_values too. Thats because getattr(instance, field).all() returns queryset
        #      which is lazy evaluated, so it is evaluated only when we use self.initial_values in assertions, which come after
        #      client.post - so, self.initial_values will contain valuues of updated article instead values before updateing!     
        #      With using str() on getattr(instance, field).all(),  evaluation is forced here in this method, which is called in setUp():
        #           self.initial_values = field_values(self.article)
        #      Then, after client.post(), we once more run this method with updated_article (we could run it on self.article,
        #      as it is updated now, but this way is cleaner), and now, new values are saved. Then we compare keys from
        #      from self.initial_values and field_values(updated_article) dictinonaries in our assertions.  
        #      One more thing about str() - if we dont use str() on getattr(instance, field).all(), initial and updated querysets
        #      will contain newly uploaded image because of lazy evaluation - but the test will pass ! That's because, even if 
        #      both querysets have exactly same image objects, they are not equal objects:
        #           q1 == q2   ->   False,
        #      but  str(q1) == str(q2)    or    list(q1) == list(q2)    -> True
        #      So, test now passes as it should, because, 1. queryset evaluation is forced, so self.initial_values 
        #      don't contain uploaded image, and querysets are now actually not equal (2 vs 3 images).
    values = [str(getattr(instance, field_name).all()) if # str() forces evaluation of QuerySet.
              str(instance._meta.get_field(field_name).__class__) in ( # str() for comparing to be possible.
                  "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                  "<class 'django.contrib.contenttypes.fields.GenericRelation'>"
              ) 
              else getattr(instance, field_name) for field_name in field_names]
    return dict(zip(field_names, values)) 