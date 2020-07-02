"""Modulo con le views di pazienti e fatture"""
import datetime
from django.shortcuts import render
from django.views import generic
from .models import Paziente, Fattura
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.contrib.auth.mixins import LoginRequiredMixin
styles = getSampleStyleSheet()
mese = {
    1:'gennaio',
    2:'febbraio',
    3:'marzo',
    4:'aprile',
    5:'maggio',
    6:'giugno',
    7:'luglio',
    8:'agosto',
    9:'settembre',
    10:'ottobre',
    11:'novembre',
    12:'dicembre'
}

# Create your views here.
#Per limitare l'accesso ai soli utenti registrati nelle Classi, aggiungi come classe
#da cui ereditare, prima delle altre, LoginRequiredMixin. Al loro interno puoi specificare
#il campo login_url e redirect_field_name.

class PazienteListView(generic.ListView):
    """View di elenco dei pazienti, home page del sito"""
    model = Paziente
    context_object_name = 'elenco_pazienti'


class PazienteDetailView(generic.DetailView):
    """Vista dettagliata del paziente, per modifica e generazione di fattura"""
    model = Paziente
    context_object_name = 'paziente'


class FatturaListView(generic.ListView):
    """Vista di elenco delle fatture, per la stampa o l'eliminazione"""
    model = Fattura
    context_object_name = 'elenco_fatture'


class FatturaDetailView(generic.DetailView):
    """Vista di dettaglio della fattura, ovvero il file da stampare"""
    model = Fattura
    context_object_name = 'fattura'

# per limitare accesso agli utenti registrati: @login_required
def home_page(request):
    paz = Paziente.objects.all().order_by('-ultima_modifica')[:15]
    context = {
        'num_paz': len(paz),
        'paz':paz,
    }
    return render(request,'gestione/home.html',context)


def fattura_pdf(request, pk):

    title_style=ParagraphStyle('title',parent=styles['Normal'],fontName='Helvetica',fontSize=21, leading=25)#,spaceAfter=15)    
    subtitle_style=ParagraphStyle('subtitle',parent=styles['Normal'],fontName='Helvetica',fontSize=18, leading=23)#,spaceAfter=25)
    info_style=ParagraphStyle('info',parent=styles['Normal'],fontName='Helvetica',fontSize=12,leading=15)
    heading_style=ParagraphStyle('heading',parent=styles['Normal'],fontName='Helvetica',fontSize=12, leading=15)#,spaceAfter=10)
    bottom_style=ParagraphStyle('bottom',parent=styles['Normal'],fontName='Helvetica',fontSize=9,leading=12)
    
    f = Fattura.objects.get(id=pk)
    paz = f.paziente
    nome_file = str(f.numero) + "-" + str(f.get_month()) + "/" + str(f.get_year()) + ".pdf"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    Story = []#Spacer(1, 0.2*inch)]
    style = styles["Normal"]

    p = Paragraph('Marco De Canal', title_style)
    Story.append(p)
    Story.append(Paragraph('Massofisioterapista',subtitle_style))
    Story.append(Spacer(1, 0.3*inch))

    text = '''
        <i>Sede legale:</i> Via Brescia 205B, 47842, S. Giovanni in M.no (RN)<br/>
        <i>C.F.:</i> DCNMRC90L25D142Z<br/>
        <i>P.IVA:</i> 04370000400<br/>
    '''
    p = Paragraph(text, info_style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    text = '''
        <i>Telefono: </i> +39 338 533 0241<br/>
        <i>email: </i> marco.decanal@gmail.com<br/>
        <i>Indirizzo studio: </i> Via XX Settembre 1, 47842, S. Giovanni in M.no (RN)<br/>
    '''
    p = Paragraph(text, info_style)
    Story.append(p)
    Story.append(Spacer(1, 0.6*inch))

    text = f"Spett.le {paz.cognome} {paz.nome}"
    if(paz.codfisc):
        text += f"<br/>Cod. fisc: {paz.codfisc}"
    if(paz.piva):
        text += f"<br/>P. Iva: {paz.piva}"
    if(paz.via and paz.civico and paz.cap and paz.paese and paz.provincia):
        text += f"<br/> {paz.via} {paz.civico}, {paz.cap}, {paz.paese} ({paz.provincia})<br/>"

    p = Paragraph(text, heading_style)
    Story.append(p)
    Story.append(Spacer(1, 0.7*inch))

    text = f"Fattura numero {f.numero} del {f.data}"

    p = Paragraph(text, heading_style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    val = float(f.valore)
    senza_rivalsa = val/1.04
    rivalsa = val-senza_rivalsa
    data = [["Trattamento massoterapico", f"{senza_rivalsa:.2f}"],
            ["Rivalsa INPS 4%", f"{rivalsa:.2f}"],
            ["Netto a pagare", f"{val:.2f}"]]
    t = Table(data,[4.5*inch,1.5*inch],3*[0.4*inch])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (1,2), 1, colors.black),
        ('VALIGN',(0,0),(1,2),'MIDDLE'),
        ('ALIGN',(1,0),(1,2),'CENTER')
    ]))
    Story.append(t)
    Story.append(Spacer(1, 1*inch))

    text = '''
        Operazione senza applicazione dell’Iva ai sensi Legge
        190 del 23/12/2014 art. 1, commi da 54 a 89.<br/><br/>
        Operazione effettuata ai sensi art. 1, commi da 54 a 89,
        della Legge 190 del 23/12/2014 – Regime forfetario.<br/>
        Il compenso non soggetto a ritenute d’acconto ai sensi della Legge
        190 del 23/12/2014, art. 1 comma 67.<br/><br/>
        Vi informiamo che tutti i dati a Voi relativi in nostro possesso verranno inseriti
        in un apposito archivio, ai sensi della L. 196/03. Tale trattamento è finalizzato
        all’adempimento di norme di Legge, di obblighi contabili, fiscali, commerciali
        per scopi interni, e nei limiti richiesti dall’adempimento dell’incarico
        (incluso corrieri, se previsti, e banche, per incassi e pagamenti). Al di
        fuori di questi casi non è prevista la divulgazione e/o diffusione di dati a terzi.<br/>
    '''
    p = Paragraph(text, bottom_style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    doc.build(Story)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=nome_file)

def privacy_pdf(request,pk):
    """Generazione modulo privacy del paziente pk"""
    paz = Paziente.objects.get(pk=pk)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    Story = []
    style = styles["Normal"]
    


    doc.build(Story)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='privacy.pdf')

def consenso_pdf(request,pk):
    """Generazione modulo consenso informato del paziente pk"""
    paz = Paziente.objects.get(pk=pk)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    Story = []
    style = styles["Normal"]
    
    title_style=ParagraphStyle('title',parent=styles['Normal'],fontName='Helvetica',fontSize=15, leading=18,alignment=1)
    body_style=ParagraphStyle('body',parent=styles['Normal'],fontName='Helvetica',fontSize=10,leading=12,spaceBefore=2)
    heading_style=ParagraphStyle('heading',parent=styles['Normal'],fontName='Helvetica',fontSize=11,leading=13,alignment=1)
    footer_style=ParagraphStyle('footer',parent=styles['Normal'],fontName='Helvetica',fontSize=11,leading=13,alignment=2)

    text = 'il Salice - studio di massofisioterapia e tecniche osteopatiche'
    p = Paragraph(text,title_style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))
    
    text = '<font size="11">MODULO DI CONSENSO INFORMATO AL TRATTAMENTO MASSOFISIOTERAPICO</font>'
    p = Paragraph(text,title_style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))
    
    text = f'Io sottoscritto {paz.nome} {paz.cognome}, '
    if(paz.codfisc):
        text += f'codice fiscale {paz.codfisc} '
    if(paz.piva):
        text += f'partita IVA {paz.piva} '
    if(paz.data_nascita and paz.paese_nascita and paz.provincia_nascita):
        text += f'<br/>nato/a a {paz.paese_nascita} ({paz.provincia_nascita}) il {paz.data_nascita} '
    if(paz.paese and paz.cap and paz.via and paz.provincia and paz.civico):
        text += f'<br/>residente a {paz.paese} ({paz.provincia}), {paz.cap}, in {paz.via} {paz.civico} '
    p = Paragraph(text,body_style)
    
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    Story.append(Paragraph('DICHIARO',heading_style))
    Story.append(Spacer(1,0.2*inch))

    Story.append(Paragraph('''di essere stato/a informato/a in modo
    chiaro ed esauriente da Marco De Canal massofisioterapista
    ''',body_style))
    #Story.append(Spacer(1,0.2*inch))

    text = 'sul tipo di trattamento proposto: tecniche, materiali e mezzi utilizzati;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'sulle possibili conseguenze derivanti dalla mancata esecuzione del trattamento suddetto;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'sui benefici attesi, i rischi presunti e le eventuali complicanze ed effetti collaterali;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'sui comportamenti da mettere in atto onde evitare e/o limitare eventuali complicanze durante e dopo il trattamento;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'sulla possibilità di interrompere liberamente ed in qualsiasi momento il trattamento;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'sull’impossibilità a procedere nel trattamento in caso di mancata sottoscrizione del presente consenso.'
    Story.append(Paragraph(text,body_style,'-'))
    Story.append(Spacer(1,0.2*inch))

    Story.append(Paragraph('DICHIARO INOLTRE DI',heading_style))
    Story.append(Spacer(1,0.2*inch))

    text = 'aver pienamente compreso quanto mi è stato verbalmente detto relativamente al trattamento proposto;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'aver avuto l’opportunità di porre domande chiarificatrici e di aver avuto risposte soddisfacenti;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'essere stato/a informato/a dei motivi che consigliano il trattamento proposto e sulla qualità della mia vita in caso di rifiuto;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'aver avuto il tempo sufficiente per decidere;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'essere consapevole che la decisione di accettare il trattamento proposto è volontaria e che posso ritirare il consenso in qualsiasi momento;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'essere stato/a informato/a che tutti i miei dati personali e di salute saranno trattati ai sensi del Regolamento UE 2016/679 relativo alla protezione delle persone fisiche con riguardo al trattamento di dati personali;'
    Story.append(Paragraph(text,body_style,'-'))
    text = 'essere stato/a informato/a che per ogni problema o eventuali ulteriori informazioni dovrò rivolgermi a Marco De Canal'
    Story.append(Paragraph(text,body_style,'-'))
    Story.append(Spacer(1,0.4*inch))

    Story.append(Paragraph('PERTANTO ACCONSENTO AL TRATTAMENTO',heading_style))
    Story.append(Spacer(1,0.3*inch))

    data = datetime.date.today()
    datastr=str(data.day)+" "+mese[data.month]+" "+str(data.year)
    Story.append(Paragraph(f'San Giovanni in Marignano, {datastr}',body_style))
    Story.append(Paragraph(f'{paz.nome} {paz.cognome}',body_style))
    Story.append(Paragraph('Firma: _______________________________________',body_style))
    Story.append(Spacer(1,0.4*inch))

    Story.append(Paragraph('De Canal Marco<br/>P.Iva 04370000400<br/>Via Brescia 205/B, San Giovanni in Marignano (RN)',footer_style))

    doc.build(Story)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='consenso informato.pdf')



# da definire, la View per l'inserimento di un nuovo paziente
