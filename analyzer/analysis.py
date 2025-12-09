import numpy as np
from scipy.signal import welch
from .preprocessing import bandpass_filter


def compute_psd(sig, fs): return welch(sig, fs, nperseg=1024)


def compute_band_power(freqs, psd, lo, hi):
    m = (freqs >= lo) & (freqs <= hi)
    return np.trapz(psd[m], freqs[m])


def dominant_freq_in_band(freqs, psd, lo, hi):
    m = (freqs >= lo) & (freqs <= hi)
    return freqs[m][np.argmax(psd[m])]


def extract_alpha_signal(sig, fs): return bandpass_filter(sig, 8, 13, fs)
