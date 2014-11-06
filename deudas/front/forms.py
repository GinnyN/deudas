from django import forms
from django.contrib.auth.models import User
from front import models
from datetime import date

class ClienteForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request', None)
		super (ClienteForm,self ).__init__(*args,**kwargs)
		self.fields['rut'].widget = forms.TextInput(attrs={'class': 'form-control', 'required':"required"})
		self.fields['nombre'].widget = forms.TextInput(attrs={'class': 'form-control', 'required':"required"})
		self.fields['duenio'].widget = forms.TextInput(attrs={'class': 'form-control'})
		self.fields['mensualidad'].widget = forms.NumberInput(attrs={'class': 'form-control'})

	class Meta:
		model = models.Cliente

class GlosaForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request', None)
		super (GlosaForm,self ).__init__(*args,**kwargs)
		self.fields['nombre'].widget = forms.TextInput(attrs={'class': 'form-control', 'required':"required"})
		self.fields["detalle"].widget = forms.Textarea(attrs={'class': 'form-control', 'required':"required"})

	class Meta:
		model = models.Glosa

class CobroForm(forms.ModelForm):
	fecha = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',
		attrs={'class': 'form-control datepicker', 'required':"required", "value":date.today().strftime("%d/%m/%Y")}), 
                                 input_formats=('%d/%m/%Y',))
	
	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request', None)
		super (CobroForm,self ).__init__(*args,**kwargs)
		self.fields['valor'].widget = forms.TextInput(attrs={'class': 'form-control', 'required':"required"})

	class Meta:
		model = models.Ingreso
		exclude = ["tipo","cliente","numero"]

class AbonoForm(forms.ModelForm):
	fecha = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',
		attrs={'class': 'form-control datepicker', 'required':"required", "value":date.today().strftime("%d/%m/%Y")}), 
                                 input_formats=('%d/%m/%Y',))
	
	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request', None)
		super (AbonoForm,self ).__init__(*args,**kwargs)
		self.fields['valor'].widget = forms.TextInput(attrs={'class': 'form-control', 'required':"required"})
		self.fields['numero'].widget = forms.NumberInput(attrs={'class': 'form-control', 'required':"required"})

	class Meta:
		model = models.Ingreso
		exclude = ["tipo","cliente"]

class ConfigForm(forms.ModelForm):

	class Meta:
		model = models.Config


