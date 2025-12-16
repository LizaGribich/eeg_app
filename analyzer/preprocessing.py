import numpy as np
from scipy.signal import butter, filtfilt
import pandas as pd

#удаление 
def remove_baseline_wander(signal, window=250):
    s = pd.Series(signal)
    return signal - s.rolling(window, center=True, min_periods=1).median().values

#очитска от выосов
def remove_spikes(signal, threshold=5):
    mean = np.mean(signal);
    std = np.std(signal)
    z = np.abs((signal - mean) / std)
    mask = z < threshold
    cleaned = signal.copy()
    if np.any(~mask):
        cleaned[~mask] = np.interp(np.flatnonzero(~mask), np.flatnonzero(mask), cleaned[mask])
    return cleaned


#нижний и верхние частоты
def bandpass_filter(data, low, high, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    return filtfilt(b, a, data)


def preprocess_signal(sig, fs, low_cut, high_cut):
    sig = remove_baseline_wander(sig)
    sig = remove_spikes(sig)
    return bandpass_filter(sig, low_cut, high_cut, fs)


def preprocess_steps(sig, fs, low_cut, high_cut):
    """
    Возвращает промежуточные стадии предобработки для визуализации кумулятивного эффекта.
    """
    stage_baseline = remove_baseline_wander(sig)
    stage_despike = remove_spikes(stage_baseline)
    stage_band = bandpass_filter(stage_despike, low_cut, high_cut, fs)
    return stage_baseline, stage_despike, stage_band

