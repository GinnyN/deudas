"""
.. module:: utils.middleware
   :synopsis: General purpose middleware for the project.
"""

import sys
import time
import logging
from functools import wraps

from django.conf import settings
from django.db import connection


logger = logging.getLogger(__name__)


class Profiler(object):
    """
    Middleware to measure performance.
    """

    def profile_view(self, view):
        """
        Measure performance in views.

        :param view: the view to profile.
        :type view: function.
        :returns: the wrapped view.
        """
        def profiled(request, *args, **kwargs):
            t1 = time.clock()
            response = view(request, *args, **kwargs)
            t2 = time.clock()
            log = lambda *args: logger.debug(u"".join(map(unicode, args)))
            log("profiled view:\t\t", view.__name__)
            log("url:\t\t\t", request.get_full_path())
            log("subdomain:\t\t", request.subdomain)
            log("get:\t\t\t", u"\n\t\t\t".join(
                    u"{0} => {1}".format(k, request.GET.getlist(k))
                    for k in request.GET))
            log("post:\t\t\t", u"\n\t\t\t".join(
                    u"{0} => {1}".format(k, request.POST.getlist(k))
                    for k in request.POST))
            log("arguments:\t\t", args)
            log("named arguments:\t", kwargs)
            log("execution time:\t\t", t2 - t1)
            log("query number:\t\t", len(connection.queries))
            return response
        return wraps(view)(profiled)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not settings.DEBUG: return None
        return self.profile_view(view_func)(request, *view_args, **view_kwargs)
