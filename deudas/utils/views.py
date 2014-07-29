"""
.. module:: utils.views
   :synopsis: Generic functions used in views.
"""

import json
import logging
import operator
import datetime
from functools import wraps

from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.template.loader import render_to_string
from django.utils.html import mark_safe
from django.db.models import Q


logger = logging.getLogger(__name__)


def encodedate(date):
    if not isinstance(date, (datetime.datetime, datetime.date)):
        raise TypeError("{0} object is not JSON-compatible".\
                            format(type(date).__name__))
    return date.isoformat()


def encodejson(t):
    return json.dumps(t, separators=(',', ':'), default=encodedate)


def renderjson(body, status, encode=None, ctype=None):
    encode = encode or encodejson
    ctype = ctype or "application/json"
    return HttpResponse(encode(body), status=status, content_type=ctype)


def service(view_fn):
    """
    Decorator for views that should return json. The decorated view
    ought to return a python dict or list with json-encodable values,
    or a tuple where the first element is the resulting object and the
    second is the status code. When returning a tuple, a third element
    is optional and specifies the json encoder to use, and a fourth
    element is also optional and specifies the content type for the
    response.

    :param view_fn: The view function. For generic views, use ServiceView.
    :type view_fn: function.
    :returns: the wrapped view.
    """
    def wrapped(*args, **kwargs):
        try:
            result = view_fn(*args, **kwargs)
            if isinstance(result, tuple):
                if len(result) < 2 or len(result) > 4:
                    raise ValueError("view returned a {0}-length tuple".\
                                         format(len(result)))
                obj = result[0]
                status = result[1]
                encode = result[2] if len(result) > 2 else None
                ctype = result[3] if len(result) > 3 else None
                if not isinstance(status, (int, long)):
                    raise ValueError(
                        "invalid status type: got {0}, expected int".\
                            format(type(status).__name__))
                return renderjson(obj, status, encode, ctype)
            return renderjson(result, 200)
        except PermissionDenied:
            return renderjson(
                {'code': 403,
                 'reason': "forbidden",
                 'message': "you don't have permission "\
                     "to access this resource"},
                403)
        except Http404:
            return renderjson(
                {'code': 404,
                 'reason': "not found",
                 'message': "the requested resource doesn't exist"},
                404)
        except:
            logger.exception("error during view {0}".format(view_fn.__name__))
            return renderjson(
                {'code': 500,
                 'reason': "internal server error",
                 'message': "an internal error ocurred "\
                     "while processing your request"},
                500)
    return wraps(view_fn)(wrapped)


class ServiceView(View):
    """
    Generic for JSON-yielding views.
    """

    def http_method_not_allowed(self, request, *args, **kwargs):
        super(ServiceView, self).\
            http_method_not_allowed(request, *args, **kwargs)
        return ({'code': 405,
                 'reason': "method not allowed",
                 'message': "allowed methods are {0}".\
                     format(", ".join(self._allowed_methods()))},
                405)

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return service(handler)(request, *args, **kwargs)


def user_passes_test(predicate=None, method=False):
    """
    Wraps a view method with a test for the current user.

    :param predicate: the test to apply to the current user.
    :type predicate: function.
    :returns: the view's method wrapper.
    """
    predicate = (lambda _: True) if predicate is None else predicate
    def wrapper(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            request = args[1] if method else args[0]
            if not request.user.is_authenticated() or \
                    not predicate(request.user):
                raise PermissionDenied(
                    "user is anonymous or doesn't pass the test")
            return view(*args, **kwargs)
        return wrapped_view
    return wrapper


def csrf_failure(request, reason=""):
    if request.is_ajax():
        return renderjson(
            {'code': 403,
             'reason': "forbidden",
             'message': "csrf check failed"},
            403)
    raise PermissionDenied


def icon_for(tag):
    return u'<span class="glyphicon glyphicon-{0}"></span>'.format({
            'success': "ok-circle",
            'info': "info-sign",
            'warning': "exclamation-sign",
            'danger': "remove-circle"
            }.get(tag, "question-sign"))


class DataTable(object):
    """
    Object that renders itself as an html table with bootstrap class
    attributes and helper components, like a search bar and a
    paginator.
    """

    defaults = {
        'classes': "table table-hover table-condensed datatable", # css
        'styles': False, # inline styles
        'shown_pages': 4, # number of pages to show in paginator
        'search_cols': 4, # number of columns for the search widget
        'responsive': False, # wrap in a table-resposive div
        }

    def __init__(self, id_, headers,  datasource=None, paginated=True, **opts):
        self.id = id_
        self.headers = headers
        self.datasource = datasource
        self.paginated = paginated
        for k, v in self.defaults.iteritems():
            setattr(self, k, opts.get(k, v))
        if self.shown_pages < 1:
            self.shown_pages = 1
        if self.search_cols < 1:
            self.search_cols = 1
        elif self.search_cols > 11:
            self.search_cols = 11
        for k in opts:
            if k not in self.defaults:
                raise TypeError(
                    "__init__() got an unexpected keyword argument '{0}'".\
                        format(k))

    @property
    def paginator_cols(self):
        return 12 - self.search_cols

    @property
    def pages_range(self):
        return xrange(2, self.shown_pages + 1)

    @property
    def is_local(self):
        return self.datasource is None

    def __unicode__(self):
        return mark_safe(render_to_string("datatable.html", {'table': self}))


def with_datatable(request, queryset, searchfields, sortfields, pageitems=16):
    """
    Returns a modified version of the queryset that filters out
    results that don't match with the search query ('q' parameter),
    that don't fit into the page ('page' parameter), and orders them
    according to the given 'order_by' parameter.

    :param request: the http request.
    :type request: HttpRequest.
    :param queryset: the queryset to filter and sort.
    :type queryset: QuerySet.
    :param searchfields: list of fields of the model to sort.
    :type searchfields: list of str.
    :param sortfields: list of fields of the model that allow sorting.
    :type sortfields: list of str.
    :param pageitems: number of items per page.
    :type pageitems: int.
    :returns: a triad of (int, int, QuerySet) -- index of first
              element, total count, filtered queryset.
    """
    querystring = request.GET.get('q', "").strip()
    if querystring:
        queryset = queryset.filter(
            reduce(operator.or_, (Q(**{field + '__icontains': querystring})
                                  for field in searchfields)))

    sortfield = request.GET.get('order_by', None)
    if sortfield:
        field = sortfield if not sortfield.startswith('-') else sortfield[1:]
        if field in sortfields:
            queryset = queryset.order_by(sortfield)

    total = queryset.count()
    if pageitems <= 0:
        return (0, total, queryset)
    page = 1
    try: page = int(request.GET.get('page', '1'))
    except ValueError: pass
    if page < 1:
        page = 1
    queryset = queryset[((page - 1) * pageitems): (page * pageitems)]
    return ((page - 1) * pageitems + 1, total, queryset)
