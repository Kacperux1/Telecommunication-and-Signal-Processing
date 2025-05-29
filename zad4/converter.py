import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav


# Funkcja do nagrywania dźwięku i zapisywania go do pliku WAV
def record_audio(filename, duration, samplerate, bitdepth):
    print(f"Nagrywanie: {duration}s, {samplerate} Hz, {bitdepth} bit")

    channels = 1  # Mono – bo jedno źródło dźwięku nam wystarczy
    # Wybieramy odpowiedni typ danych w zależności od rozdzielczości bitowej
    dtype = np.int16 if bitdepth == 16 else np.uint8

    # Rozpoczynamy nagrywanie – tworzymy tablicę z dźwiękiem
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype=dtype)
    sd.wait()  # Czekamy, aż nagranie się zakończy

    # Zapisujemy nagrany dźwięk do pliku WAV
    wav.write(filename, samplerate, audio)
    print("Zapisano:", filename)


# Funkcja do odtwarzania dźwięku z pliku
def play_audio(filename):
    # Odczytujemy dane z pliku WAV
    samplerate, data = wav.read(filename)
    # Odtwarzamy to, co udało się nagrać
    sd.play(data, samplerate)
    sd.wait()  # Czekamy, aż odtwarzanie się zakończy
    print("Odtwarzanie zakończone.")


# Funkcja do obliczania stosunku sygnału do szumu (SNR)
def calculate_snr(reference, test):
    # Różnica między sygnałem oryginalnym a testowym to nasz szum
    noise = reference[:len(test)] - test
    # Obliczamy moc sygnału i moc szumu (średnie kwadraty)
    signal_power = np.mean(reference[:len(test)] ** 2)
    noise_power = np.mean(noise ** 2)
    # Klasyczny wzór na SNR w decybelach
    snr = 10 * np.log10(signal_power / noise_power)
    return snr
