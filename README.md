# Gestione pazienti e fatture

Views:
	navbar sx: home (list_view paziente), fatture (list_view fatture)
	navbar dx: list_pazienti_ultima_modifica 15? con barra di ricerca
	
	home_page(list_pazienti[link->detail_view, elimina,genera_fattura_veloce], nuovo paziente)
		URL: '/pazienti'
	list_view fatture (link->detail_view, stampa pdf, elimina, link->nuova_fattura, filtri)
		URL: '/fatture'
	
	detail_view fattura, documento già in formato stampa?? (modifica, stampa pdf / download, elimina)
		URL: '/fattura/id'
#	list_view paziente (link->detail_view, elimina, genera_fattura_veloce)
	detail_view paziente (navbar_dx: elenco fattura del paziente con filtro sulla data, modifica dei campi, generazione moduli, ??editing scheda??, genera fattura[sia con prezzo specificato che standard])
		URL: 'paziente/id'
	
	nuovo paziente(compilazione dati e salvataggio, generazione moduli, genera fattura)
		URL: 'nuovopaziente'
	
