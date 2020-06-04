# Generated by Django 3.0.6 on 2020-06-04 19:44

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paziente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cognome', models.CharField(blank=True, help_text='Cognome', max_length=100)),
                ('nome', models.CharField(blank=True, help_text='Nome', max_length=100)),
                ('codfisc', models.CharField(blank=True, help_text='Codice fiscale', max_length=16, verbose_name='Codice fiscale')),
                ('piva', models.CharField(help_text='P. Iva', max_length=50, verbose_name='Partita Iva')),
                ('paese', models.CharField(blank=True, help_text='Città', max_length=100, verbose_name='Città')),
                ('provincia', models.CharField(blank=True, help_text='Prov.', max_length=2)),
                ('cap', models.CharField(blank=True, help_text='CAP', max_length=5, verbose_name='CAP')),
                ('via', models.CharField(blank=True, help_text='Via', max_length=100)),
                ('civico', models.CharField(blank=True, help_text='N. civico', max_length=30, verbose_name='N. civico')),
                ('telefono', models.CharField(blank=True, help_text='Telefono', max_length=25)),
                ('email', models.EmailField(blank=True, help_text='email', max_length=254)),
                ('data_nascita', models.DateField(blank=True, help_text='Data di nascita <em>YYYY-MM-DD</em>.', verbose_name='Data di nascita')),
                ('paese_nascita', models.CharField(blank=True, help_text='Città di nascita', max_length=100, verbose_name='Città di nascita')),
                ('provincia_nascita', models.CharField(blank=True, help_text='Prov. di nascita', max_length=2, verbose_name='Provincia di nascita')),
                ('prezzo', models.DecimalField(blank=True, decimal_places=2, default=50.0, help_text='Prezzo', max_digits=8)),
            ],
            options={
                'ordering': ['cognome', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='Fattura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valore', models.DecimalField(decimal_places=2, help_text='Valore', max_digits=8)),
                ('data', models.DateField(default=datetime.date.today, help_text='Data <em>YYYY-MM-DD</em>.')),
                ('numero', models.PositiveSmallIntegerField(help_text="Numero d'ordine", verbose_name="Numero d'ordine")),
                ('paziente', models.ForeignKey(help_text='Intestatario (Paziente)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='gestione.Paziente')),
            ],
            options={
                'ordering': ['data', 'numero'],
            },
        ),
    ]