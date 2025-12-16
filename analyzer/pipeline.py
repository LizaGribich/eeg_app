from utils import print_memory, start_timer, print_time
from .data_loader import load_eeg
from .preprocessing import preprocess_steps
from .analysis import compute_psd, compute_band_power, dominant_freq_in_band
from .visualization import (
    fig_raw,
    fig_filtered,
    fig_alpha,
    fig_psd,
    fig_segment_stage,
)


def process_file(path, colors, low_cut, high_cut):
    total_start = start_timer()
    #print_memory("Перед загрузкой файла")

    t0 = start_timer()
    t, signal, fs = load_eeg(path)
    print_time(t0, "Время загрузки EEG-файла")
    #print_memory("После загрузки EEG-файла")

    t0 = start_timer()
    stage_baseline, stage_despike, filtered = preprocess_steps(signal, fs, low_cut, high_cut)
    print_time(t0, "Время предобработки")
    #print_memory("После предобработки")

    t0 = start_timer()
    freqs, psd = compute_psd(filtered, fs)
    print_time(t0, "Время спектрального анализа (PSD)")
    #print_memory("После PSD")

    t0 = start_timer()
    alpha_power = compute_band_power(freqs, psd, 8, 13)
    dom = dominant_freq_in_band(freqs, psd, 8, 13)
    print_time(t0, "Время вычисления признаков альфа-диапазона")
    #print_memory("После вычисления признаков")

    t0 = start_timer()
    start_sec = 20
    duration_sec = 10
    segment_figs = [
        fig_segment_stage(t, signal, "Сырой сегмент", colors["raw"], start_sec, duration_sec),
        fig_segment_stage(t, stage_baseline, "После удаления дрейфа", colors["filtered"], start_sec, duration_sec),
        fig_segment_stage(t, stage_despike, "После удаления выбросов", colors["filtered"], start_sec, duration_sec),
        fig_segment_stage(t, filtered, "После ФНЧ и ФВЧ", colors["filtered"], start_sec, duration_sec),
    ]

    figs = segment_figs + [
        fig_raw(t, signal, colors["raw"]),
        fig_filtered(t, filtered, colors["filtered"]),
        fig_alpha(t, signal, fs, alpha_power, colors["alpha"]),
        fig_psd(freqs, psd, dom, colors["psd"], colors["filtered"])
    ]
    print_time(t0, "Время построения графиков")
    #print_memory("После визуализации")

    print_time(total_start, "Общее время обработки файла")

    return path, alpha_power, figs
