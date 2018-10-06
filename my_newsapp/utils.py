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