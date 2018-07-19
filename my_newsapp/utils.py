from random import shuffle
from .models import Category

# returns ids of Category instances whose status field value is None. Ovo koristim u HomeViewMixin-u gdje definiram
# context za HomeView
def get_status_none_categories_random_ids():
    ids = []
    for category in Category.objects.filter(status=None):
        ids.append(category.id)
    shuffle(ids)
    return ids