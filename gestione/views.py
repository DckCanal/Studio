"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render
from django.views import generic
from .models import Paziente, Fattura

# Create your views here.

class PazienteListView(generic.ListView):
    """View di elenco dei pazienti, home page del sito"""
    model = Paziente
    context_object_name = 'elenco_pazienti'

class PazienteDetailView(generic.DetailView):
    """Vista dettagliata del paziente, per modifica e generazione di fattura"""
    model = Paziente
    context_object_name = 'paziente'

class FatturaListView(generic.ListView):
    """Vista di elenco delle fatture, per la stampa o l'eliminazione"""
    model = Fattura
    context_object_name = 'elenco_fatture'

class FatturaDetailView(generic.DetailView):
    """Vista di dettaglio della fattura, ovvero il file da stampare"""
    model = Fattura
    context_object_name = 'fattura'

#da definire, la View per l'inserimento di un nuovo paziente
