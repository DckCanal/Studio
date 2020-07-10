from django.forms import ModelForm
from gestione.models import Fattura
from django.core.exceptions import ValidationError
from datetime import date

class NuovaFatturaForm(ModelForm):
    class Meta:
        model = Fattura
        fields = ['paziente','valore','data','numero']
        
        
    def clean_data(self):
        '''Data non nel futuro'''
        data = self.cleaned_data['data']
        if data > date.today():
            raise ValidationError('Data non valida - futuro')
        return data
    
    def clean_numero(self):
        '''Numero non esistente nell'anno corrente'''
        data = self.cleaned_data['numero']
        if Fattura.objects.filter(data__year=self.cleaned_data['data'].year).filter(numero__exact=data):
            raise ValidationError('Numero d\'ordine già presente')
        return data

    def clean_valore(self):
        '''Non negativo'''
        data = self.cleaned_data['valore']
        if data < 0:
            raise ValidationError('Valore non valido - negativo')
        return data
