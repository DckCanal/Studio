from datetime import date
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
def data_italiana(data:date):
    return str(data.day)+' '+mese[data.month]+' '+str(data.year)

def data_italiana_breve(data:date):
    return str(data.day)+' '+mese[data.month][:3]+' '+str(data.year)
