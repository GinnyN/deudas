# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Cliente(models.Model):
	rut = models.CharField(max_length=12, verbose_name="RUT")
	nombre = models.CharField(max_length=1000, verbose_name="Nombre")
	tipo_opciones = (
        ('natural', u"Persona Natural"), 
        ('sociedad', u"Sociedad"))
	tipo = models.CharField(max_length=20, choices=tipo_opciones, default=tipo_opciones[0][0], verbose_name=u"Tipo")
	duenio = models.CharField(max_length=1000, verbose_name=u"Dueño", blank=True)
	activo_opciones = (
        ('activo', u"Activo"), 
        ('no-activo', u"No Activo"))
	activo = models.CharField(max_length=20, choices=activo_opciones, default=activo_opciones[0][0], verbose_name=u"Activo")
	mensualidad = models.IntegerField(verbose_name=u"Mensualidad", blank=True, null=True)

	def __unicode__(self):
        return self.nombre

class Glosa(models.Model):
	nombre = models.CharField(max_length=500, verbose_name=u"Nombre")
	detalle = models.TextField(verbose_name=u"Detalle")

	def __unicode__(self):
		return '%s' % self.nombre

class Ingreso(models.Model):
	fecha = models.DateTimeField(verbose_name=u"Fecha")
	tipo_opciones = (
        ('deuda', u"Deuda"), 
        ('boleta', u"Boleta"))
	tipo = models.CharField(max_length=20, choices=tipo_opciones, default=tipo_opciones[0][0], verbose_name=u"Tipo")
	valor = models.IntegerField(verbose_name=u"Valor", blank=True, null=True)
	numero = models.IntegerField(verbose_name=u"Numero de Boleta", blank=True)
	glosa = models.ForeignKey(Glosa, blank=True, null=True)
	cliente = models.ForeignKey(Cliente)

	def __unicode__(self):
        return self.cliente.nombre + " - " + self.glosa.nombre
	
