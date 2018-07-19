from random import shuffle
from .models import Category

# returns ids of Category instances whose status field value is None. Ovo koristim u HomeViewMixin-u gdje definiram
# context za HomeView
def get_random_status_none_categories_ids():
    list = []
    for category in Category.objects.filter(status=None):
        list.append(category.id)
    shuffle(list)
    return list