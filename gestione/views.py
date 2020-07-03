"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render
from django.views import generic
from .models import Paziente, Fattura
from django.contrib.auth.mixins import LoginRequiredMixin
from . import pdfgen

#Per limitare l'accesso ai soli utenti registrati nelle Classi, aggiungi come classe
#da cui ereditare, prima delle altre, LoginRequiredMixin. Al loro interno puoi specificare
#il campo login_url e redirect_field_name.

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

# per limitare accesso agli utenti registrati: @login_required
def home_page(request):
    paz = Paziente.objects.all().order_by('-ultima_modifica')[:15]
    context = {
        'num_paz': len(paz),
        'paz':paz,
    }
    return render(request,'gestione/home.html',context)


def fattura_pdf(request, pk):
    return pdfgen.genera_fattura(request,pk)

def privacy_pdf(request,pk):
    """Generazione modulo privacy del paziente pk"""
    return pdfgen.genera_privacy(request,pk,False)

def privacy_m_pdf(request,pk):
    return pdfgen.genera_privacy(request,pk,True)

def consenso_pdf(request,pk):
    """Generazione modulo consenso informato del paziente pk"""
    return pdfgen.genera_consenso_informato(request,pk,False)

def consenso_m_pdf(request,pk):
    return pdfgen.genera_consenso_informato(request,pk,True)


# da definire, la View per l'inserimento di un nuovo paziente
