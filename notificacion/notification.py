import vonage
from api import get_staff

def notification():

    # Dominio de la pagina web
    url = 'http://143.23.52.1/'
    
    client = vonage.Client(key="26dcc8e1", secret="spHjzHHXoQ0J2RqI")
    sms = vonage.Sms(client)

    staff = get_staff()

    for destinatario in staff:
        
        mensaje = f'Está ocurriendo un sismo, sigue la ruta de evacuación: {url}geo '
        
        to_number = '593' + destinatario['phone_number']

        from_vanage = 'Vonage APIs'

        response = sms.send_message({
            'from': from_vanage,
            'to': to_number,
            'text': mensaje,
        })

        print(response)
