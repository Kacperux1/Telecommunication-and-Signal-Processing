import heapq
from collections import defaultdict, Counter
import sender
import receiver


host = 'localhost'
port = 12345

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
    #filename = input("Podaj nazwę pliku:")
    #print("wprowadzony plik: " + filename)
    filename = "message.txt"
    if not filename.endswith(".txt"):
        raise ValueError("Niewłaściwy format pliku!")
    # wczytanie pliku
    with open(filename, "r", encoding="ascii") as file:
        message = file.read()
    # wyswietlenie wczytanej wiadomości
    print(message)

    root = build_huffman_tree(message)
    codebook = generate_codes(root)

    print("Słownik kodowy Huffmana:")
    for char, code in codebook.items():
        print(f"'{char}': {code}")

    encoded = encode_text(message, codebook)
    print("\nZakodowany tekst binarnie:")
    print(encoded)

main()
