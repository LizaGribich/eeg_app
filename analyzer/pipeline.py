from .data_loader import load_eeg
from .preprocessing import preprocess_signal
from .analysis import compute_psd, compute_band_power, dominant_freq_in_band
from .visualization import fig_raw, fig_filtered, fig_alpha, fig_psd


def process_file(path, colors):
    t, signal, fs = load_eeg(path)

    filtered = preprocess_signal(signal, fs)
    freqs, psd = compute_psd(filtered, fs)

    alpha_power = compute_band_power(freqs, psd, 8, 13)
    dom = dominant_freq_in_band(freqs, psd, 8, 13)

    figs = [
        fig_raw(t, signal, colors["raw"]),
        fig_filtered(t, filtered, colors["filtered"]),
        fig_alpha(t, signal, fs, alpha_power, colors["alpha"]),
        fig_psd(freqs, psd, dom, colors["psd"], colors["filtered"])
    ]

    return path, alpha_power, figs
