import socket
import json

# Funkcja odwrotna do codebooku
def decode_message(encoded, codebook):
    inverse = {v: k for k, v in codebook.items()}
    decoded = ''
    buffer = ''
    for bit in encoded:
        buffer += bit
        if buffer in inverse:
            decoded += inverse[buffer]
            buffer = ''
    return decoded

def receive(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("Oczekiwanie na połączenie...")
        conn, addr = s.accept()
        with conn:
            print(f"Połączono z {addr}")
            data = b''
            while True:
                part = conn.recv(1024)
                if not part:
                    break
                data += part

            # Parsujemy JSON
            message = json.loads(data.decode())
            codebook = message['codebook']
            encoded = message['encoded']
            decoded = decode_message(encoded, codebook)

            print(f"Odebrana i zdekodowana wiadomość: {decoded}")

            # Zapis do pliku
            with open('output.txt', 'w') as f:
                f.write(decoded)
            print("Zapisano do pliku output.txt")