from django.conf.urls import patterns, include, url
from django.conf import settings
from front import views 

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',views.Login.as_view(), name="login"),
    url(r'^list/$',views.List.as_view(), name="list"),
    url(r'^logout/$',views.LogOut.as_view(), name="logout"),
    url(r'^add/cliente$',views.addCliente.as_view(), name="add-cliente"),
    url(r'^add/glosa/$',views.addGlosa.as_view(), name="add-glosa"),
    url(r'^add/cobro$',views.addCobro.as_view(), name="add-cobro"),
    url(r'^add/abono$',views.addAbono.as_view(), name="add-abono"),
    url(r'^edit/cliente/$',views.editCliente.as_view(), name="edit-cliente"),
    url(r'^delete/cliente/$',views.deleteCliente.as_view(), name="delete-cliente"),
    url(r'^delete/ingreso/$',views.deleteIngreso.as_view(), name="delete-ingreso"),
    url(r'^filter/$',views.filter.as_view(), name="filter"),
    url(r'^excel/(?P<interval>.+)/(?P<fecha>.+)/$',views.excel.as_view(), name="excel"),
    url(r'^cartas/cartas.pdf$',views.cartas.as_view(), name="cartas"),
    url(r'^mensualidad/$',views.aplicarMensualidad.as_view(), name="mensualidad"),
    url(r'^createUser/$',views.createUser.as_view(), name="create-user"),
    url(r'^changePassword/$',views.changePassword.as_view(), name="change-password"),

    url(r'^cliente/(?P<id>\d+)$',views.cliente.as_view(), name="cliente"),
    url(r'^load/log',views.loadLog.as_view(), name="load-log"),
    url(r'^config/',views.config.as_view(), name="config"),
)

