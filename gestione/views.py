"""Modulo con le views di pazienti e fatture"""
from django.shortcuts import render
from django.views import generic
from .models import Paziente, Fattura
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.contrib.auth.mixins import LoginRequiredMixin
styles = getSampleStyleSheet()

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
    f = Fattura.objects.get(id=pk)
    paz = f.paziente
    nome_file = str(f.numero) + "-" + str(f.get_year()) + ".pdf"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    Story = [Spacer(1, 2*inch)]
    style = styles["Normal"]

    text = '<font size="18">Marco De Canal</font><br/><font size="14">Massofisioterapista</font><br/>'
    p = Paragraph(text, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    text = '''
        <i>Sede legale:</i> Via Brescia 205B, 47842, S. Giovanni in M.no (RN)<br/>
        <i>C.F.:</i> DCNMRC90L25D142Z<br/>
        <i>P.IVA:</i> 04370000400<br/>
    '''
    p = Paragraph(text, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    text = '''
        <i>Telefono: </i> +39 338 533 0241<br/>
        <i>email: </i> marco.decanal@gmail.com<br/>
        <i>Indirizzo studio: </i> Via XX Settembre 1, 47842, S. Giovanni in M.no (RN)<br/>
    '''
    p = Paragraph(text, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    text = f"Spett.le {paz.cognome} {paz.nome}"
    if(paz.codfisc):
        text += f"<br/>Cod. fisc: {paz.codfisc}"
    if(paz.piva):
        text += f"<br/>P. Iva: {paz.piva}"
    if(paz.via and paz.civico and paz.cap and paz.paese and paz.provincia):
        text += f"<br/> {paz.via} {paz.civico}, {paz.cap}, {paz.paese} ({paz.provincia})<br/>"

    p = Paragraph(text, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    text = f"Fattura numero {f.numero} del {f.data}"

    p = Paragraph(text, style)
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
    Story.append(Spacer(1, 0.2*inch))

    text = '''
        Operazione senza applicazione dell’Iva ai sensi Legge
        190 del 23/12/2014 art. 1, commi da 54 a 89.<br/>
        Operazione effettuata ai sensi art. 1, commi da 54 a 89,
        della Legge 190 del 23/12/2014 – Regime forfetario.<br/>
        Il compenso non soggetto a ritenute d’acconto ai sensi della Legge
        190 del 23/12/2014, art. 1 comma 67.<br/>
        Vi informiamo che tutti i dati a Voi relativi in nostro possesso verranno inseriti
        in un apposito archivio, ai sensi della L. 196/03. Tale trattamento è finalizzato
        all’adempimento di norme di Legge, di obblighi contabili, fiscali, commerciali
        per scopi interni, e nei limiti richiesti dall’adempimento dell’incarico
        (incluso corrieri, se previsti, e banche, per incassi e pagamenti). Al di
        fuori di questi casi non è prevista la divulgazione e/o diffusione di dati a terzi.<br/>
    '''
    p = Paragraph(text, style)
    Story.append(p)
    Story.append(Spacer(1, 0.2*inch))

    doc.build(Story)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=nome_file)


# da definire, la View per l'inserimento di un nuovo paziente
