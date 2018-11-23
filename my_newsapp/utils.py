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
    file_path = f'{get_test_files_dir_path()}{filename}'
    with open(file_path, 'rb') as file: # 'rb' because SimpleUploadedFile requires bytes-like object, not 'str'
        return SimpleUploadedFile(file.name, file.read(), content_type=content_type(file_path))

def get_test_files_dir_path():
    return os.path.join(settings.BASE_DIR, 'my_newsapp/tests/test_files/')

def content_type(file_path):
    from magic import Magic
    mime = Magic(mime=True)
    return mime.from_file(file_path)

def field_values(instance):
    field_names = [field.name for field in instance._meta.get_fields()]
    values = [str(getattr(instance, field_name).all()) if # str() forces evaluation of QuerySet.
                type(instance._meta.get_field(field_name)).__name__ in ('ManyToOneRel', 'GenericRelation')
              else getattr(instance, field_name) for field_name in field_names]
    return dict(zip(field_names, values)) 