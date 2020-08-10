import datetime
from .models import Paziente, Fattura
import io
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .utils import data_italiana
from openpyxl import Workbook, load_workbook
from tempfile import NamedTemporaryFile
from docx import Document
from .models import Paziente

numCell = 'B10'
dataCell = 'B11'
nomeCell = 'D9'
indirizzoCell = 'D10'
CAPCell = 'D11'
ComuneCell = 'D12'
CFCell = 'D13'
PIvaCell = 'D14'
TestoCell = 'A20'
IDBolloCell = 'D29'
NettoCell = 'F36'
InpsCell = 'F35'
NoInpsCell = 'F34'
ImportoCell = 'E20'
PagamentoCell = 'A34'
DataPagamentoCell = 'B34'

def crea_dizionario(p:Paziente):
    d = {
        'xxxCognome':p.cognome,
        'xxxNome':p.nome,
        'xxxData':data_italiana(datetime.date.today()),
    }
    d['xxxCodFisc'] = 'C.F.: '+p.codfisc if p.codfisc else ''
    d['xxxPIva'] = 'P.Iva: '+p.piva if p.piva else ''
    if(p.data_nascita and p.paese_nascita and p.provincia_nascita):
        d['xxxNascita'] = (f'nato/a a {p.paese_nascita} ({p.provincia_nascita})'
        f' il {data_italiana(p.data_nascita)}')
    else:
        d['xxxNascita'] = ''
    if(p.paese and p.cap and p.via and p.provincia and p.civico):
        d['xxxResidenza'] = (f'e residente a {p.paese} ({p.provincia}),'
        f' {p.cap}, in {p.via} {p.civico}')
    else:
        d['xxxResidenza'] = ''

    return d

def sostituisci(d:Document, subs):
    for par in d.paragraphs:
        for key in subs:
            if key in par.text:
                inline = par.runs
                for i in range(len(inline)):
                    if key in inline[i].text:
                        text = inline[i].text.replace(key,subs[key])
                        inline[i].text = text
    b = io.BytesIO()
    d.save(b)
    b.seek(0)
    return b

def genera_fattura(request, pk, per_cliente):
    f = get_object_or_404(Fattura, pk=pk)
    p = f.paziente
    nome_file = str(f.numero) + '-' + str(f.get_month()) + '/' + str(f.get_year()) + ' - ' + str(p.cognome) + '.xlsx'
    w = load_workbook(filename='gestione/static/F.xltx')
    s = w.active
    
    s[numCell] = f.numero
    s[dataCell] = f.data
    s[nomeCell] = p.nome + ' ' + p.cognome
    if(p.codfisc):
        s[CFCell] = 'C.F.: ' + p.codfisc
    if(p.piva):
        s[PIvaCell] = 'P.Iva: ' + p.piva
    if(p.via and p.civico and p.cap and p.paese and p.provincia):
        s[indirizzoCell] = p.via + ' N. ' + p.civico
        s[CAPCell] = p.cap
        s[ComuneCell] = p.paese + ' (' + p.provincia + ')'
    s[TestoCell] = f.testo
    s[NettoCell] = f.valore
    s[ImportoCell] = f.valore
    noInps = float(f.valore)/1.04
    s[NoInpsCell] = noInps
    s[InpsCell] = float(f.valore)-noInps

    if not per_cliente and f.data != f.data_incasso:
        if f.data_incasso:
            s[PagamentoCell] = 'Pagamento: '
            s[DataPagamentoCell] = f.data_incasso
        else:
            s[PagamentoCell] = 'Non ancora pagata'

    b = io.BytesIO()
    w.save(b)
    b.seek(0)
    return FileResponse(b, as_attachment=True, filename=nome_file)

def genera_consenso_informato(request, pk, minorenne):
    p = get_object_or_404(Paziente, pk=pk)
    if minorenne:
        doc = Document('gestione/static/CI_m.docx')
    else:
        doc = Document('gestione/static/CI.docx')
    subs = crea_dizionario(p)
    b = sostituisci(doc,subs)
    return FileResponse(b, as_attachment=True, filename='Consenso informato.docx')

def genera_privacy(request, pk, minorenne):
    p = get_object_or_404(Paziente,pk=pk)
    if minorenne:
        doc = Document('gestione/static/P_m.docx')
    else:
        doc = Document('gestione/static/P.docx')
    subs = crea_dizionario(p)
    b = sostituisci(doc,subs)
    return FileResponse(b, as_attachment=True, filename='Privacy.docx')

# def genera_fattura_pdf(request, pk, per_cliente):
#     title_style=ParagraphStyle('title',parent=styles['Normal'],fontName='Helvetica',fontSize=21, leading=25)#,spaceAfter=15)    
#     subtitle_style=ParagraphStyle('subtitle',parent=styles['Normal'],fontName='Helvetica',fontSize=18, leading=23)#,spaceAfter=25)
#     info_style=ParagraphStyle('info',parent=styles['Normal'],fontName='Helvetica',fontSize=12,leading=15)
#     heading_style=ParagraphStyle('heading',parent=styles['Normal'],fontName='Helvetica',fontSize=12, leading=15)#,spaceAfter=10)
#     bottom_style=ParagraphStyle('bottom',parent=styles['Normal'],fontName='Helvetica',fontSize=9,leading=12)
    
#     f = Fattura.objects.get(id=pk)
#     paz = f.paziente
#     nome_file = str(f.numero) + "-" + str(f.get_month()) + "/" + str(f.get_year()) + ".pdf"

#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer)
#     Story = []
#     style = styles["Normal"]

#     p = Paragraph('Marco De Canal', title_style)
#     Story.append(p)
#     Story.append(Paragraph('Massofisioterapista',subtitle_style))
#     Story.append(Spacer(1, 0.3*inch))

#     text = '''
#         <i>Sede legale:</i> Via Brescia 205B, 47842, S. Giovanni in M.no (RN)<br/>
#         <i>C.F.:</i> DCNMRC90L25D142Z<br/>
#         <i>P.IVA:</i> 04370000400<br/>
#     '''
#     p = Paragraph(text, info_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))

#     text = '''
#         <i>Telefono: </i> +39 338 533 0241<br/>
#         <i>email: </i> marco.decanal@gmail.com<br/>
#         <i>Indirizzo studio: </i> Via XX Settembre 1, 47842, S. Giovanni in M.no (RN)<br/>
#     '''
#     p = Paragraph(text, info_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.6*inch))

#     text = f"Spett.le {paz.cognome} {paz.nome}"
#     if(paz.codfisc):
#         text += f"<br/>Cod. fisc: {paz.codfisc}"
#     if(paz.piva):
#         text += f"<br/>P. Iva: {paz.piva}"
#     if(paz.via and paz.civico and paz.cap and paz.paese and paz.provincia):
#         text += f"<br/> {paz.via} {paz.civico}, {paz.cap}, {paz.paese} ({paz.provincia})<br/>"

#     p = Paragraph(text, heading_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.7*inch))

#     data_fat = data_italiana(f.data)
#     text = f"Fattura numero {f.numero} del {data_fat}"

#     p = Paragraph(text, heading_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))

#     val = float(f.valore)
#     senza_rivalsa = val/1.04
#     rivalsa = val-senza_rivalsa
#     data = [["Trattamento massoterapico", f"{senza_rivalsa:.2f}"],
#             ["Rivalsa INPS 4%", f"{rivalsa:.2f}"],
#             ["Netto a pagare", f"{val:.2f}"]]
#     t = Table(data,[4.5*inch,1.5*inch],3*[0.4*inch])
#     t.setStyle(TableStyle([
#         ('GRID', (0, 0), (1,2), 1, colors.black),
#         ('VALIGN',(0,0),(1,2),'MIDDLE'),
#         ('ALIGN',(1,0),(1,2),'CENTER')
#     ]))
#     Story.append(t)
    

#     if not per_cliente and f.data != f.data_incasso:
#         Story.append(Spacer(1,0.2*inch))
#         if f.data_incasso:
#             data_incasso = data_italiana(f.data_incasso)
#             Story.append(Paragraph(f'Pagata il {data_incasso}',info_style))
#         else:
#             Story.append(Paragraph('Non ancora pagata',info_style))
#     Story.append(Spacer(1, 1*inch))
#     text = '''
#         Operazione senza applicazione dell’Iva ai sensi Legge
#         190 del 23/12/2014 art. 1, commi da 54 a 89.<br/><br/>
#         Operazione effettuata ai sensi art. 1, commi da 54 a 89,
#         della Legge 190 del 23/12/2014 – Regime forfetario.<br/>
#         Il compenso non soggetto a ritenute d’acconto ai sensi della Legge
#         190 del 23/12/2014, art. 1 comma 67.<br/><br/>
#         Vi informiamo che tutti i dati a Voi relativi in nostro possesso verranno inseriti
#         in un apposito archivio, ai sensi della L. 196/03. Tale trattamento è finalizzato
#         all’adempimento di norme di Legge, di obblighi contabili, fiscali, commerciali
#         per scopi interni, e nei limiti richiesti dall’adempimento dell’incarico
#         (incluso corrieri, se previsti, e banche, per incassi e pagamenti). Al di
#         fuori di questi casi non è prevista la divulgazione e/o diffusione di dati a terzi.<br/>
#     '''
#     p = Paragraph(text, bottom_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))

#     doc.build(Story)
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename=nome_file)


# def genera_consenso_informato_pdf(request, pk, minorenne):
#     paz = Paziente.objects.get(pk=pk)
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
#     Story = []
#     style = styles["Normal"]
    
#     title_style=ParagraphStyle('title',parent=style,fontName='Helvetica',fontSize=15, leading=18,alignment=1)
#     body_style=ParagraphStyle('body',parent=style,fontName='Helvetica',fontSize=10,leading=12,spaceBefore=2)
#     heading_style=ParagraphStyle('heading',parent=style,fontName='Helvetica',fontSize=11,leading=13,alignment=1)
#     footer_style=ParagraphStyle('footer',parent=style,fontName='Helvetica',fontSize=10,leading=12,alignment=2)

#     text = 'il Salice - studio di massofisioterapia e tecniche osteopatiche'
#     p = Paragraph(text,title_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))
    
#     text = '<font size="11">MODULO DI CONSENSO INFORMATO AL TRATTAMENTO MASSOFISIOTERAPICO</font>'
#     p = Paragraph(text,title_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))
    
#     text = ''
#     if(not minorenne):
#         text = 'Io sottoscritto '
#     else:
#         text = '''
#         Io sottoscritto/a _______________________________________________, 
#         C.F./P.Iva_________________________
#         nato/a a_______________________________ il__/__/____ e residente 
#         a____________________________________ (____)
#         in via_______________________________________ N° __________
#         '''
#         text += '<br/>in qualità di Genitore/Rappresentante legale di '

#     text += f'{paz.nome} {paz.cognome}, '
#     if(paz.codfisc):
#         text += f'codice fiscale {paz.codfisc} '
#     if(paz.piva):
#         text += f'partita IVA {paz.piva} '
#     if(paz.data_nascita and paz.paese_nascita and paz.provincia_nascita):
#         text += f'<br/>nato/a a {paz.paese_nascita} ({paz.provincia_nascita}) il {paz.data_nascita} '
#     if(paz.paese and paz.cap and paz.via and paz.provincia and paz.civico):
#         text += f'<br/>residente a {paz.paese} ({paz.provincia}), {paz.cap}, in {paz.via} {paz.civico} '
#     p = Paragraph(text,body_style)
    
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))

#     Story.append(Paragraph('DICHIARO',heading_style))
#     Story.append(Spacer(1,0.2*inch))

#     Story.append(Paragraph('''di essere stato/a informato/a in modo
#     chiaro ed esauriente da Marco De Canal massofisioterapista
#     ''',body_style))

#     text = 'sul tipo di trattamento proposto: tecniche, materiali e mezzi utilizzati;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'sulle possibili conseguenze derivanti dalla mancata esecuzione del trattamento suddetto;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'sui benefici attesi, i rischi presunti e le eventuali complicanze ed effetti collaterali;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'sui comportamenti da mettere in atto onde evitare e/o limitare eventuali complicanze durante e dopo il trattamento;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'sulla possibilità di interrompere liberamente ed in qualsiasi momento il trattamento;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'sull’impossibilità a procedere nel trattamento in caso di mancata sottoscrizione del presente consenso.'
#     Story.append(Paragraph(text,body_style,'-'))
#     Story.append(Spacer(1,0.2*inch))

#     Story.append(Paragraph('DICHIARO INOLTRE DI',heading_style))
#     Story.append(Spacer(1,0.2*inch))

#     text = 'aver pienamente compreso quanto mi è stato verbalmente detto relativamente al trattamento proposto;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'aver avuto l’opportunità di porre domande chiarificatrici e di aver avuto risposte soddisfacenti;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'essere stato/a informato/a dei motivi che consigliano il trattamento proposto e sulla qualità della mia vita in caso di rifiuto;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'aver avuto il tempo sufficiente per decidere;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'essere consapevole che la decisione di accettare il trattamento proposto è volontaria e che posso ritirare il consenso in qualsiasi momento;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'essere stato/a informato/a che tutti i miei dati personali e di salute saranno trattati ai sensi del Regolamento UE 2016/679 relativo alla protezione delle persone fisiche con riguardo al trattamento di dati personali;'
#     Story.append(Paragraph(text,body_style,'-'))
#     text = 'essere stato/a informato/a che per ogni problema o eventuali ulteriori informazioni dovrò rivolgermi a Marco De Canal'
#     Story.append(Paragraph(text,body_style,'-'))
#     Story.append(Spacer(1,0.4*inch))

#     Story.append(Paragraph('PERTANTO ACCONSENTO AL TRATTAMENTO',heading_style))
#     Story.append(Spacer(1,0.3*inch))

#     data = data_italiana(datetime.date.today())
#     Story.append(Paragraph(f'San Giovanni in Marignano, {data}',body_style))
#     if (not minorenne):
#         Story.append(Paragraph(f'{paz.nome} {paz.cognome}',body_style))
#     else:
#         Story.append(Paragraph('Nome e cognome ____________________', body_style))
#     Story.append(Paragraph('Firma: _______________________________________',body_style))
#     Story.append(Spacer(1,0.4*inch))

#     Story.append(Paragraph('De Canal Marco<br/>P.Iva 04370000400<br/>Via Brescia 205/B, San Giovanni in Marignano (RN)',footer_style))

#     doc.build(Story)
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename='consenso informato.pdf')

# def genera_privacy_pdf(request, pk, minorenne):
#     paz = Paziente.objects.get(pk=pk)
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
#     Story = []
#     style = styles["Normal"]
    
#     title_style=ParagraphStyle('title',parent=style,fontName='Helvetica',fontSize=15, leading=18,alignment=1)
#     body_style=ParagraphStyle('body',parent=style,fontName='Helvetica',fontSize=9,leading=10,spaceAfter=2)
#     heading_style=ParagraphStyle('heading',parent=style,fontName='Helvetica',fontSize=11,leading=13,spaceBefore=2,alignment=1)
#     footer_style=ParagraphStyle('footer',parent=style,fontName='Helvetica',fontSize=9,leading=10,alignment=2)

#     text = 'il Salice - studio di massofisioterapia e tecniche osteopatiche'
#     p = Paragraph(text,title_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))
    
#     text = '''<font size="11">AUTORIZZAZIONE AL TRATTAMENTO DEI DATI RELATIVI 
#     ALLA SALUTE - INFORMATIVA AI SENSI DELL’ART. 13 DEL REG. UE 2016/679</font>'''
#     p = Paragraph(text,title_style)
#     Story.append(p)
#     Story.append(Spacer(1, 0.2*inch))

#     if(paz.nome and paz.nome and not minorenne):
#         Story.append(Paragraph(f'Gentile Sig.\\Sig.ra {paz.nome} {paz.cognome}',body_style))
#     else:
#         Story.append(Paragraph('Gentile Sig.\\Sig.ra __________________________________',body_style))
    
#     Story.append(Paragraph('''
#     ai sensi dell’art. 13 del Regolamento Europeo 2016/679 (di seguito Reg. UE), 
#     ed in relazione ai dati personali di cui il sottoscritto Marco De Canal 
#     entrerà in possesso, La informo di quanto segue:
#     ''',body_style))

#     Story.append(Paragraph('''
#     1 - FINALITÀ DEL TRATTAMENTO DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     Il trattamento dei dati è finalizzato unicamente alla corretta e completa esecuzione 
#     del mio incarico professionale connesso con le attività di valutazione massofisioterapica, 
#     prevenzione, cura e riabilitazione da me svolte a tutela della sua salute.
#     ''',body_style))

#     Story.append(Paragraph('''
#     2 - MODALITÀ DEL TRATTAMENTO DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     Il trattamento dei dati è realizzato per mezzo delle operazioni o complesso di 
#     operazioni indicate all’art. 2 del Reg. UE. Il trattamento dei dati è svolto dal Titolare.
#     ''',body_style))

#     Story.append(Paragraph('''
#     3 - CONFERIMENTO DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     Il conferimento dei dati personali e relativi alla salute è strettamente 
#     necessario ai fini dello svolgimento delle attività di cui al punto 1.
#     ''',body_style))

#     Story.append(Paragraph('''
#     4 - RIFIUTO DI CONFERIMENTO DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     L’eventuale rifiuto da parte sua di conferire dati personali nel caso 
#     di cui al punto 3 comporta l’impossibilità di adempiere alle attività di cui al punto 1.
#     ''',body_style))

#     Story.append(Paragraph('''
#     5 - COMUNICAZIONE DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     I dati personali possono essere conosciuti dagli incaricati del trattamento 
#     e possono essere comunicati per le finalità di cui al punto 1 a familiari, 
#     fiscalisti, collaboratori interni, soggetti comunque operanti nel settore 
#     medico\fisioterapico e, in genere, a tutti quei soggetti cui la comunicazione 
#     sia necessaria per il corretto adempimento delle finalità indicate nel punto 1.
#     ''',body_style))

#     Story.append(Paragraph('''
#     6 - DIFFUSIONE DEI DATI
#     ''',heading_style))
#     Story.append(Paragraph('''
#     I dati personali non sono soggetti a diffusione. Per lo svolgimento 
#     del presente incarico, Marco De Canal potrà altresì venire a conoscenza 
#     ed utilizzare dati relativi alla salute per il trattamento dei quali, 
#     in ottemperanza alle disposizioni normative sopra richiamate (art. 6 del Reg. UE), 
#     è con la presente a richiedere espresso consenso. I dati verranno conservati, 
#     per il periodo di tempo previsto dalla normativa comunitaria, da leggi, o da 
#     regolamenti. I dati potranno essere comunicati a soggetti pubblici o privati, 
#     nei limiti strettamente pertinenti all’espletamento dell’incarico conferito e 
#     nel rispetto, in ogni caso, del segreto professionale.
#     ''',body_style))

#     Story.append(Paragraph('''
#     7 - DIRITTI DELL’INTERESSATO
#     ''',heading_style))
#     Story.append(Paragraph('''
#     Gli artt. 15, 16, 17, 18, 20 e 21 del Reg. UE le conferiscono l’esercizio di specifici 
#     diritti, tra cui quello di ottenere dal Titolare la conferma dell’esistenza o meno 
#     di propri dati personali e la loro messa disposizione in forma intelligibile; lei ha 
#     diritto di avere conoscenza dell’origine dei dati, della finalità e delle modalità del 
#     trattamento, della logica applicata al trattamento, degli estremi identificativi del 
#     Titolare e dei soggetti cui i dati possono essere comunicati; ha inoltre diritto di 
#     ottenere la rettifica, la cancellazione, la limitazione al trattamento, la portabilità 
#     e l’opposizione al trattamento dei dati.
#     ''',body_style))

#     Story.append(Paragraph('''
#     8 - TITOLARE DEL TRATTAMENTO
#     ''',heading_style))
#     Story.append(Paragraph('''
#     Titolare del trattamento è Marco De Canal, via XX Settembre 1, 
#     San Giovanni in Marignano (RN).
#     ''',body_style))
    
#     Story.append(Spacer(1, 0.2*inch))



#     text = ''
#     if(not minorenne):
#         text = 'Io sottoscritto '
#     else:
#         text = '''
#         Io sottoscritto/a _______________________________________________, 
#         C.F./P.Iva_________________________
#         nato/a a_______________________________ il__/__/____ e residente 
#         a____________________________________ (____)
#         in via_______________________________________ N° __________
#         '''
#         text += '<br/>in qualità di Genitore/Rappresentante legale di '
#     text += f'{paz.nome} {paz.cognome}, '
#     if(paz.codfisc):
#         text += f'codice fiscale {paz.codfisc} '
#     if(paz.piva):
#         text += f'partita IVA {paz.piva} '
#     if(paz.data_nascita and paz.paese_nascita and paz.provincia_nascita):
#         text += f'<br/>nato/a a {paz.paese_nascita} ({paz.provincia_nascita}) il {paz.data_nascita} '
#     if(paz.paese and paz.cap and paz.via and paz.provincia and paz.civico):
#         text += f'<br/>residente a {paz.paese} ({paz.provincia}), {paz.cap}, in {paz.via} {paz.civico} '
    
#     text += '''
#     acquisite le summenzionate informazioni fornitemi dal Titolare del 
#     trattamento ai sensi dell’art. 13 del Reg. UE, e consapevole, 
#     in particolare che il trattamento potrà riguardare dati relativi alla salute, 
#     presto il mio consenso per il trattamento dei dati, anche dati sanitari, 
#     necessari allo svolgimento delle operazioni indicate nell’informativa.
#     '''
#     Story.append(Paragraph(text,body_style))
#     Story.append(Spacer(1, 0.2*inch))

#     data = data_italiana(datetime.date.today())
#     Story.append(Paragraph(f'San Giovanni in Marignano, {data}',body_style))
#     if (not minorenne):
#         Story.append(Paragraph(f'{paz.nome} {paz.cognome}',body_style))
#     else:
#         Story.append(Paragraph('Nome e cognome ____________________', body_style))
#     Story.append(Paragraph('Firma: _______________________________________',body_style))
#     Story.append(Spacer(1,0.4*inch))

#     Story.append(Paragraph('De Canal Marco<br/>P.Iva 04370000400<br/>Via Brescia 205/B, San Giovanni in Marignano (RN)',footer_style))
    
#     doc.build(Story)
#     buffer.seek(0)
#     return FileResponse(buffer, as_attachment=True, filename='privacy.pdf')
