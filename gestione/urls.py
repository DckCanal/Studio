"""Modulo per la gestione degli URLS per l'app Gestione"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('pazienti/',views.PazienteListView.as_view(),name='pazienti'),
    path('fatture/', views.FatturaListView.as_view(), name='fatture'),
    path('fattura/<int:pk>', views.FatturaDetailView.as_view(), name='dettaglio-fattura'),
    path('paziente/<int:pk>', views.PazienteDetailView.as_view(), name='dettaglio-paziente'),
    path('fattura-pdf/<int:pk>',views.fattura_pdf,name='fattura-pdf'),
    path('privacy-pdf/<int:pk>/<int:minorenne>',views.privacy_pdf,name='privacy-pdf'),
    path('consenso-pdf/<int:pk>/<int:minorenne>',views.consenso_pdf,name='consenso-pdf'),
]
