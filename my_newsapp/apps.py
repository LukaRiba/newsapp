from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MyNewsappConfig(AppConfig):
    name = 'my_newsapp'
    label = "My Newsapp"
    description = _("An app for creating news articles and categories")
