"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Paziente, Fattura
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from . import pdfgen

#Per limitare l'accesso ai soli utenti registrati nelle Classi, aggiungi come classe
#da cui ereditare, prima delle altre, LoginRequiredMixin. Al loro interno puoi specificare
#il campo login_url e redirect_field_name.

@login_required
@permission_required('gestione.view_paziente')
def home_page(request):
    paz = Paziente.objects.all().order_by('-ultima_modifica')[:15]
    context = {
        'num_paz': len(paz),
        'paz':paz,
    }
    return render(request,'gestione/home.html',context)

class PazienteListView(LoginRequiredMixin, generic.ListView):
    """View di elenco dei pazienti, home page del sito"""
    model = Paziente
    context_object_name = 'elenco_pazienti'
    permission_required = ('gestione.view_paziente','gestione.delete_paziente')


class PazienteDetailView(LoginRequiredMixin, generic.DetailView):
    """Vista dettagliata del paziente, per modifica e generazione di fattura"""
    model = Paziente
    context_object_name = 'paziente'
    #Dai permessi, ricava le azioni che farai da questa view!
    permission_required = ('gestione.view_paziente','gestione.change_paziente','gestione.delete_paziente','gestione.view_fattura','gestione.add_fattura','gestione.delete_fattura')


class FatturaListView(LoginRequiredMixin, generic.ListView):
    """Vista di elenco delle fatture, per la stampa o l'eliminazione"""
    model = Fattura
    context_object_name = 'elenco_fatture'
    permission_required = ('gestione.view_fattura','gestione.delete_fattura','gestione.view_paziente')


class FatturaDetailView(LoginRequiredMixin, generic.DetailView):
    """Vista di dettaglio della fattura, ovvero il file da stampare"""
    model = Fattura
    context_object_name = 'fattura'
    permission_required = ('gestione.view_fattura','gestione.delete_fattura','view.change_fattura','gestione.view_paziente')

@login_required
def fattura_pdf(request, pk):
    return pdfgen.genera_fattura(request,pk)

@login_required
def privacy_pdf(request,pk):
    """Generazione modulo privacy del paziente pk"""
    return pdfgen.genera_privacy(request,pk,False)

@login_required
def privacy_m_pdf(request,pk):
    return pdfgen.genera_privacy(request,pk,True)

@login_required
def consenso_pdf(request,pk):
    """Generazione modulo consenso informato del paziente pk"""
    return pdfgen.genera_consenso_informato(request,pk,False)

@login_required
def consenso_m_pdf(request,pk):
    return pdfgen.genera_consenso_informato(request,pk,True)

class NuovoPaziente(LoginRequiredMixin,CreateView):
    model = Paziente
    fields = ['nome','cognome','codfisc','piva',
        'paese','provincia','cap','via','civico',
        'telefono','email','data_nascita','paese_nascita',
        'provincia_nascita','prezzo']
    permission_required = ['gestione.add_paziente']

#Occorre passare a questa classe un argomento che sia la PK del paziente. Il campo
#paziente deve quindi essere oscurato ed il prezzo ricavato dal suo di default
class NuovaFattura(LoginRequiredMixin,CreateView):
    model = Fattura
    fields = ['paziente','valore','data','numero']
    permission_required = ['gestione.add_fattura']
    nuovoNumero = 5 #definire la query
    initial = {'valore':'50.00', 'numero':nuovoNumero}
    #success_url = reverse_lazy(f'fattura_pdf/{nuovoNumero}')

