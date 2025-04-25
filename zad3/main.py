import heapq
from collections import deque
from collections import defaultdict, Counter


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
    print(frequency)
    heap = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)
    for node in heap:
        print(node.char, node.freq)
    print()

    while len(heap) > 1:
        right = heapq.heappop(heap)
        print("right:", right.char, right.freq)
        left = heapq.heappop(heap)
        print("left:", left.char, left.freq)
        merged = Node(None, left.freq + right.freq)
        print(merged.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
        print()

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


# Zapis binarny do pliku
def save_encoded_to_file(encoded_text, filename="encoded.txt"):
    byte_array = bytearray()
    for i in range(0, len(encoded_text), 8):
        byte = encoded_text[i:i + 8]
        byte_array.append(int(byte.ljust(8, '0'), 2))  # dopełnij zerami
    with open(filename, "wb") as f:
        f.write(byte_array)


input_text = "ABRACADABRA"
root = build_huffman_tree(input_text)
codebook = generate_codes(root)

print("Słownik kodowy Huffmana:")
for char, code in codebook.items():
    print(f"'{char}': {code}")

encoded = encode_text(input_text, codebook)
print("\nZakodowany tekst binarnie:")
print(encoded)

save_encoded_to_file(encoded, "encoded.txt")
print("\nZakodowany plik zapisano jako 'encoded.txt'")
