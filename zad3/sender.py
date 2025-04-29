import socket
import json

def send(host, port, codebook, encoded):
    # Pakujemy do JSON-a
    payload = json.dumps({
        'codebook': codebook,
        'encoded': encoded
    }).encode()

    # Wysylamy przez socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(payload)
        print("Wiadomość wysłana.")