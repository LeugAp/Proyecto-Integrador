import requests

def get_staff():
    url = 'http://127.0.0.1:8000/all-staff'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error al leer la API:", response.status_code)
