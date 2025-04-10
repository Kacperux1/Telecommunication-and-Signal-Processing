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
        # zamien każdy znak na listę bitów
        binary_char = [int(b) for b in format(ord(char), '08b')]
        # wyznacz bity kontrolne przez mnożenie z macierzą H
        even_bits = (np.dot(h_matrix[:, :8], binary_char) % 2).tolist()
        result.append(binary_char + even_bits)
    return result


# funkcja SPRAWDŹ POPRAWNOŚĆ
# parametry wejścia:
# @encoded_message - macierz Nx16 reprezentujaca zakodowaną wiadomość z bitami kontrolnymi
# ZWRÓĆ: sprawdzona (i ewentualnie poprawiona) wiadomość
def is_correct(encoded_message):
    znak = 1
    decoded = []
    for codeword in encoded_message:
        # sprawdź, czy jest błąd
        syndrome = np.dot(h_matrix, codeword) % 2
        if any(syndrome):
            # jeżeli syndrom rozny od 0 sprawdzamy czy jest pojedynczy bład
            error_position = find_single_error(syndrome)

            if error_position is not None:
                # jeżeli błąd jest pojedynczy naprawiamy go normalnie
                codeword[error_position] = 1 - codeword[error_position]
            else:
                # jeżeli nie zanleziono błędu pojedynczego to szykamy podwójnego
                error_pattern = find_two_errors(syndrome)
                if error_pattern:
                    # jeżeli lista (error_pattern) nie jest pusta to znaleziono błąd podwójny i go naprawiamy
                    codeword = correct_two_errors(codeword, error_pattern)
                # jeżeli syndrom!=0 ale nie ma błędu pojedynczego ani podwójnego no to nie umiemy go naprawić
                else:
                    print()
                    print("Znalazłem błąd w", znak, "znaku ale niestety nie umiem tego naprawić :( ")
                    print()

        decoded.append(codeword[:8])
        znak = znak + 1
    return decoded


def find_single_error(syndrome):
    # Szukamy pojedynczego błędu czyli czy syndrom to jedna z kolum w macierzy
    for i in range(16):
        if np.array_equal(syndrome, h_matrix[:, i]):
            return i  # Pozycja błędu
    return None  # Jeśli nie znaleziono pojedynczego błędu


def find_two_errors(syndrome):
    # Szukamy dwóch błędów poprzez sprawdzenie czy syndrom to XOR dwóch kolumn
    for i in range(16):
        for j in range(i + 1, 16):
            if np.array_equal(syndrome, np.bitwise_xor(h_matrix[:, i], h_matrix[:, j])):
                # print(i," ", j)
                return [i, j]  # Pozycje błędów
    return None  # Jeśli nie znaleziono dwóch błędów


def correct_two_errors(codeword, error_pattern):
    # Korygujemy dwa błędy
    for index in error_pattern:
        codeword[index] = 1 - codeword[index]  # Zmieniamy bit
    return codeword


# funkcja DEKODUJ
# parametry wejścia:
# @coded_message - macierz Nx16 reprezentujaca zakodowaną wiadomość z bitami kontrolnymi
# ZWRÓĆ: zdekodowany ciąg znaków (ascii)
def decode(coded_message):
    result = []
    for codeword in coded_message:
        # pobierz pierwsze 8 bitów z każdego wiersza (część wcześniej pobrana z pliku)
        binary_char = codeword[:8]
        # zamień na znak
        ascii_char = chr(int(''.join(map(str, binary_char)), 2))
        # dodaj do wyniku
        result.append(ascii_char)
    return ''.join(result)


def main():
    filename = input("Podaj nazwę pliku:")
    print("wprowadzony plik: " + filename)
    if not filename.endswith(".txt"):
        raise ValueError("Niewłaściwy format pliku!")
    # wczytanie pliku
    with open(filename, "r", encoding="ascii") as file:
        message = file.read()
    # wyswietlenie wczytanej wiadomości
    print(message)
    # dodanie bitów kontrolnych
    coded_message = encode(message)
    # popsucie wiadomości
    coded_message[2][1] = 1 - coded_message[2][1]
    coded_message[2][3] = 1 - coded_message[2][3]

    coded_message[3][3] = 1 - coded_message[3][3]

    coded_message[1][1] = 1 - coded_message[1][1]

    # coded_message[7][1] = 1 - coded_message[7][1]
    # coded_message[7][2] = 1 - coded_message[7][2]
    # coded_message[7][3] = 1 - coded_message[7][3]
    # coded_message[7][4] = 1 - coded_message[7][4]

    # kontrolne wyświetlenie popsutej wiadomości
    print(decode(coded_message))
    # sprawdzenie i korekcja błędów
    decoded_message = decode(is_correct(coded_message))
    # wyświetl prawidłową wiadomość
    print(decoded_message)

    with open("wiadomosc_wynikowa.txt", "w", encoding="ascii") as file:
        file.write(decoded_message)


main()
