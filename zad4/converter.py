import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav


def record_audio(filename, duration, samplerate, bitdepth):
    print(f"Nagrywanie: {duration}s, {samplerate} Hz, {bitdepth} bit")

    channels = 1
    dtype = np.int16 if bitdepth == 16 else np.uint8

    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype=dtype)
    sd.wait()

    # Skalowanie do formatu WAV
    wav.write(filename, samplerate, audio)
    print("Zapisano:", filename)


def play_audio(filename):
    samplerate, data = wav.read(filename)
    sd.play(data, samplerate)
    sd.wait()
    print("Odtwarzanie zakończone.")


def calculate_snr(reference, test):
    noise = reference[:len(test)] - test
    signal_power = np.mean(reference[:len(test)] ** 2)
    noise_power = np.mean(noise ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    return snr
