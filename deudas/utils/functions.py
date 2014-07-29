"""
.. module:: utils.functions
"""

import re
import math
import operator
import hashlib
from itertools import imap

from django.db.models.query import QuerySet


class Object(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


def find(predicate, collection):
    for e in collection:
        if predicate(e):
            return e


def partition(predicate, collection):
    pos, neg = [], []
    for e in collection: (pos if predicate(e) else neg).append(e)
    return (pos, neg)


def mapmaybe(fn, collection):
    return [e for e in imap(fn, collection) if e is not None]


def flatten(iterable):
    return (e for subiter in iterable for e in subiter)


def const(value):
    return lambda *args, **kwargs: value


def in_batches(batch_size=100, queryset=None):
    """
    Splits a single queryset into many, each containing at most
    *batch_size* elements. It executes ``count()`` before yielding
    results.
    """
    if not isinstance(queryset, QuerySet):
        raise TypeError("in_batches expected a QuerySet object, got {0}".\
                            format(type(queryset).__name__))
    count = queryset.count()
    for batch in xrange(int(math.ceil(operator.truediv(count, batch_size)))):
        for e in queryset[batch * batch_size: (batch + 1) * batch_size]: yield e


def makehash(string):
    "Probably not the best way, but it's standard for the project"
    return hashlib.md5(string).hexdigest()


def fdate(date):
    "Standard date formatting."
    return date.strftime("%d/%m/%Y") if date is not None else ""


def frut(rut):
    "Standard rut formatting."
    if rut is None: return ""
    if re.match(r"^(\d+)-(\d|k|K)$", rut) is None: return rut
    parts = rut.split("-")
    body = ""
    for i, c in enumerate(reversed(parts[0])):
        if i % 3 == 0 and i != 0:
            body = "." + body
        body = c + body
    return u"-".join([body] + parts[1:])


def fpercent(percent):
    "Standard percentage formatting."
    if percent is None: return ""
    return u"{0} %".format(format(percent * 100, '.1f').replace(".", ","))
