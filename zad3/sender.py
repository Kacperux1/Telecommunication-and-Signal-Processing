import socket
import json

# Wysyła zakodowaną wiadomość do odbiornika
# Parametry:
#   host (str)      – IP odbiornika (np. '192.168.1.10')
#   port (int)      – port, na który wysyłamy
#   codebook (dict) – słownik znak → kod binarny
#   encoded (str)   – wiadomość zakodowana binarnie
# Zwraca:
#   Nic – wypisuje tylko potwierdzenie wysłania
def send(host, port, codebook, encoded):
    # Tworzymy pakiet JSON z danymi
    payload = json.dumps({
        'codebook': codebook,
        'encoded': encoded
    }).encode()

    # Łączymy się z odbiornikiem i wysyłamy dane
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(payload)
        print("Wiadomość wysłana.")
