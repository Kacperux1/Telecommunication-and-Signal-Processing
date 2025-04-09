import numpy as np

# Macierz H
# tablica NumPy'-owa dla lepszej wydajności i możliwości wykonania dodatkowych operacji
h_matrix = np.array(
  [[1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
         [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
         [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
         [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
         [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
         [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
         [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=int)


# funkcja ZAKODUJ
# parametry wejścia:
# @message - ciąg znaków (wyłącznie ASCII!) do zakodowania (dodania bitów kontrolnych)
# ZWRÓĆ: ciąg bitów (macierz[długość wiadomomości][16 zawierajaca poszczegolne znaki w postaci binarnej
# z dołączonymi bitami kontrolnymi)
def encode(message):
    result = []
    for char in message:
        #zamien każdy znak na listę bitów
        binary_char = [int(b) for b in format(ord(char), '08b')]
        #wyznacz bity kontrolne przez mnożenie z macierzą H
        even_bits = (np.dot(h_matrix[:, :8], binary_char) % 2).tolist()
        result.append(binary_char + even_bits)
    return result


# funkcja SPRAWDŹ POPRAWNOŚĆ
# parametry wejścia:
# @encoded_message - macierz Nx16 reprezentujaca zakodowaną wiadomość z bitami kontrolnymi
# ZWRÓĆ: sprawdzona (i ewentualnie poprawiona) wiadomość
def is_correct(encoded_message):
    decoded = []
    for codeword in encoded_message:
        #sprawdź, czy jest błąd
        syndrome = np.dot(h_matrix, codeword) % 2
        if any(syndrome):
            for i in range(16):
                if np.array_equal(h_matrix[:, i], syndrome):
                    codeword[i] = 1 - codeword[i]  # naprawa błędu
                    break
        decoded.append(codeword[:8])
    return decoded


# funkcja DEKODUJ
# parametry wejścia:
# @coded_message - macierz Nx16 reprezentujaca zakodowaną wiadomość z bitami kontrolnymi
#ZWRÓĆ: zdekodowany ciąg znaków (ascii)
def decode(coded_message):
    result = []
    for codeword in coded_message:
        #pobierz pierwsze 8 bitów z każdego wiersza (część wcześniej pobrana z pliku)
        binary_char = codeword[:8]
        #zamień na znak
        ascii_char = chr(int(''.join(map(str, binary_char)), 2))
        #dodaj do wyniku
        result.append(ascii_char)
    return ''.join(result)


def main():
    # wczytanie pliku
    with open("wiadomosc.txt", "r", encoding="ascii") as file:
        message = file.read()
    # wyswietlenie wczytanej wiadomości
    print(message)
    # dodanie bitów kontrolnych
    coded_message = encode(message)
    # popsucie wiadomości
    coded_message[2][6] = 1 - coded_message[2][6]
    coded_message[3][3] = 1 - coded_message[3][3]
    coded_message[1][1] = 1 - coded_message[1][1]
    # kontrolne wyświetlenie popsutej wiadomości
    print(decode(coded_message))
    # sprawdzenie i korekcja błędów
    decoded_message = decode(is_correct(coded_message))
    # wyświetl prawidłową wiadomość
    print(decoded_message)


main()
