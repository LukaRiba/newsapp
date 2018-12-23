from django.views.generic import DetailView

from comments.views import CommentsContextMixin
from my_newsapp.models import Article
 
# View for displaying comments (_testing.html includes comments/base.html) of corresponding comments owner object
# Article instances are used as comments owners
class CommentsOwnerView(CommentsContextMixin, DetailView):
    template_name = 'comments/test_templates/_testing.html'
    model = Article # comments owner
    pk_url_kwarg = 'id' # as default is 'pk'