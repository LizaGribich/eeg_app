import tkinter as tk
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
from .pipeline import process_file
from .ui_plots import embed_plot


class EEGApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#0d1226")
        self.loaded_files = []

        self.color_sets = [
            {"raw": "#76aaff", "filtered": "#5cffb0", "alpha": "#ff6b6b", "psd": "#ffd166"},
            {"raw": "#e27dff", "filtered": "#7dffea", "alpha": "#ff7d7d", "psd": "#ffe27d"},
            {"raw": "#7dd0ff", "filtered": "#9dff7d", "alpha": "#ff9d7d", "psd": "#ff7dd0"},
            {"raw": "#ffadad", "filtered": "#caffbf", "alpha": "#ffd6a5", "psd": "#9bf6ff"},
            {"raw": "#bdb2ff", "filtered": "#ffc6ff", "alpha": "#ff9e00", "psd": "#00bbf9"},
        ]

        self.canvas = tk.Canvas(root, bg="#0d1226", highlightthickness=0)
        self.scroll_frame = tk.Frame(self.canvas, bg="#0d1226")
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)

        self.scroll_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.scroll_frame, bg="#0d1226")
        top.pack(fill="x", pady=20)

        tk.Button(top, text="Выбрать файлы", bg="#5c63ff", fg="white",
                  command=self.load_files).pack(side="left", padx=10)

        tk.Button(top, text="Очистить", bg="#ff4d4d", fg="white",
                  command=self.clear_all).pack(side="left", padx=10)

        # --- Параметры фильтра ---
        filter_frame = tk.Frame(top, bg="#0d1226")
        filter_frame.pack(side="left", padx=20)

        tk.Label(filter_frame, text="Нижняя Гц",
                 bg="#0d1226", fg="white").grid(row=0, column=0)

        self.low_cut_var = tk.StringVar(value="1")
        tk.Entry(filter_frame, textvariable=self.low_cut_var,
                 width=6).grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Верхняя Гц",
                 bg="#0d1226", fg="white").grid(row=0, column=2)

        self.high_cut_var = tk.StringVar(value="40")
        tk.Entry(filter_frame, textvariable=self.high_cut_var,
                 width=6).grid(row=0, column=3, padx=5)

        #self.low_cut_var.trace_add("write", self.on_filter_change)
        #self.high_cut_var.trace_add("write", self.on_filter_change)
        tk.Button(
            filter_frame,
            text="ОК",
            bg="#5cffb0",
            fg="black",
            command=self.apply_filter
        ).grid(row=0, column=4, padx=10)

        self.file_label = tk.Label(self.scroll_frame, text="Файлы не выбраны",
                                   bg="#0d1226", fg="#5c63ff", font=("Arial", 14))
        self.file_label.pack()

    def on_filter_change(self, *args):
        # если файлы ещё не выбраны — ничего не делаем
        if not self.loaded_files:
            return

        # 1. безопасно читаем значения (пользователь может ещё печатать)
        try:
            low_cut = float(self.low_cut_var.get())
            high_cut = float(self.high_cut_var.get())
        except ValueError:
            return

        # 2. получаем fs из первого файла
        try:
            from .data_loader import load_eeg
            _, _, fs = load_eeg(self.loaded_files[0])
        except Exception:
            return

        # 3. ЖЁСТКАЯ валидация для scipy butter
        if low_cut <= 0:
            return
        if high_cut <= low_cut:
            return
        if high_cut >= fs / 2:
            return

        # 4. очищаем всё, кроме верхней панели
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.build_ui()

        # 5. восстанавливаем список файлов
        self.file_label.config(
            text="\n".join(os.path.basename(f) for f in self.loaded_files)
        )

        # 6. пересчитываем и перерисовываем графики
        results = []
        for idx, path in enumerate(self.loaded_files):
            colors = self.color_sets[idx % len(self.color_sets)]

            tk.Label(
                self.scroll_frame,
                text=os.path.basename(path),
                fg=colors["raw"],
                bg="#0d1226",
                font=("Arial", 18, "bold")
            ).pack(pady=20)

            fname, alpha_power, figs = process_file(
                path, colors, low_cut, high_cut
            )
            results.append((fname, alpha_power, colors["alpha"]))

            for fig in figs:
                embed_plot(self.scroll_frame, fig)

        # 7. итоговая гистограмма
        self.build_summary(results)

    def clear_all(self):
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.build_ui()

    def load_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("EEG files", "*.csv *.edf *.set *.fdt")]
        )
        if not files:
            return

        self.file_label.config(text="\n".join(os.path.basename(f) for f in files))
        self.loaded_files = list(files)

        results = []

        low_cut = float(self.low_cut_var.get())
        high_cut = float(self.high_cut_var.get())

        for idx, path in enumerate(files):
            colors = self.color_sets[idx % len(self.color_sets)]

            tk.Label(self.scroll_frame, text=os.path.basename(path),
                     fg=colors["raw"], bg="#0d1226",
                     font=("Arial", 18, "bold")).pack(pady=20)
            fname, alpha_power, figs = process_file(
                path, colors, low_cut, high_cut
            )

            results.append((fname, alpha_power, colors["alpha"]))

            for fig in figs:
                embed_plot(self.scroll_frame, fig)

        self.build_summary(results)

    def build_summary(self, results):
        results.sort(key=lambda x: x[1], reverse=True)

        names = [os.path.basename(x[0]) for x in results]
        powers = [x[1] for x in results]
        colors = [x[2] for x in results]

        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#0d1226")
        ax.set_facecolor("#0f1530")

        bars = ax.bar(names, powers, color=colors)
        for b, p in zip(bars, powers):
            ax.text(b.get_x() + b.get_width() / 2, p, f"{p:.4f}",
                    ha="center", va="bottom", color="white")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")

        embed_plot(self.scroll_frame, fig)

    def apply_filter(self):
        if not self.loaded_files:
            return

        try:
            low_cut = float(self.low_cut_var.get())
            high_cut = float(self.high_cut_var.get())
        except ValueError:
            return

        # fs берём из первого файла
        from .data_loader import load_eeg
        _, _, fs = load_eeg(self.loaded_files[0])

        # валидация
        if low_cut <= 0 or high_cut <= low_cut or high_cut >= fs / 2:
            from tkinter import messagebox
            messagebox.showerror(
                "Ошибка параметров",
                f"Допустимо: 0 < low < high < {fs / 2:.1f} Гц"
            )
            return

        # очистка графиков
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.build_ui()

        self.file_label.config(
            text="\n".join(os.path.basename(f) for f in self.loaded_files)
        )

        results = []
        for idx, path in enumerate(self.loaded_files):
            colors = self.color_sets[idx % len(self.color_sets)]

            tk.Label(
                self.scroll_frame,
                text=os.path.basename(path),
                fg=colors["raw"],
                bg="#0d1226",
                font=("Arial", 18, "bold")
            ).pack(pady=20)

            fname, alpha_power, figs = process_file(
                path, colors, low_cut, high_cut
            )
            results.append((fname, alpha_power, colors["alpha"]))

            for fig in figs:
                embed_plot(self.scroll_frame, fig)

        self.build_summary(results)
