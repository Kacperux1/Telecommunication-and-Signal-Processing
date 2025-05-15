from converter import record_audio, play_audio

def main():
    print("Co chcesz zrobić?")
    print("1. Nagrać dźwięk (A/C)")
    print("2. Odtworzyć dźwięk (C/A)")
    choice = input("Wybierz [1/2]: ")

    filename = input("Podaj nazwę pliku WAV (np. dzwiek.wav): ")

    if choice == '1':
        try:
            duration = float(input("Czas nagrania w sekundach (np. 5): "))
            samplerate = int(input("Częstotliwość próbkowania (np. 44100): "))
            bitdepth = int(input("Rozdzielczość [8 lub 16]: "))
            if bitdepth not in (8, 16):
                raise ValueError("Dozwolona rozdzielczość to tylko 8 lub 16 bitów.")
            record_audio(filename, duration, samplerate, bitdepth)
        except ValueError as e:
            print("Błąd danych wejściowych:", e)

    elif choice == '2':
        try:
            play_audio(filename)
        except FileNotFoundError:
            print("Nie znaleziono pliku:", filename)
        except Exception as e:
            print("Wystąpił błąd podczas odtwarzania:", e)
    else:
        print("Niepoprawny wybór.")

if __name__ == "__main__":
    main()
