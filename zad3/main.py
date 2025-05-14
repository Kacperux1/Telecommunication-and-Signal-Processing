import heapq
from collections import defaultdict, Counter
import sender
import receiver




# Węzeł drzewa Huffmana
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):  # dla heapq
        return self.freq < other.freq


# Budowanie drzewa Huffmana
def build_huffman_tree(text):
    frequency = Counter(text)
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        right = heapq.heappop(heap)
        left = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0]  # korzeń drzewa


# Generowanie kodów (rekurencyjnie)
def generate_codes(node, prefix="", codebook={}):
    if node is None:
        return
    if node.char is not None:
        codebook[node.char] = prefix
    generate_codes(node.left, prefix + "0", codebook)
    generate_codes(node.right, prefix + "1", codebook)
    return codebook


# Kodowanie tekstu
def encode_text(text, codebook):
    return ''.join(codebook[char] for char in text)


def main():
    import threading
    import time
    host = '0.0.0.0'
    port = 12345


    mode = input("Wybierz tryb działania (send / receive): ").strip().lower()

    if mode == 'send':
        filename = input("Podaj nazwę pliku do wysłania (np. message.txt): ").strip()
        host = input("Podaj adres IP odbiorcy:")
        if not filename.endswith(".txt"):
            raise ValueError("Niewłaściwy format pliku!")

        # Wczytanie wiadomości z pliku
        with open(filename, "r", encoding="ascii") as file:
            message = file.read()
        print("Wiadomość do zakodowania:")
        print(message)

        # Kompresja Huffmana
        root = build_huffman_tree(message)
        codebook = generate_codes(root)
        encoded = encode_text(message, codebook)

        # Wyświetlenie danych
        print("\nSłownik kodowy Huffmana:")
        for char, code in codebook.items():
            print(f"'{char}': {code}")

        print("\nZakodowana wiadomość binarnie:")
        print(encoded)

        # Wysyłanie
        sender.send(host, port, codebook, encoded)

    elif mode == 'receive':
        receiver.receive(host, port)

    elif mode == 'both':
        # Działa w obu trybach: najpierw startuje receiver w tle
        threading.Thread(target=receiver.receive, args=(host, port), daemon=True).start()
        time.sleep(1)  # chwilka na uruchomienie odbiornika

        filename = input("Podaj nazwę pliku do wysłania (np. message.txt): ").strip()
        if not filename.endswith(".txt"):
            raise ValueError("Niewłaściwy format pliku!")

        with open(filename, "r", encoding="ascii") as file:
            message = file.read()
        print("Wiadomość do zakodowania:")
        print(message)

        root = build_huffman_tree(message)
        codebook = generate_codes(root)
        encoded = encode_text(message, codebook)

        print("\nSłownik kodowy Huffmana:")
        for char, code in codebook.items():
            print(f"'{char}': {code}")
        print("\nZakodowana wiadomość binarnie:")
        print(encoded)

        sender.send(host, port, codebook, encoded)
        time.sleep(2)  # czas na zakończenie odbioru

    else:
        print("Nieznany tryb. Użyj 'send' lub 'receive")


main()

