"""Modulo per la gestione degli URLS per l'app Gestione"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PazienteListView.as_view(), name='home'),
    path('fatture/', views.FatturaListView.as_view(), name='fatture'),
    path('fattura/<int:pk>', views.FatturaDetailView.as_view(), name='dettaglio-fattura'),
    path('paziente/<int:pk>', views.PazienteDetailView.as_view(), name='dettaglio-paziente'),
]