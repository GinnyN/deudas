# -*- coding: utf-8 -*-

import datetime, imp
from django.conf.urls.defaults import *
from django.conf import settings
from reports.views import *
from django.views.generic.date_based import archive_year
from django.contrib.admin.models import LogEntry
from django.utils.importlib import import_module

queryset    = LogEntry.objects.all()
report_conf = settings.REPORT_CONF
report_conf['title'] = 'Admin action log (%d total)' % len(queryset)

urlpatterns = patterns('',
    url(r'^actions/$', archive_year, {
        'year':             datetime.datetime.now().year,
        'date_field':       'action_time',
        'make_object_list': True,
        'queryset':         queryset,
        'template_name':    'report/actions.html',
        'extra_context':    settings.REPORT_CONF,
    },name='reports-actions'),
) 

for app in settings.INSTALLED_APPS:
    try:
        app_path = import_module(app).__path__
    except AttributeError:
        continue
    try:
        imp.find_module('report_urls', app_path)
    except ImportError:
        continue
        
    urlpatterns += patterns('',
        (r'^%s/' % app.split('.')[-1], include('%s.report_urls' % app)),
    )
