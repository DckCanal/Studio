from django.apps import AppConfig
from django.db.models.signals import post_save
from .signals import aggiorna_ultima_modifica


class GestioneConfig(AppConfig):
    name = 'gestione'
    def ready(self):
        post_save.connect(aggiorna_ultima_modifica,sender='gestione.Fattura')