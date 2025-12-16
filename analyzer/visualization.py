import matplotlib.pyplot as plt
import numpy as np

from .preprocessing import bandpass_filter


def fig_raw(t, s, c):
    f, a = plt.subplots(figsize=(12, 3))
    f.patch.set_facecolor("#0d1226")
    a.set_facecolor("#0f1530")
    a.plot(t, s, color=c)
    a.set_title("Raw", color=c)
    a.set_xlabel("Время, с", color="white")
    a.set_ylabel("Амплитуда, отн. ед.", color="white")
    a.tick_params(colors="white")
    f.subplots_adjust(bottom=0.25)
    return f


def fig_filtered(t, s, c):
    f, a = plt.subplots(figsize=(12, 3))
    f.patch.set_facecolor("#0d1226")
    a.set_facecolor("#0f1530")
    a.plot(t, s, color=c)
    a.set_title("Filtered", color=c)
    a.set_xlabel("Время, с", color="white")
    a.set_ylabel("Амплитуда, отн. ед.", color="white")
    a.tick_params(colors="white")
    f.subplots_adjust(bottom=0.25)
    return f


def fig_alpha(t, s, fs, p, c):
    f, a = plt.subplots(figsize=(12, 3))
    f.patch.set_facecolor("#0d1226")
    a.set_facecolor("#0f1530")
    al = bandpass_filter(s, 8, 13, fs)
    a.plot(t, al, color=c)
    a.set_title(f"Alpha {p:.4f}", color=c)
    a.set_xlabel("Время, с", color="white")
    a.set_ylabel("Амплитуда, отн. ед.", color="white")
    a.tick_params(colors="white")
    f.subplots_adjust(bottom=0.25)
    return f


def fig_psd(freqs, psd, df, cpsd, cline):
    f, a = plt.subplots(figsize=(12, 3))
    f.patch.set_facecolor("#0d1226")
    a.set_facecolor("#0f1530")
    m = freqs <= 30
    a.semilogy(freqs[m], psd[m], color=cpsd, label="PSD")
    a.axvspan(8, 13, color="red", alpha=0.25, label="Alpha band")
    a.axvline(df, color=cline, linestyle="--", label=f"{df:.2f} Hz")
    a.legend(facecolor="#0f1530", edgecolor="white", labelcolor="white")
    a.set_xlabel("Частота, Гц", color="white")
    a.set_ylabel("Мощность, отн. ед.", color="white")
    a.tick_params(colors="white")
    f.subplots_adjust(bottom=0.25)
    return f


def fig_segment_raw_filtered(t, raw, filtered, c_raw, c_filt, start_sec=20, duration_sec=10):
    """
    Build a combined figure with raw and filtered segments.
    Shows a window [start_sec, start_sec + duration_sec].
    Falls back to the last duration_sec of data if the requested window is unavailable.
    """
    desired_start = start_sec
    desired_end = start_sec + duration_sec

    mask = (t >= desired_start) & (t <= desired_end)
    if np.count_nonzero(mask) < 2:
        fallback_start = max(t[0], t[-1] - duration_sec)
        fallback_end = fallback_start + duration_sec
        mask = (t >= fallback_start) & (t <= fallback_end)
        if np.count_nonzero(mask) < 2:
            mask = slice(None)

    t_seg = t[mask]
    raw_seg = raw[mask]
    filt_seg = filtered[mask]

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(12, 6))
    fig.patch.set_facecolor("#0d1226")

    axes[0].set_facecolor("#0f1530")
    axes[0].plot(t_seg, raw_seg, color=c_raw)
    axes[0].set_title(
        f"Сырой сегмент {duration_sec} с начиная с {start_sec} с",
        color=c_raw
    )
    axes[0].set_ylabel("Амплитуда, отн. ед.", color="white")
    axes[0].tick_params(colors="white")

    axes[1].set_facecolor("#0f1530")
    axes[1].plot(t_seg, filt_seg, color=c_filt)
    axes[1].set_title(
        f"Отфильтрованный сегмент {duration_sec} с начиная с {start_sec} с",
        color=c_filt
    )
    axes[1].set_ylabel("Амплитуда, отн. ед.", color="white")
    axes[1].tick_params(colors="white")
    axes[1].set_xlabel("Время, с", color="white")

    fig.subplots_adjust(bottom=0.12, hspace=0.12)
    return fig
