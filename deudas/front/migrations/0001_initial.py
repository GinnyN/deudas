# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cliente'
        db.create_table(u'front_cliente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rut', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('tipo', self.gf('django.db.models.fields.CharField')(default='natural', max_length=20)),
            ('duenio', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('activo', self.gf('django.db.models.fields.CharField')(default='activo', max_length=20)),
            ('mensualidad', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'front', ['Cliente'])

        # Adding model 'Glosa'
        db.create_table(u'front_glosa', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('detalle', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'front', ['Glosa'])

        # Adding model 'Ingreso'
        db.create_table(u'front_ingreso', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('tipo', self.gf('django.db.models.fields.CharField')(default='deuda', max_length=20)),
            ('valor', self.gf('django.db.models.fields.IntegerField')()),
            ('numero', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('glosa', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.Glosa'], null=True, blank=True)),
            ('cliente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.Cliente'])),
        ))
        db.send_create_signal(u'front', ['Ingreso'])


    def backwards(self, orm):
        # Deleting model 'Cliente'
        db.delete_table(u'front_cliente')

        # Deleting model 'Glosa'
        db.delete_table(u'front_glosa')

        # Deleting model 'Ingreso'
        db.delete_table(u'front_ingreso')


    models = {
        u'front.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'activo': ('django.db.models.fields.CharField', [], {'default': "'activo'", 'max_length': '20'}),
            'duenio': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mensualidad': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'rut': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'natural'", 'max_length': '20'})
        },
        u'front.glosa': {
            'Meta': {'object_name': 'Glosa'},
            'detalle': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'front.ingreso': {
            'Meta': {'object_name': 'Ingreso'},
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['front.Cliente']"}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'glosa': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['front.Glosa']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numero': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'deuda'", 'max_length': '20'}),
            'valor': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['front']