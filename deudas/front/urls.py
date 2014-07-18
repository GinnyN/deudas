from django.conf.urls import patterns, include, url
from django.conf import settings
from front import views 

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',views.Login.as_view(), name="login"),
    url(r'^list/$',views.List.as_view(), name="list"),
    url(r'^add/cliente$',views.addCliente.as_view(), name="add-cliente"),
    url(r'^add/glosa$',views.addGlosa.as_view(), name="add-glosa"),
    url(r'^add/cobro$',views.addCobro.as_view(), name="add-cobro"),
    url(r'^add/abono$',views.addAbono.as_view(), name="add-abono"),
)

