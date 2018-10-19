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

# returns a dictionary model field names as keys, and with values as field values (all strings)
def field_values(instance):
    model = type(instance)
    field_names = [field.name for field in model._meta.get_fields()]
    # comment
        # 1.   For relational fields (images, files or comments - istances of models whose fk is Article model)
        #      getattr(self.article, field) returns RelatedManager object, so we have to add of statement for
        #      that fields to call all() method on getattr(self.article, field), which then returns QuerySet of
        #      related model instances.  
        # 2.   Without using str() method, image which is uploaded through self.client.post() will be listed in 
        #      self.initial_values too. Thats because, even if we store self.article's field values using this
        #      method in a self.initial_values before actually updateing article through self.client.post(), query methods
        #      used in here (model._meta.get_fields(), instance._meta.get_field()) are probably
        #      lazy evaluated only when we use self.initial_values, and we do it an assertions, which come after
        #      client.post - so, self.initial_values will contain valuues of updated article instead values before updateing!     
        #      With using str(), it looks like these methods are forced to evaluate when we call this method in setUp():
        #           self.initial_values = field_values(self.article)
        #      Then, after client.post(), we once more run this method with updated_article (we could run it on self.article,
        #      as it is updated now, but this way is cleaner), and now, new values are saved. Then we compare keys from
        #      from self.initial_values amd field_values(updated_article) dictinonaries in our assertions.   
    values = [str(getattr(instance, field_name).all()) if 
              str(instance._meta.get_field(field_name).__class__) in (
                  "<class 'django.contrib.contenttypes.fields.GenericRelation'>",
                  "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>"
              ) 
              else str(getattr(instance, field_name)) for field_name in field_names]
    return dict(zip(field_names, values)) 