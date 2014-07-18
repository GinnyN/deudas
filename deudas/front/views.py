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
		context["listCliente"] = models.Cliente.objects.all().order_by("pk")
		context["listGlosa"] = models.Glosa.objects.all().order_by("pk")
		context["clienteGlosa"] = map(
			(lambda cliente:
				[cliente.nombre,
				map(lambda glosa:
					models.Ingreso.objects.filter(cliente=cliente,glosa=glosa).aggregate(Sum('valor'))["valor__sum"],
				context["listGlosa"]),
				deuda(cliente,"deuda"),
				deuda(cliente,"boleta"),
				deuda(cliente,"deuda") - deuda(cliente,"boleta"),
				cliente.pk]),
			context["listCliente"])
		print(context["clienteGlosa"])
		return context

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

def deuda(cliente, tipo): 
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

		return redirect("list")

	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(self.__class__, self).dispatch(request, *args, **kwargs)

