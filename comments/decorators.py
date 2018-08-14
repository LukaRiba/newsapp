from django.core.exceptions import PermissionDenied

def require_ajax(view):
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return view(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrapper.__doc__ = view.__doc__
    wrapper.__name__ = view.__name__
    return wrapper

# def override(method):
#      def wrapper(request, *args, **kwargs):
#         if request.is_ajax():
#             return view(request, *args, **kwargs)
#         else:
#             raise PermissionDenied
#     wrapper.__doc__ = view.__doc__
#     wrapper.__name__ = view.__name__
#     return wrapper