import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd


def remove_baseline_wander(signal, window=250):
    s = pd.Series(signal)
    return signal - s.rolling(window, center=True, min_periods=1).median().values


def remove_spikes(signal, threshold=5):
    mean = np.mean(signal);
    std = np.std(signal)
    z = np.abs((signal - mean) / std)
    mask = z < threshold
    cleaned = signal.copy()
    if np.any(~mask):
        cleaned[~mask] = np.interp(np.flatnonzero(~mask), np.flatnonzero(mask), cleaned[mask])
    return cleaned


def bandpass_filter(data, low, high, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    return filtfilt(b, a, data)


def preprocess_signal(sig, fs):
    sig = remove_baseline_wander(sig)
    sig = remove_spikes(sig)
    return bandpass_filter(sig, 1, 40, fs)
