from rest_framework import serializers
from .models import Fattura, Paziente


class FatturaSerializer(serializers.HyperlinkedModelSerializer):
    paziente = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Fattura
        fields = ['paziente', 'valore', 'data', 'data_incasso', 'testo', 'numero']


class PazienteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Paziente
        fields = ['pk','nome', 'cognome', 'codfisc', 'piva', 'paese', 'provincia' ,'cap', 'via', 'civico', 'telefono', 'email', 'data_nascita', 'paese_nascita', 'provincia_nascita', 'prezzo', 'ultima_modifica']
