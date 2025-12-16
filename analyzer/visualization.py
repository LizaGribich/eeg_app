import matplotlib.pyplot as plt
import numpy as np

from .preprocessing import bandpass_filter


def fig_raw(t,s,c):
    f,a=plt.subplots(figsize=(12,3)); f.patch.set_facecolor("#0d1226"); a.set_facecolor("#0f1530")
    a.plot(t,s,color=c); a.set_title("Raw",color=c); a.tick_params(colors="white"); return f


def fig_filtered(t,s,c):
    f,a=plt.subplots(figsize=(12,3)); f.patch.set_facecolor("#0d1226"); a.set_facecolor("#0f1530")
    a.plot(t,s,color=c); a.set_title("Filtered",color=c); a.tick_params(colors="white"); return f


def fig_alpha(t,s,fs,p,c):
    f,a=plt.subplots(figsize=(12,3)); f.patch.set_facecolor("#0d1226"); a.set_facecolor("#0f1530")
    al=bandpass_filter(s,8,13,fs); a.plot(t,al,color=c); a.set_title(f"Alpha {p:.4f}",color=c); a.tick_params(colors="white"); return f


def fig_psd(freqs,psd,df,cpsd,cline):
    f,a=plt.subplots(figsize=(12,3)); f.patch.set_facecolor("#0d1226"); a.set_facecolor("#0f1530")
    m=freqs<=30; a.semilogy(freqs[m],psd[m],color=cpsd,label="PSD")
    a.axvspan(8,13,color="red",alpha=0.25,label="Alpha band")
    a.axvline(df,color=cline,linestyle="--",label=f"{df:.2f} Hz")
    a.legend(facecolor="#0f1530",edgecolor="white",labelcolor="white"); a.tick_params(colors="white")
    return f


def fig_segment_stage(t, s, title, color, start_sec=20, duration_sec=10):
    """
    Отображает выбранный 10-секундный сегмент после очередной стадии обработки.
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
    s_seg = s[mask]

    f,a=plt.subplots(figsize=(12,3)); f.patch.set_facecolor("#0d1226"); a.set_facecolor("#0f1530")
    a.plot(t_seg,s_seg,color=color)
    a.set_title(f"{title} ({duration_sec} с начиная с {start_sec} с)", color=color)
    a.tick_params(colors="white")
    return f
