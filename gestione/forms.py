from django import forms
from django.forms import ModelForm
from gestione.models import Fattura, Paziente
from django.core.exceptions import ValidationError
from datetime import date

class NuovoPazienteForm(ModelForm):
    data_nascita = forms.DateField(input_formats=['%d/%m/%Y'])
    class Meta:
        model = Paziente
        fields = ['nome','cognome','codfisc','piva',
        'paese','provincia','cap','via','civico',
        'telefono','email','data_nascita','paese_nascita',
        'provincia_nascita','prezzo']

class NuovaFatturaForm(ModelForm):
    data = forms.DateField(input_formats=['%d/%m/%Y'])
    data_incasso = forms.DateField(input_formats=['%d/%m/%Y'])
    class Meta:
        model = Fattura
        fields = ['paziente','valore','data','numero','data_incasso','testo']
        
        
    def clean_data(self):
        '''Data non nel futuro'''
        data = self.cleaned_data['data']
        if data > date.today():
            raise ValidationError('Data non valida - futuro')
        return data
    
    def clean_numero(self):
        '''Numero non esistente nell'anno corrente'''
        data = self.cleaned_data['numero']
        f = Fattura.objects.filter(data__year=self.cleaned_data['data'].year).filter(numero__exact=data)
        if f:
            raise ValidationError(f'Numero d\'ordine già presente:{f[0]} a {f[0].paziente}')
        return data

    def clean_valore(self):
        '''Non negativo'''
        data = self.cleaned_data['valore']
        if data < 0:
            raise ValidationError('Valore non valido - negativo')
        return data
