def aggiorna_ultima_modifica(sender, instance, **kwargs):
   instance.paziente.save()

