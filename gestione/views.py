"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Max, Q
from .models import Paziente, Fattura
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from . import docgen
from gestione.forms import NuovaFatturaForm, ModificaFatturaForm
from datetime import date
from django.core import serializers
import json
import datetime
# API
from rest_framework import viewsets, permissions
from .serializers import FatturaSerializer, PazienteSerializer

@login_required
@permission_required('gestione.view_paziente')
def home_page(request):
    paz = Paziente.objects.all().order_by('-ultima_modifica')[:15]
    indici = [1,4,7,10,13]
    context = {
        'num_paz': len(paz),
        'paz':paz,
        'indici':indici,
    }
    return render(request,'gestione/home.html',context)

class PazienteListView(LoginRequiredMixin, generic.ListView):
    """View di elenco dei pazienti, home page del sito"""
    model = Paziente
    context_object_name = 'elenco_pazienti'
    paginate_by=25
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
    paginate_by=25
    permission_required = ('gestione.view_fattura','gestione.delete_fattura','gestione.view_paziente')
    def get_queryset(self):
        qs = Fattura.objects.all()
        anno = self.request.GET.get('anno','0')
        mese = self.request.GET.get('mese','0')
        paziente = self.request.GET.get('paziente','')
        if anno != '0':
            qs = qs.filter(data__year=anno)

        if mese != '0':
            qs = qs.filter(data__month=mese)

        incasso = self.request.GET.get('stato-incasso','tutte')

        if incasso == 'incassate':
            qs = qs.filter(data_incasso__isnull=False)
        elif incasso == 'da-incassare':
            qs = qs.filter(data_incasso__isnull=True)

        if paziente != '' and ', PK:' in paziente:
            qs = qs.filter(paziente=paziente.split(', PK:')[1])
        return qs
    
    def get_context_data(self,**kwargs):
        context = super(FatturaListView,self).get_context_data(**kwargs)
        years = list()

        fatt = Fattura.objects.all()
        for f in fatt:
            if (f.data.year) not in years:
                years.append(f.data.year)

        context['anni']=years

        if self.request.GET.get('anno'):# and self.request.GET.get('anno') != '0':
            context['anno_selezionato'] = int(self.request.GET.get('anno'))
        if self.request.GET.get('mese'):# and self.request.GET.get('mese') != '0':
            context['mese_selezionato'] = int(self.request.GET.get('mese'))
        if self.request.GET.get('stato-incasso'):
            context['stato_incasso_selezionato'] = self.request.GET.get('stato-incasso')
        if self.request.GET.get('paziente')  and ', PK:' in self.request.GET.get('paziente'):
            context['paziente_selezionato'] = self.request.GET.get('paziente')
        
        context['num_fatture'] = len(context['object_list'])
        
        return context

class FatturaDetailView(LoginRequiredMixin, generic.DetailView):
    """Vista di dettaglio della fattura, ovvero il file da stampare"""
    model = Fattura
    context_object_name = 'fattura'
    permission_required = ('gestione.view_fattura','gestione.delete_fattura','view.change_fattura','gestione.view_paziente')

@login_required
def fattura_pdf(request, pk, per_cliente):
    return docgen.genera_fattura(request,pk,per_cliente)

@login_required
def privacy_pdf(request,pk):
    """Generazione modulo privacy del paziente pk"""
    return docgen.genera_privacy(request,pk,False)

@login_required
def privacy_m_pdf(request,pk):
    return docgen.genera_privacy(request,pk,True)

@login_required
def consenso_pdf(request,pk):
    """Generazione modulo consenso informato del paziente pk"""
    return docgen.genera_consenso_informato(request,pk,False)

@login_required
def consenso_m_pdf(request,pk):
    return docgen.genera_consenso_informato(request,pk,True)

class NuovoPaziente(LoginRequiredMixin,CreateView):
    model = Paziente
    permission_required = ['gestione.add_paziente']
    fields = '__all__'
    exclude = ['ultima_modifica']

class ModificaPaziente(LoginRequiredMixin,UpdateView):
    model = Paziente
    fields = '__all__'
    exclude = ['ultima_modifica']
    permission_required = ['gestione.add_paziente']

class ModificaFattura(LoginRequiredMixin,UpdateView):
    model = Fattura
    permission_required = ['gestione.add_fattura']
    form_class = ModificaFatturaForm

@permission_required('gestione.add_fattura')
def nuovaFattura(request):
    if request.method == 'POST':
        form = NuovaFatturaForm(request.POST)
        if form.is_valid():            
            f = Fattura()
            f.paziente = form.cleaned_data['paziente']
            f.valore = form.cleaned_data['valore']
            f.data = form.cleaned_data['data']
            f.numero = form.cleaned_data['numero']
            f.data_incasso = form.cleaned_data['data_incasso']
            f.save()
            return HttpResponseRedirect(f.get_absolute_url())
    else:
        num = Fattura.objects.filter(data__year=date.today().year).aggregate(Max('numero'))['numero__max']
        if num is not None:
            num = num + 1
        else:
            num = 1
        form = NuovaFatturaForm(initial={'valore':50.00,'numero':num})
    context = {
        'form' : form,
    }
    
    return render(request,'gestione/fattura_form.html',context)

@permission_required('gestione.add_fattura')
def fatturaVeloce(request,pzpk):
    paz = get_object_or_404(Paziente,pk=pzpk)            
    f = Fattura()
    f.paziente = paz
    f.valore = paz.prezzo
    f.data = date.today()
    f.data_incasso = date.today()
    num = Fattura.objects.filter(data__year=date.today().year).aggregate(Max('numero'))['numero__max']
    if num is not None:
        num = num + 1
    else:
        num = 1
    f.numero = num
    f.save()
    return docgen.genera_fattura(request,f.pk, True)

        
@permission_required('gestione.add_fattura')
def incassaOggi(request,pk):
    f = get_object_or_404(Fattura,pk=pk)
    f.data_incasso = date.today()
    f.save()
    return HttpResponseRedirect(f.get_absolute_url())

class FatturaDelete(LoginRequiredMixin, DeleteView):
    model = Fattura
    success_url = reverse_lazy('fatture')
    permission_required = ['gestione.delete_fattura']

class PazienteDelete(LoginRequiredMixin, DeleteView):
    model = Paziente
    success_url = reverse_lazy('pazienti')
    permission_required = ['gestione.delete_paziente']

@permission_required('gestione.view_paziente')
def autocompleteModel(request):
    if request.method == 'GET':
        if 'term' in request.GET:
            qs = Paziente.objects.filter(Q(cognome__icontains=request.GET.get('term')) | Q(nome__icontains=request.GET.get('term')))
            paz = list()
            for p in qs:
                paz.append(' '.join([p.nome,p.cognome]) + ', PK:'+str(p.pk))
            return JsonResponse(paz,safe=False)
    elif request.method == 'POST':
        if 'txtSearch' in request.POST and ', PK:' in request.POST.get('txtSearch'):
            pk = request.POST.get('txtSearch').split(', PK:')[1]
            paz = Paziente.objects.get(pk=pk)
            return HttpResponseRedirect(paz.get_absolute_url())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# def apiFatture(request):
#     if request.method == 'GET':
#         fat = Fattura.objects.all()
#         #jfat = serializers.serialize('json',fat,fields = ('paziente','valore','data'))
#         #content = {
#         #    "status":"success",
#         #    "content":{
#         #        "fatture":jfat
#         #    }
#         #}
#         #return JsonResponse(jfat,safe=False)
#         return HttpResponse(serializers.serialize('json',fat), content_type='application/json')

# def apiFattura(request,pk):
#     if request.method == 'GET':
#         fat = get_object_or_404(Fattura,pk=pk)
#         return HttpResponse(serializers.serialize('json',[fat]),content_type='application/json')

# def apiPazienti(request):
#     if request.method == 'GET':
#         paz = Paziente.objects.all()
#         return HttpResponse(serializers.serialize('json',paz),content_type='application/json')

# def apiPaziente(request,pk):
#     if request.method == 'GET':
#         paz = get_object_or_404(Paziente,pk=pk)
#         return HttpResponse(serializers.serialize('json',[paz]),content_type='application/json')

class FatturaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows invoices to be viewed or edited.
    """
    serializer_class = FatturaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Fattura.objects.all().order_by('-data','-numero')
        
        anno = self.request.query_params.get('anno')
        if anno is not None:
            queryset = queryset.filter(data__year=anno)

        paziente = self.request.query_params.get('paziente')
        if paziente is not None:
            queryset = queryset.filter(paziente=paziente)
        
        # if paziente is None and anno is None:
            # queryset = queryset.filter(data__year=datetime.datetime.now().date().year)

        return queryset


class PazienteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    """
    queryset = Paziente.objects.all()
    serializer_class = PazienteSerializer
    permission_classes = [permissions.IsAuthenticated]