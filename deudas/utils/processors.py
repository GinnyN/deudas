"""
.. module:: utils.processors
   :synopsis: Context processors for general use.
"""

import re

from django.conf import settings
from django.conf.urls import url as django_url
from django.contrib.sites.models import get_current_site, Site
from django.utils.html import mark_safe


def default_site():
    if hasattr(default_site, 'cache'):
        return default_site.cache
    default_site.cache = Site.objects.get(pk=settings.SITE_ID)
    return default_site.cache


def get_site(request):
    if hasattr(get_site, 'cache'):
        return get_site.cache
    get_site.cache = get_current_site(request)
    return get_site.cache


def site_processor(request):
    return {'site': get_site(request)}


# Javascript url resolver

JS_URLS = {}


def parse_js_expression(subdomain, expr):
    args = sorted(set(re.findall("\$\d+", expr)), key=lambda tok: int(tok[1:]))
    site = "http://{0}.{1}/".format(subdomain, default_site().domain) \
        if subdomain is not None else "/";
    return mark_safe("function({0}) {{ return '{1}'{2} }}".\
                         format(", ".join(args), site,
                                u" + " + expr if expr else ""))


def pythonize_name(name):
    return u"".join({'-': "_", ' ': "_"}.get(c, c) for c in name)


def make_url(subdomains=('*',)):
    def url(*args, **kwargs):
        if 'js' not in kwargs:
            return django_url(*args, **kwargs)
        if 'name' not in kwargs:
            raise ValueError("url name attribute required for js parameter")
        name = pythonize_name(kwargs['name'])
        for subdomain in subdomains:
            subsite = JS_URLS.get(subdomain, {})
            subsite[name] = kwargs['js']
            JS_URLS[subdomain] = subsite
        kwargs.pop('js')
        return django_url(*args, **kwargs)
    return url


def js_urls_processor(request):
    subsite = JS_URLS.get(request.subdomain)
    if subsite is None:
        subsite = JS_URLS.get('*')
        if subsite is None: return {}
    return {'js_urls': dict((name, parse_js_expression(request.subdomain, expr))
                            for name, expr in subsite.iteritems())}
