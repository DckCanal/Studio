"""Modulo per la gestione degli URLS per l'app Gestione"""
from django.urls import path
from . import views
# API
from django.urls import include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'fatture', views.FatturaViewSet, basename='fattura')
router.register(r'pazienti', views.PazienteViewSet, basename='paziente')


urlpatterns = [
    path('', views.home_page, name='home'),
    path('pazienti/',views.PazienteListView.as_view(),name='pazienti'),
    path('fatture/', views.FatturaListView.as_view(), name='fatture'),
    path('fattura/<int:pk>', views.FatturaDetailView.as_view(), name='dettaglio-fattura'),
    path('paziente/<int:pk>', views.PazienteDetailView.as_view(), name='dettaglio-paziente'),
    path('fattura-pdf/<int:pk>',views.fattura_pdf,{'per_cliente':True},name='fattura-pdf'),
    path('fattura-commercialista/<int:pk>',views.fattura_pdf, {'per_cliente':False}, name='fattura-commercialista'),
    path('privacy-pdf/<int:pk>>',views.privacy_pdf,name='privacy-pdf'),
    path('consenso-pdf/<int:pk>',views.consenso_pdf,name='consenso-pdf'),
    path('privacy-m-pdf/<int:pk>',views.privacy_m_pdf,name='privacy-m-pdf'),
    path('consenso-m-pdf/<int:pk>',views.consenso_m_pdf,name='consenso-m-pdf'),
    path('nuovo-paziente',views.NuovoPaziente.as_view(),name='nuovo-paziente'),
    path('modifica-paziente/<int:pk>',views.ModificaPaziente.as_view(),name='modifica-paziente'),
    path('nuova-fattura',views.nuovaFattura,name='nuova-fattura'),
    path('fattura-veloce/<int:pzpk>',views.fatturaVeloce,name='fattura-veloce'),
    path('modifica-fattura/<int:pk>',views.ModificaFattura.as_view(),name='modifica-fattura'),
    path('incassa-fattura/<int:pk>',views.incassaOggi,name='incassa-oggi'),
    path('elimina-fattura/<int:pk>',views.FatturaDelete.as_view(),name='elimina-fattura'),
    path('elimina-paziente/<int:pk>',views.PazienteDelete.as_view(),name='elimina-paziente'),
    path('ajax_calls/search/', views.autocompleteModel, name='search'),
    # path('api-auth/', include('rest_framework.urls'))
    # path('api/fattura/<int:pk>',views.apiFattura),
    # path('api/fatture/',views.apiFatture),
    # path('api/paziente/<int:pk>',views.apiPaziente),
    # path('api/pazienti/',views.apiPazienti),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
