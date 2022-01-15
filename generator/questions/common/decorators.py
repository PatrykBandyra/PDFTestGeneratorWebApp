from django.http import HttpResponseBadRequest  # pragma: no cover
from functools import wraps                     # pragma: no cover


def ajax_required(f):                           # pragma: no cover

    @wraps(f)                                   # pragma: no cover
    def wrap(request, *args, **kwargs):         # pragma: no cover
        if not request.is_ajax():               # pragma: no cover
            return HttpResponseBadRequest()     # pragma: no cover
        return f(request, *args, **kwargs)      # pragma: no cover

    return wrap                                 # pragma: no cover
