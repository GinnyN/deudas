# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Ingreso.glosa'
        db.alter_column(u'front_ingreso', 'glosa_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['front.Glosa'], null=True))

    def backwards(self, orm):

        # Changing field 'Ingreso.glosa'
        db.alter_column(u'front_ingreso', 'glosa_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['front.Glosa']))

    models = {
        u'front.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'activo': ('django.db.models.fields.CharField', [], {'default': "'activo'", 'max_length': '20'}),
            'duenio': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mensualidad': ('django.db.models.fields.IntegerField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'rut': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'natural'", 'max_length': '20'})
        },
        u'front.glosa': {
            'Meta': {'object_name': 'Glosa'},
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