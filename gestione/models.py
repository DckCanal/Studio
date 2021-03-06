from django.db import models
from datetime import date
from django.urls import reverse
from .utils import data_italiana, data_italiana_breve

class Paziente(models.Model):
	"""Classe per rappresentare il paziente."""
	
	cognome = models.CharField(max_length = 100, help_text = 'Cognome')
	nome = models.CharField(max_length = 100, help_text = 'Nome')
	
	codfisc = models.CharField("Codice fiscale", max_length = 16, help_text = 'Codice fiscale', blank = True)
	#inserire un Validator. Trovare il modo di segnalare la lunghezza fissa di 16 caratteri.
	
	piva = models.CharField('Partita Iva', max_length = 50, help_text = 'P. Iva', blank = True)
	
	paese = models.CharField('Città', max_length = 100, help_text = 'Città', blank = True)
	provincia = models.CharField(max_length = 2, help_text = 'Prov.', blank = True)
	#inserire anche qui un Validator, 2 caratteri maiuscoli

	cap = models.CharField('CAP', max_length = 5, help_text = 'CAP', blank = True)
	#validator anche qui
	
	via = models.CharField(max_length = 100, help_text = 'Via', blank = True)
	civico = models.CharField('N. civico', max_length = 30, help_text = 'N. civico', blank = True)
	
	telefono = models.CharField(max_length = 25, help_text = 'Telefono', blank = True)
	email = models.EmailField(help_text = 'email', blank = True)
	
	data_nascita  = models.DateField('Data di nascita', help_text = '', blank = True, null=True)
	
	paese_nascita = models.CharField('Città di nascita', max_length = 100, help_text = 'Città di nascita', blank = True)
	provincia_nascita = models.CharField('Provincia di nascita',max_length = 2, help_text = 'Prov. di nascita', blank = True)
	
	prezzo = models.DecimalField(help_text = 'Prezzo', max_digits = 8, decimal_places = 2, blank = True, default = 50.00)
	
	ultima_modifica = models.DateTimeField(help_text = 'Ultima modifica', auto_now = True)
	
	class Meta:
		ordering = ['cognome','nome']
		
	def __str__(self):
		return ' '.join([self.cognome, self.nome])
	
	def get_absolute_url(self):
		return reverse('dettaglio-paziente', args=[str(self.id)])

class Fattura(models.Model):
	"""Classe per rappresentare la fattura."""
	
	paziente = models.ForeignKey(Paziente, on_delete = models.SET_NULL, null = True, help_text = 'Intestatario (Paziente)')
	valore = models.DecimalField(help_text = 'Valore', max_digits = 8, decimal_places = 2)
	data = models.DateField(default = date.today, help_text = '')
	data_incasso = models.DateField(help_text='',null=True,blank=True)
	testo = models.CharField(max_length=300,help_text='Servizio eseguito',default='Trattamento massoterapico')
	
	numero = models.PositiveSmallIntegerField('Numero d\'ordine', help_text = 'Numero d\'ordine')
	
	class Meta:
		ordering = ['-data','-numero']
	
	def __str__(self):
		return str(self.numero) + " - " + data_italiana_breve(self.data)
		
	def get_absolute_url(self):
		return reverse('dettaglio-fattura', args=[str(self.id)])

	def get_year(self):
		return self.data.year
	
	def get_month(self):
	    return self.data.month
	
	def date_diverse(self):
		if self.data != self.data_incasso:
			return True
		else:
			return False

