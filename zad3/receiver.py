import socket
import json

# Odszyfrowuje wiadomość na podstawie słownika kodowego
# Parametry:
#   encoded (str)  – zakodowana binarnie wiadomość
#   codebook (dict) – słownik: znak → kod binarny
# Zwraca:
#   decoded (str) – odszyfrowana wiadomość
def decode_message(encoded, codebook):
    inverse = {v: k for k, v in codebook.items()}  # Odwracamy słownik: binarka → litera
    decoded = ''
    buffer = ''
    for bit in encoded:
        buffer += bit
        if buffer in inverse:
            decoded += inverse[buffer]
            buffer = ''
    return decoded

# Nasłuchuje na porcie i odbiera wiadomość
# Parametry:
#   host (str) – adres IP do nasłuchiwania (np. '0.0.0.0')
#   port (int) – numer portu, na którym nasłuchujemy
# Nie zwraca nic – zapisuje wynik do pliku i wypisuje na ekranie
def receive(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))       # Rejestrujemy port
        s.listen(1)                # Czekamy na połączenie
        print("Oczekiwanie na połączenie...")
        conn, addr = s.accept()    # Akceptujemy połączenie
        with conn:
            print(f"Połączono z {addr}")
            data = b''
            while True:
                part = conn.recv(1024)  # Odbieramy dane po kawałku
                if not part:
                    break
                data += part

            # Rozpakowujemy dane z JSON-a
            message = json.loads(data.decode())
            codebook = message['codebook']
            encoded = message['encoded']
            decoded = decode_message(encoded, codebook)

            print(f"Odebrana i zdekodowana wiadomość: {decoded}")

            # Zapisujemy wynik do pliku
            with open('output.txt', 'w') as f:
                f.write(decoded)
            print("Zapisano do pliku output.txt")
