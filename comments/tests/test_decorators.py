from django.test import TestCase
from django.http.request import HttpRequest
from django.core.exceptions import PermissionDenied

from comments.decorators import require_ajax

class DecoratorsTests(TestCase):

    def test_require_ajax_request_is_ajax(self):
        request = HttpRequest()
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        self.assertEqual(view_fucn(request), 'works')

    def test_require_ajax_request_NOT_ajax(self):
        request = HttpRequest()
        with self.assertRaises(PermissionDenied):        
            view_fucn(request)

@require_ajax
def view_fucn(request):
    return 'works'