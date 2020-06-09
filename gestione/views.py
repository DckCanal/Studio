"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render
from django.views import generic
from .models import Paziente, Fattura

# Create your views here.

class PazienteListView(generic.ListView):
    model = Paziente

class PazienteDetailView(generic.DetailView):
    model = Paziente

class FatturaListView(generic.ListView):
    model = Fattura

class FatturaDetailView(generic.ListView):
    model = Fattura
