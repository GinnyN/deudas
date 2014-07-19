import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, FormView
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from front import forms, models
from django.db.models import Sum

class Login(FormView):	
	template_name = 'auth.html'
	form_class = AuthenticationForm
	success_url = "/list/"

	def form_valid(self, form):
		login(self.request,form.get_user())
		return super(Login, self).form_valid(form)

class List(TemplateView):
	template_name = "lista.html"

	def get_context_data(self, **kwargs):
		context = super(List, self).get_context_data(**kwargs)
		context["formCliente"] = forms.ClienteForm()
		context["formGlosa"] = forms.GlosaForm()
		context["formCobro"] = forms.CobroForm(prefix="id")
		context["formAbono"] = forms.AbonoForm(prefix="id")	
		context["duenios"] = models.Cliente.objects.values_list("duenio").distinct()
		context["listCliente"] = models.Cliente.objects.all().order_by("pk")
		context["listGlosa"] = models.Glosa.objects.all().order_by("pk")
		context["clienteGlosa"] = tabla(context["listCliente"],context["listGlosa"])
		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

def tabla(listCliente,listGlosa):
	month = datetime.date.today().month
	year = datetime.date.today().year
	return map(
		(lambda cliente:
			[cliente.nombre,
			map(lambda glosa:
				models.Ingreso.objects.filter(cliente=cliente,glosa=glosa,fecha__month=month,fecha__year=year).aggregate(Sum('valor'))["valor__sum"],
			listGlosa),
			deuda(cliente,"deuda",month, year),
			deuda__other(cliente,"deuda",month, year) - deuda__other(cliente,"boleta",month, year),
			deuda(cliente,"boleta",month, year),
			deuda_total(cliente,"deuda") - deuda_total(cliente,"boleta"),
			cliente.pk]),
		listCliente)

def deuda(cliente, tipo, month, year): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo,fecha__month=month,fecha__year=year).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(cliente=cliente,tipo=tipo,fecha__month=month,fecha__year=year).aggregate(Sum('valor'))["valor__sum"]

def deuda__other(cliente, tipo, month, year): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo).exclude(fecha__month=month,fecha__year=year).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(cliente=cliente,tipo=tipo).exclude(fecha__month=month,fecha__year=year).aggregate(Sum('valor'))["valor__sum"]

def deuda_total(cliente, tipo): 
	if models.Ingreso.objects.filter(cliente=cliente,tipo=tipo).aggregate(Sum('valor'))["valor__sum"] == None: 
		return 0
	else:
		return models.Ingreso.objects.filter(cliente=cliente,tipo=tipo).aggregate(Sum('valor'))["valor__sum"]


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
		form = forms.GlosaForm(request.POST)
		if form.is_valid():
			form.save()
		return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class addCobro(View):

	def post(self, request):
		form = forms.CobroForm(request.POST,prefix="id")
		if form.is_valid():
			print("Hola!")
			cliente = models.Cliente.objects.get(pk=request.POST["cliente_pk"])
			print("Hola!")
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
			print("Hola!")
			cliente = models.Cliente.objects.get(pk=request.POST["cliente_pk"])
			print("Hola!")
			cobro = models.Ingreso(cliente=cliente,
				fecha=form.cleaned_data["fecha"],
				tipo="boleta",
				valor=form.cleaned_data["valor"],
				glosa=None,
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

class filter(TemplateView):
	template_name = "table.html"

	def get_context_data(self, **kwargs):
		context = super(filter, self).get_context_data(**kwargs)
		context["listGlosa"] = models.Glosa.objects.all().order_by("pk")
		if(self.request.GET["filter"]=="all"):
			context["listCliente"] = models.Cliente.objects.all().order_by("pk")
		elif self.request.GET["filter"]=="natural":
			context["listCliente"] = models.Cliente.objects.filter(tipo="natural").order_by("pk")
		elif self.request.GET["filter"]=="no":
			context["listCliente"] = models.Cliente.objects.filter(tipo="sociedad",duenio="").order_by("pk")
		else:
			context["listCliente"] = models.Cliente.objects.filter(tipo="sociedad",duenio=self.request.GET["filter"]).order_by("pk")
		context["clienteGlosa"] = tabla(context["listCliente"],context["listGlosa"])
		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

class cliente(TemplateView):
	template_name = "cliente.html"

	def get_context_data(self, id, **kwargs):
		context = super(cliente, self).get_context_data(**kwargs)
		context["cliente"] = models.Cliente.objects.get(pk=id)
		context["ingreso"] = models.Ingreso.objects.filter(cliente=context["cliente"]).order_by("-fecha")
		context["deuda"] = context["ingreso"].filter(tipo="deuda").order_by("-fecha")
		context["boleta"] = context["ingreso"].filter(tipo="boleta").order_by("-fecha")
		context["balance"] = deuda_total(context["cliente"],"deuda") - deuda_total(context["cliente"],"boleta")
		context["formCliente"] = forms.ClienteForm(instance=context["cliente"],prefix="cliente")
		context["formCobro"] = forms.CobroForm(prefix="id")
		context["formAbono"] = forms.AbonoForm(prefix="id")	
		
		listaNatural = map(lambda cliente: cliente.pk, models.Cliente.objects.filter(tipo="natural"))
		listaSociedad = map(lambda cliente: cliente.pk, models.Cliente.objects.filter(tipo="sociedad").order_by("duenio"))
		try:
			place = listaNatural.index(int(id))
			print(place)
			print(listaNatural[place])
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

		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)