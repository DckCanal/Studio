from django.forms import ModelForm
from gestione.models import Fattura

class NuovaFatturaForm(ModelForm):
    class Meta:
        model = Fattura
        fields = ['paziente','valore','data','numero']
        
        
    def clean_data(self):
        '''Data non nel futuro'''
        data = self.cleaned_data['data']
        return data
    
    def clean_numero(self):
        '''Numero non esistente nell'anno corrente'''
        data = self.cleaned_data['numero']
        return data