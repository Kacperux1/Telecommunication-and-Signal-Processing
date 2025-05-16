from converter import record_audio, play_audio, calculate_snr
import soundfile as sf

def main():
    print("Co chcesz zrobić?")
    print("1. Nagrać dźwięk (A/C)")
    print("2. Odtworzyć dźwięk (C/A)")
    print("3. oblicz współczynnik SNR")
    choice = input("Wybierz [1/2/3]: ")

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

    elif choice == '3':
        ref_file = input("Podaj nazwę pliku referencyjnego: ").strip()
        test_file = input("Podaj nazwę pliku testowego: ").strip()
        try:
            ref_signal, _ = sf.read(ref_file, dtype='float32')
            test_signal, _ = sf.read(test_file, dtype='float32')

            snr = calculate_snr(ref_signal, test_signal)
            print(f"SNR między '{ref_file}' i '{test_file}': {snr:.2f} dB")
        except Exception as e:
            print(f"Błąd przy liczeniu SNR: {e}")
    else:
        print("Niepoprawny wybór.")

if __name__ == "__main__":
    main()
