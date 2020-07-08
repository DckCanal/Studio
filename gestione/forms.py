from django.forms import ModelForm
from gestione.models import Paziente, Fattura

class NuovoPazienteForm(ModelForm):
    class Meta:
        model = Paziente
        fields = ['nome','cognome','codfisc','piva',
        'paese','provincia','cap','via','civico',
        'telefono','email','data_nascita','paese_nascita',
        'provincia_nascita','prezzo']

    def clean_codfisc(self):
        '''vuoto o 16 caratteri alfanumerici'''
        data = self.cleaned_data['codfisc']
        return data
    
    def clean_piva(self):
        '''vuoto o una p.iva valida'''
        data = self.cleaned_data['piva']
        return data
    
    def clean_provincia(self):
        '''due caratteri, da trasformare in maiuscoli'''
        data = self.cleaned_data['provincia']
        return data
    
    def clean_cap(self):
        '''5 cifre'''
        data = self.cleaned_data['cap']
        return data

class NuovaFatturaForm(ModelForm):
    fields = ['paziente','valore','data','numero']
    class Meta:
        model = Fattura
        
        
    def clean_data(self):
        '''Data non nel futuro'''
        data = self.cleaned_data['data']
        return data
    
    def clean_numero(self):
        '''Numero non esistente nell'anno corrente'''
        data = self.cleaned_data['numero']
        return data