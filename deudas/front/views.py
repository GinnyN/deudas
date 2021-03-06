# -*- coding: utf-8 -*-

import datetime
import locale
import calendar
import xlwt
import cStringIO
import urllib
import codecs

import os
import logging

logging.basicConfig()

from django.http import HttpResponse
from utils.exporter import xls_response
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, FormView
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.db.models import Sum 
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.views.generic.edit import CreateView
from django.contrib.auth import logout
from front import forms, models

# Style constants

#: Style to be applied to date and datetime columns.
DATESTYLE = xlwt.easyxf("", "DD/MM/YYYY")

#: Default style for text cells.
DEFAULTSTYLE = xlwt.easyxf("align: wrap on")

#: Style to be applied to headers.
_HEADERSTYLE = xlwt.easyxf("font: bold on; "
                           "align: wrap on, vert center, horiz center")

#: Unit of with for columns.
_COLUMN_WIDTH = 1344

#Default Config
CARTACONFIG = 2
CEROSXLSBODY = False
CEROSXLSFOOTER = True
COBROMENSUALIDAD = True


class Login(FormView):	
	template_name = 'auth.html'
	form_class = AuthenticationForm
	success_url = "/list/"

	def form_valid(self, form):
		login(self.request,form.get_user())
		return super(Login, self).form_valid(form)

class config(FormView):
	template_name = "creation.html"
	form_class = forms.ConfigForm
	success_url = "/list/"

	def get_initial(self, **kwargs):
		try:
			configModel = models.Config.objects.get(id=1)
			context = {
				'cartaPerPage': configModel.cartaPerPage,
				'cerosOnXlsBody': configModel.cerosOnXlsBody,
				'cerosOnXlsFooter': configModel.cerosOnXlsFooter,
				'activarMensualidad': configModel.activarMensualidad, 
			}
		except:
			context = {
				'cartaPerPage': CARTACONFIG,
				'cerosOnXlsFooter': CEROSXLSFOOTER,
				'cerosOnXlsBody': CEROSXLSBODY,
				'activarMensualidad': COBROMENSUALIDAD,
			}
		return context
		

	def form_valid(self, form):
		form.instance.id = 1
		form.save()
		return super(config, self).form_valid(form)

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

def loadConfig():
	try:
		return models.Config.objects.get(id=1)
	except:
		return models.Config(cartaPerPage= CARTACONFIG,
				cerosOnXlsFooter= CEROSXLSFOOTER,
				cerosOnXlsBody= CEROSXLSBODY,
				activarMensualidad= COBROMENSUALIDAD)

class LogOut(View):

	def get(self,request):
		logout(request)
		return redirect("login")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


class createUser(CreateView):
	template_name = "creation.html"
	form_class = UserCreationForm
	success_url = "/list/"

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class changePassword(View):

	def get(self, request):
		form = PasswordChangeForm(user=request.user)
		return render(request,"creation.html", {'form':form})

	def post(self, request):
		form = PasswordChangeForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
		return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class List(TemplateView):
	template_name = "lista.html"

	def get_context_data(self, **kwargs):
		context = super(List, self).get_context_data(**kwargs)

		today = datetime.date.today()
		thisMonth = datetime.date(day=1,month=today.month,year=today.year)
		lastMonth = thisMonth - datetime.timedelta(days=1)
		'''if models.Glosa.objects.filter(nombre="Atrasado").exists():
			glosa = models.Glosa.objects.get(nombre="Atrasado")
		else:
			glosa = models.Glosa(nombre="Atrasado",detalle="Honorarios Mensuales Atrasados")
			glosa.save()

		mensualidades = models.Ingreso.objects.filter(glosa__nombre="Mensualidad",fecha__month=lastMonth.month)
		for mensualidad in mensualidades:
			mensualidad.glosa = glosa
			mensualidad.save()
		'''
		if models.Glosa.objects.filter(nombre="Mensualidad").exists():
			mensualidad = models.Glosa.objects.get(nombre="Mensualidad")
		else:
			glosa = models.Glosa(nombre="Mensualidad",detalle="Honorarios Mensuales")
			glosa.save()

		if models.Glosa.objects.filter(nombre="Atrasado").exists() != True:
			models.Glosa(nombre="Atrasado", detalle="Honorarios Atrasados").save()

		config = loadConfig()

		today = datetime.date.today()
		last_month = datetime.date(day=1,month=today.month,year=today.year) - datetime.timedelta(days=1)

		#models.Ingreso.objects.filter(glosa=mensualidad, fecha__month=today.month).delete()
		#models.Ingreso.objects.filter(glosa=mensualidad, fecha__month=last_month.month).delete()

		if config.activarMensualidad:
			clientes = models.Cliente.objects.filter(activo="activo").exclude(mensualidad=None)
			for cliente in clientes:
				if not models.Ingreso.objects.filter(cliente=cliente,glosa=mensualidad,fecha__month=last_month.month) or models.Ingreso.objects.filter(cliente=cliente,glosa=mensualidad,fecha__month=last_month.month,valor=None):
					models.Ingreso.objects.filter(cliente=cliente,glosa=mensualidad,fecha__month=last_month.month,valor=None).delete()
					ingreso = models.Ingreso(glosa=mensualidad,tipo="deuda",fecha=last_month,valor=cliente.mensualidad,cliente=cliente,numero=1)
					ingreso.save()

		locale.setlocale(locale.LC_TIME, 'es_ES')
		context["formCliente"] = forms.ClienteForm()
		context["formGlosa"] = forms.GlosaForm(prefix="id")
		context["formCobro"] = forms.CobroForm(prefix="id")
		context["formAbono"] = forms.AbonoForm(prefix="id")	
		context["duenios"] = models.Cliente.objects.all().order_by("duenio").values_list("duenio").distinct()
		context["listCliente"] = models.Cliente.objects.all().order_by("nombre")
		context["listGlosa"] = models.Glosa.objects.all().order_by("pk").exclude(nombre__in=["Mensualidad","Atrasado"])
		table = tabla(context["listCliente"],context["listGlosa"],datetime.date.today(),"m")
		context["clienteGlosa"] = table[1]
		context["listGlosa"] = table[0]
		context["ahora"] = datetime.date.today().strftime("%B - %Y")
		dates = models.Ingreso.objects.all().order_by("-fecha").values_list("fecha").distinct()
		context["dates"] = monthsGenerator(dates, "%B - %Y")
		context["years"] = monthsGenerator(dates, "%Y")	

		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

def monthsGenerator(dates, format):
	locale.setlocale(locale.LC_TIME, 'es_ES')
	datesList = map(lambda date: date[0].strftime(format), dates)
	listDates = []
	for distint in datesList:
		if distint not in listDates:
			listDates.append(distint) 
	return listDates

def mensualidad(date):
	if models.Ingreso.objects.filter(fecha__month=date.month,glosa__nombre="Mensualidad").count() == models.Cliente.objects.filter(activo="activo").count():
		return True
	else:
		return False

def tabla(listCliente,listGlosa, date,interval):
	month = date.month
	year = date.year
	if interval == "m":
		datet = date.replace(day = calendar.monthrange(year, month)[1])
		datel = date.replace(day = 1)
	else:
		datet = datetime.date(date.year,12,31)
		datel = datetime.date(date.year,1,1)

	listGlosa2 = listGlosa
	listGlosa = []

	for glosa in listGlosa2:
		if not glosaCalc(listCliente, glosa,datet) == 0:
			listGlosa.append(glosa)

	return [listGlosa, [tablaCliente(listCliente,listGlosa,datel,datet),tablaTotal(listCliente,listGlosa,datel,datet)]]

def tablaTotal(listCliente,listGlosa,datel,datet):
	return [["Mensualidad", mensualidadCal(listCliente, False,datet,datel)],
		["Atrasado", mensualidadCal(listCliente, True,datet,datel)],
		map(lambda glosa:
		[glosa, glosaCalc(listCliente,glosa,datet)],	
		listGlosa),
		deuda_total("deuda",listCliente,datet) - deuda_total("boleta",listCliente,datet)]

def tablaCliente(listCliente,listGlosa,datel,datet):
	return map(
		(lambda cliente:
			[cliente.nombre,
			["Mensualidad", mensualidadCal(cliente,False,datet,datel)],
			["Atrasado", mensualidadCal(cliente,True,datet,datel)],
			map(lambda glosa:
				[glosa, glosaCalcCliente(cliente,glosa,datet)],
			listGlosa),
			deuda_totalCliente(cliente,"deuda",datet) - deuda_totalCliente(cliente,"boleta",datet),
			cliente.pk,
			cliente.tipo]),
		listCliente)

def mensualidadCal(listCliente, atrasado, datet, datel):
	glosa =  models.Glosa.objects.get(nombre="Mensualidad")
	atrasadoGlosa =  models.Glosa.objects.get(nombre="Atrasado")

	if isinstance(listCliente, list):
		lista = models.Ingreso.objects.filter(cliente__in=listCliente)
	else:
		lista = models.Ingreso.objects.filter(cliente=listCliente)

	if atrasado:
		if lista.filter(glosa=glosa,fecha__lt=datel, cliente=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"] == None:
			deuda = 0
		else:
			deuda = int(lista.filter(glosa=glosa,fecha__lt=datel, cliente=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"])

		if lista.filter(glosa=atrasadoGlosa, fecha__lt= datet, cliente=listCliente, tipo="deuda").aggregate(Sum('valor'))["valor__sum"] == None:
			atrasado = 0
		else:
			atrasado = int(lista.filter(glosa=atrasadoGlosa, fecha__lt= datet, cliente=listCliente, tipo="deuda").aggregate(Sum('valor'))["valor__sum"])
		
		if lista.filter(glosa=atrasadoGlosa, fecha__lt= datet, cliente=listCliente, tipo="boleta").aggregate(Sum('valor'))["valor__sum"] == None:
			atrasadoBoleta = 0
		else:
			atrasadoBoleta = int(lista.filter(glosa=atrasadoGlosa, fecha__lte= datet, cliente=listCliente, tipo="boleta").aggregate(Sum('valor'))["valor__sum"])
		

		if lista.filter(glosa=glosa,fecha__lt=datel, cliente=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"] == None:
			boleta = 0
		else:
			boleta = int(lista.filter(glosa=glosa,fecha__lt=datel, cliente=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"])
	else:
		if lista.filter(glosa=glosa,fecha__lte=datet, fecha__gte=datel, cliente=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"] == None:
			deuda = 0
		else:
			deuda = int(lista.filter(glosa=glosa,fecha__lte=datet, fecha__gte=datel, cliente=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"])

		if lista.filter(glosa=glosa,fecha__lte=datet, fecha__gte=datel, cliente=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"] == None:
			boleta = 0
		else:
			boleta = int(lista.filter(glosa=glosa,fecha__lte=datet, fecha__gte=datel, cliente=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"])

		atrasado = 0
		atrasadoBoleta = 0

	return atrasado + deuda - boleta - atrasadoBoleta

def glosaCalc(listCliente, glosa,datet):
	if models.Ingreso.objects.filter(glosa=glosa,fecha__lte=datet, cliente__in=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"] == None:
		deuda = 0
	else:
		deuda = int(models.Ingreso.objects.filter(glosa=glosa,fecha__lte=datet, cliente__in=listCliente,tipo="deuda").aggregate(Sum('valor'))["valor__sum"])

	if models.Ingreso.objects.filter(glosa=glosa,fecha__lte=datet, cliente__in=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"] == None:
		boleta = 0
	else:
		boleta = int(models.Ingreso.objects.filter(glosa=glosa,fecha__lte=datet, cliente__in=listCliente,tipo="boleta").aggregate(Sum('valor'))["valor__sum"])

	return deuda - boleta

def glosaCalcCliente(cliente,glosa,datet):
	if models.Ingreso.objects.filter(cliente=cliente,glosa=glosa,fecha__lte=datet,tipo="deuda").aggregate(Sum('valor'))["valor__sum"] == None:
		deuda = 0
	else:
		deuda = int(models.Ingreso.objects.filter(cliente=cliente,glosa=glosa,fecha__lte=datet,tipo="deuda").aggregate(Sum('valor'))["valor__sum"])

	if models.Ingreso.objects.filter(cliente=cliente,glosa=glosa,fecha__lte=datet,tipo="boleta").aggregate(Sum('valor'))["valor__sum"] == None:
		boleta = 0
	else:
		boleta = int(models.Ingreso.objects.filter(cliente=cliente,glosa=glosa,fecha__lte=datet,tipo="boleta").aggregate(Sum('valor'))["valor__sum"])

	return deuda - boleta

def deuda(tipo, listCliente,datet, date): 
	if models.Ingreso.objects.filter(tipo=tipo,fecha__lte=datet, fecha__gte=date, cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(tipo=tipo,fecha__lte=datet, fecha__gte=date, cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"]

def deudaCliente(cliente, tipo, datet, date): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo,fecha__lte=datet, fecha__gte=date).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(cliente=cliente,tipo=tipo,fecha__lte=datet, fecha__gte=date).aggregate(Sum('valor'))["valor__sum"]

def deuda__other(tipo, listCliente, date): 
	if models.Ingreso.objects.filter(tipo=tipo, fecha__lte=date,cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(tipo=tipo, fecha__lte=date,cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"]

def deuda__otherCliente(cliente, tipo, date): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo, fecha__lte=date).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return int(models.Ingreso.objects.filter(cliente=cliente,tipo=tipo, fecha__lte=date).aggregate(Sum('valor'))["valor__sum"])

def deuda_total(tipo,listCliente, datet): 
	print(models.Ingreso.objects.filter(tipo=tipo, fecha__lte=datet,cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"])
	if models.Ingreso.objects.filter(tipo=tipo, fecha__lte=datet,cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return int(models.Ingreso.objects.filter(tipo=tipo, fecha__lte=datet,cliente__in=listCliente).aggregate(Sum('valor'))["valor__sum"])

def deuda_totalCliente(cliente, tipo, datet): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo, fecha__lte=datet).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return int(models.Ingreso.objects.filter(cliente=cliente,tipo=tipo, fecha__lte=datet).aggregate(Sum('valor'))["valor__sum"])


class addCliente(View):

	def post(self, request):
		form = forms.ClienteForm(request.POST)
		if form.is_valid():
			form.save()
		return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class addGlosa(View):

	def post(self, request):
		if(request.POST["selectGlosa"]=="new"):
			form = forms.GlosaForm(request.POST,prefix="id")
		else:
			form = forms.GlosaForm(request.POST,prefix="id",instance=models.Glosa.objects.get(pk=request.POST["selectGlosa"]))
		if form.is_valid():
			form.save()
		return redirect("list")

	def get(self, request):
		if(request.GET["selectGlosa"]=="new"):
			return  render(request, 'form.html', 
			{"form": forms.GlosaForm(prefix="id")})
		else:
			return  render(request, 'form.html', 
			{"form": forms.GlosaForm(prefix="id",instance=models.Glosa.objects.get(pk=request.GET["selectGlosa"]))})

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class addCobro(View):

	def post(self, request):
		form = forms.CobroForm(request.POST,prefix="id")
		if form.is_valid():
			cliente = models.Cliente.objects.get(pk=request.POST["cliente_pk"])
			cobro = models.Ingreso(cliente=cliente,
				fecha=form.cleaned_data["fecha"],
				tipo="deuda",
				valor=form.cleaned_data["valor"],
				glosa=form.cleaned_data["glosa"],
				numero=0)
			cobro.save()
		else:
			print(form.errors)

		try:
			if request.POST["where"] == "cliente":
				return redirect("cliente",id=request.POST["cliente_pk"])
		except:
			return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class addAbono(View):

	def post(self, request):
		form = forms.AbonoForm(request.POST,prefix="id")
		if form.is_valid():
			cliente = models.Cliente.objects.get(pk=request.POST["cliente_pk"])
			cobro = models.Ingreso(cliente=cliente,
				fecha=form.cleaned_data["fecha"],
				tipo="boleta",
				valor=form.cleaned_data["valor"],
				glosa=form.cleaned_data["glosa"],
				numero=form.cleaned_data["numero"])
			cobro.save()
		else:
			print(form.errors)

		try:
			if request.POST["where"] == "cliente":
				return redirect("cliente",id=request.POST["cliente_pk"])
		except:
			return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class editCliente(View):

	def get(self, request):
		return  render(request, 'form.html', 
			{"form": forms.ClienteForm(instance=models.Cliente.objects.get(pk=request.GET["pk"]),prefix="cliente")})

	def post(self, request):
		form = forms.ClienteForm(request.POST,prefix="cliente",instance=models.Cliente.objects.get(pk=request.POST["cliente_pk"]))
		if form.is_valid():
			form.save()
		try:
			if request.POST["where"] == "cliente":
				return redirect("cliente",id=request.POST["cliente_pk"])
		except:
			return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class deleteCliente(View):

	def post(self, request):
		models.Cliente.objects.get(pk=request.POST["cliente_pk"]).delete()
		return HttpResponse()

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


class filter(TemplateView):
	template_name = "table.html"

	def get_context_data(self, **kwargs):
		context = super(filter, self).get_context_data(**kwargs)
		context["listGlosa"] = models.Glosa.objects.exclude(nombre__in=["Mensualidad","Atrasado"]).order_by("pk")
		locale.setlocale(locale.LC_TIME, 'es_ES')
		try:
			datet = datetime.datetime.strptime(self.request.GET["date"], "%B - %Y")
			interval = "m"
		except: 
			datet = datetime.datetime.strptime(self.request.GET["date"], "%Y")
			interval = "y"
		
		if(self.request.GET["filter"]=="all"):
			context["listCliente"] = models.Cliente.objects.all().order_by("pk")
		elif self.request.GET["filter"]=="natural":
			context["listCliente"] = models.Cliente.objects.filter(tipo="natural").order_by("nombre")
		elif self.request.GET["filter"]=="sociedades":
			context["listCliente"] = models.Cliente.objects.filter(tipo="sociedad").order_by("nombre")
		elif self.request.GET["filter"]=="no":
			context["listCliente"] = models.Cliente.objects.filter(tipo="sociedad",duenio=None).order_by("nombre")
		else:
			context["listCliente"] = models.Cliente.objects.filter(duenio=self.request.GET["filter"]).order_by("nombre")
		if self.request.GET["activo"] == "activo":
			context["listCliente"] = context["listCliente"].filter(activo=self.request.GET["activo"])
		table = tabla(context["listCliente"],context["listGlosa"],datet,interval)
		context["clienteGlosa"] = table[1]
		context["listGlosa"] = table[0]

		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class cliente(TemplateView):
	template_name = "cliente.html"

	def get_context_data(self, id, **kwargs):
		context = super(cliente, self).get_context_data(**kwargs)
		dateEnd = datetime.date.today().replace(day = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1])
		context["dateEnd"] = dateEnd.strftime("%d/%m/%Y")
		dateBegining = datetime.date.today().replace(day = 1)
		context["dateBegining"] = dateBegining.strftime("%d/%m/%Y")
		context["cliente"] = models.Cliente.objects.get(pk=id)
		context["ingreso"] = models.Ingreso.objects.filter(fecha__lte=dateEnd, fecha__gte=dateBegining, cliente=context["cliente"]).order_by("-fecha")
		context["deuda"] = context["ingreso"].filter(tipo="deuda").order_by("-fecha")
		context["boleta"] = context["ingreso"].filter(tipo="boleta").order_by("-fecha")
		context["balance"] = deuda_totalCliente(context["cliente"],"deuda",dateEnd) - deuda_totalCliente(context["cliente"],"boleta",dateEnd)
		context["formCliente"] = forms.ClienteForm(instance=context["cliente"],prefix="cliente")
		context["formCobro"] = forms.CobroForm(prefix="id")
		context["formAbono"] = forms.AbonoForm(prefix="id")
		dates = models.Ingreso.objects.all().order_by("-fecha").values_list("fecha").distinct()
		context["dates"] = monthsGenerator(dates, "%B - %Y")
		
		if models.Cliente.objects.filter(tipo="natural").exists():
			listaNatural = map(lambda cliente: cliente.pk, models.Cliente.objects.filter(tipo="natural"))
		
		if models.Cliente.objects.filter(tipo="sociedad").exists():
			listaSociedad = map(lambda cliente: cliente.pk, models.Cliente.objects.filter(tipo="sociedad").order_by("duenio"))
		try:
			try:
				place = listaNatural.index(int(id))
				if place + 1 == len(listaNatural):
					context["next"] = listaSociedad[0]	
				else:
					context["next"] = listaNatural[place+1]
					

				if place - 1 > -1:
					context["prev"] = listaNatural[place-1]

			except:
				place = listaSociedad.index(int(id))
				if place+1 < len(listaSociedad):	
					context["next"] = listaSociedad[place+1]

				if place-1 > -1:
					context["prev"] = listaSociedad[place-1]
				else:
					context["prev"] = listaNatural[len(listaNatural)-1]
		except:
			pass

		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class deleteIngreso(View):

	def post(self, request):
		models.Ingreso.objects.get(pk=request.POST["pk"]).delete()
		return redirect("cliente",id=request.POST["cliente_pk"])

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class loadLog(TemplateView):
	template_name = "tab.html"

	def get_context_data(self, **kwargs):
		context = super(loadLog, self).get_context_data(**kwargs)
		cliente= models.Cliente.objects.get(pk=self.request.GET["cliente_pk"])
		begin = datetime.datetime.strptime(self.request.GET["begin"], "%d/%m/%Y")
		end = datetime.datetime.strptime(self.request.GET["end"], "%d/%m/%Y")
		context["ingreso"] = models.Ingreso.objects.filter(fecha__lte=end, fecha__gte=begin, cliente=cliente).order_by("-fecha")
		context["deuda"] = context["ingreso"].filter(tipo="deuda").order_by("-fecha")
		context["boleta"] = context["ingreso"].filter(tipo="boleta").order_by("-fecha")
		return context
		

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class excel(View):

	http_method_names = ['get']

	def get(self, request, interval, fecha):
		locale.setlocale(locale.LC_TIME, 'es_ES')
		fecha.encode('utf8')
		if interval == "m":
			date = datetime.datetime.strptime(fecha, "%B - %Y")
		else: 
			date = datetime.datetime.strptime(fecha, "%Y")
		month = date.month
		year = date.year

		if interval == "m":
			datet = date.replace(day = calendar.monthrange(year, month)[1])
			datel = date.replace(day = 1)
		else:
			datet = datetime.date(date.year,12,31)
			datel = datetime.date(date.year,1,1)

		listGlosa= models.Glosa.objects.all().order_by("pk").exclude(nombre__in=["Mensualidad","Atrasado"])
		listGlosa2 = listGlosa
		listGlosa = []
		listCliente = models.Cliente.objects.order_by("nombre")

		for glosa in listGlosa2:
			if not glosaCalc(listCliente, glosa,datet) == 0:
				listGlosa.append(glosa)

		qs = [[u"Sociedades sin Dueño"]]
		qs = qs + tablaCliente(listCliente.filter(duenio=None, tipo=u"sociedad"),listGlosa,datel,datet)
		listaSociedad = tablaCliente(listCliente.filter(duenio="", tipo=u"sociedad"),listGlosa,datel,datet)
		qs = qs + listaSociedad

		qn = [[u"Personas Naturales"]]
		qn = qn + tablaCliente(listCliente.filter(duenio=None, tipo=u"natural"),listGlosa,datel,datet)
		listaSociedad = tablaCliente(listCliente.filter(duenio="", tipo=u"natural"),listGlosa,datel,datet)
		qn = qn + listaSociedad

		qs = qn + qs

		familias = models.Cliente.objects.filter(duenio__regex=u"Familia(.*)").order_by("duenio").values_list("duenio").distinct()
		empresas = models.Cliente.objects.exclude(duenio__regex=u"Familia(.*)").exclude(duenio=u"").order_by("duenio").values_list("duenio").distinct()
		
		for duenio in familias:
			qs.append([duenio[0]])
			listaSociedad = tablaCliente(listCliente.filter(duenio=duenio[0]),listGlosa,datel,datet)
			qs = qs + listaSociedad

		for duenio in empresas:
			qs.append([duenio[0]])
			listaSociedad = tablaCliente(listCliente.filter(duenio=duenio[0]),listGlosa,datel,datet)
			qs = qs + listaSociedad

		headers = map(lambda glosa: (glosa.nombre) ,listGlosa)
		headers.insert(0,"Atrasado")
		headers.insert(0,"Mensualidad")
		headers.insert(0,"Nombre")
		headers.append("Total")

		book = xlwt.Workbook(encoding="UTF-8")
		sheet = book.add_sheet(u"Clientes "+fecha)

		for c, h in enumerate(headers):
			w = 4
			if isinstance(h, tuple):
				h, w = h
			w = w * _COLUMN_WIDTH
			sheet.write(0, c, h.encode("UTF-8"), _HEADERSTYLE)
			sheet.col(c).width = w

		config = loadConfig()
		y = 1
		for row in qs:
			if len(row) > 1:
				row.pop()
				row.pop()
				i = 0
				for cell in row:
					if isinstance(cell, list):
						for insideCell in cell:
							if isinstance(insideCell, list):
								if (config.cerosOnXlsBody == False) and (insideCell[1] == 0):
									cont = ""
								else:
									cont = unicode(insideCell[1]).encode("UTF-8")
								sheet.write(y, i, cont, DEFAULTSTYLE)
								i+=1
							else:
								if isinstance(insideCell, int):
									if (config.cerosOnXlsBody == False) and (insideCell == 0):
										cont = ""
									else:
										cont = unicode(insideCell).encode("UTF-8")
									sheet.write(y, i, cont, DEFAULTSTYLE)
									i+=1
					else:
						if (config.cerosOnXlsBody == False) and (cell == 0):
							cont = ""
						else:
							cont = unicode(cell).encode("UTF-8")
						sheet.write(y, i, cont, DEFAULTSTYLE)
						i+=1
			else:
				sheet.write(y, 0, "", _HEADERSTYLE)
				y+=1
				sheet.write(y, 0, unicode(row[0]).encode("UTF-8"), _HEADERSTYLE)
			y+=1

		i = 1

		for cell in tablaTotal(listCliente, listGlosa,datel,datet):
			if isinstance(cell, list):
				for insideCell in cell:
					if isinstance(insideCell, list):
						if (config.cerosOnXlsFooter == False) and (insideCell[1] == 0):
							cont = ""
						else:
							cont = unicode(insideCell[1]).encode("UTF-8")
						sheet.write(y, i, cont, _HEADERSTYLE)
						i+=1
					else:
						if isinstance(insideCell, int):
							if (config.cerosOnXlsFooter == False) and (insideCell == 0):
								cont = ""
							else:
								cont = unicode(insideCell).encode("UTF-8")
							sheet.write(y, i, cont, _HEADERSTYLE)
							i+=1
			else:
				if (config.cerosOnXlsFooter == False) and (unicode(cell) == 0): 
					cont=""
				else:
					cont=unicode(cell)
				sheet.write(y, i, cont, _HEADERSTYLE)
				i+=1

		response = HttpResponse()
		response['Content-Disposition'] = u"attachment; filename=Clientes "+fecha+".xls"
		response['Content-Type'] = "application/vnd.ms-excel"
		book.save(response)
		
		return response

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)


class cartas(View):

	def get(self, request, id):
		glosas = models.Glosa.objects.exclude(nombre="Mensualidad").exclude(nombre="Atrasado")
		listCliente = [models.Cliente.objects.get(pk=id)]

		locale.setlocale(locale.LC_TIME, 'es_ES')
		date = datetime.datetime.strptime(request.GET["dates"], "%B - %Y")

		datet = date.replace(day = calendar.monthrange(date.year, date.month)[1])
		datel = date.replace(day = 1)
		clients = tablaCliente(listCliente,glosas,datel,datet)
		#today = datetime.date.today()
 		#first = datetime.date(day=1, month=today.month, year=today.year)
 		lastMonth =  date #first - datetime.timedelta(days=1)
 		cartaPerPage = loadConfig().cartaPerPage

		return  render(request, 'carta.html', 
			{"clients": clients, "lastMonth": lastMonth, "cartaPerPage": cartaPerPage})

	def post(self, request):
		#for value in request.POST.getlist("value"):
		print(request.POST["value[]"])
		valuesString = request.POST.getlist('value[]') 
		value = []
		print(valuesString)
		for v in valuesString:
			value.append(int(v))
		glosas = models.Glosa.objects.exclude(nombre="Mensualidad").exclude(nombre="Atrasado")
		listCliente = models.Cliente.objects.filter(activo="activo",pk__in=valuesString).order_by("nombre")

		locale.setlocale(locale.LC_TIME, 'es_ES')
		request.POST["date"].encode('utf8')
		if request.POST["interval"] == "mensual":
			date = datetime.datetime.strptime(request.POST["date"], "%B - %Y")
		else: 
			date = datetime.datetime.strptime(request.POST["date"], "%Y")
		month = date.month
		year = date.year

		if request.POST["interval"] == "mensual":
			datet = date.replace(day = calendar.monthrange(year, month)[1])
			datel = date.replace(day = 1)
		else:
			datet = datetime.date(date.year,12,31)
			datel = datetime.date(date.year,1,1)

		#datet = datetime.date.today().replace(day = calendar.monthrange(datetime.date.today().year, datetime.date.today().month)[1])
		#datel = datetime.date.today().replace(day = 1)
		clients = tablaCliente(listCliente,glosas,datel,datet)
		#today = datetime.date.today()
 		#first = datetime.date(day=1, month=today.month, year=today.year)
 		lastMonth =  date #first - datetime.timedelta(days=1)
 		cartaPerPage = loadConfig().cartaPerPage
		return  render(request, 'carta.html', 
			{"clients": clients, "lastMonth": lastMonth, "cartaPerPage": cartaPerPage})

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class aplicarMensualidad(View):

	def get(self, request):
		cliente = map(lambda ingreso: ingreso.cliente.pk, models.Ingreso.objects.filter(fecha__month=datetime.date.today().month,glosa__nombre="Mensualidad"))
		applyTo = models.Cliente.objects.exclude(pk__in=cliente).exclude(activo="no-activo")
		try:
			glosa = models.Glosa.objects.get(nombre="Mensualidad")
		except:
			glosa = models.Glosa(nombre="Mensualidad")
			glosa.save()

		for c in applyTo:
			models.Ingreso(glosa=glosa,valor=c.mensualidad,tipo="deuda",cliente=c,fecha=datetime.date.today(),numero=0).save()

		return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)