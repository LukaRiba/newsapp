from django.views.generic import DetailView

from comments.views import CommentsContextMixin
from my_newsapp.models import Article
 
# View for displaying comments (_testing.html includes comments/base.html) of corresponding comments owner object
# Article instances are used as comments owners
class CommentsOwnerView(CommentsContextMixin, DetailView):
    template_name = 'comments/test_templates/_testing.html'
    model = Article # comments owner
    pk_url_kwarg = 'id' # as default is 'pk'

    def get(self, request, *args, **kwargs):
        self.request.session['comments_owner_model_name'] = self.model.__name__
        self.request.session['comments_owner_id'] = self.kwargs['id']
        return super(CommentsOwnerView, self).get(request, *args, **kwargs)