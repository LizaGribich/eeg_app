import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import threading
import time
import csv
from collections import deque
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DARK_BG = "#0d1226"
PANEL_BG = "#151b33"
ACCENT = "#5c63ff"
TEXT = "#cdd2ff"
GRAPH_BG = "#0f1530"
GRAPH_GRID = "#2c335c"
GRAPH_LINE = "#76aaff"


class DarkNeuroApp:

    def __init__(self, parent: tk.Frame):

        self.root = parent
        self.root.configure(bg=DARK_BG)

        self.serial_obj = None
        self.baud = 115200
        self.selected_channel = "A0"

        self.x_vals = deque(maxlen=1500)
        self.y_vals = deque(maxlen=1500)
        self.idx = 0
        self.active = True

        self.data_buffer = bytearray()

        self.is_recording = False
        self.file = None
        self.writer = None

        # UI
        self._apply_dark_style()
        self._build_ui()
        self._list_ports()
        self._start_thread()

    def _apply_dark_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        style.configure("TFrame", background=DARK_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("TLabel", background=PANEL_BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=PANEL_BG, foreground=ACCENT, font=("Segoe UI", 12, "bold"))
        style.configure(
            "TButton",
            background="#1c2342",
            foreground=TEXT,
            padding=6,
            font=("Segoe UI", 10),
        )
        style.map("TButton", background=[("active", "#2a3360")])
        style.configure("TCombobox", fieldbackground="#1b213a", background="#1b213a", foreground=TEXT)

    def _build_ui(self):
        left = ttk.Frame(self.root, style="Panel.TFrame", padding=15)
        left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left, text="Подключение", style="Title.TLabel").pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="COM-port:").pack(anchor="w")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(left, textvariable=self.port_var, width=18, state="readonly")
        self.port_combo.pack(pady=5)

        ttk.Button(left, text="Обновить", command=self._list_ports).pack(pady=2)

        ttk.Label(left, text="Baudrate:").pack(anchor="w", pady=(10, 0))
        self.baud_var = tk.StringVar(value="115200")
        ttk.Entry(left, textvariable=self.baud_var).pack(pady=4)

        ttk.Label(left, text="Канал:").pack(anchor="w", pady=(10, 0))
        self.channel_var = tk.StringVar(value="A0")
        self.channel_combo = ttk.Combobox(
            left,
            textvariable=self.channel_var,
            values=["A0", "A1", "A2", "A3", "A4", "A5", "B0", "B1", "B2", "B3", "B4", "B5"],
            width=10,
            state="readonly",
        )
        self.channel_combo.pack(pady=4)

        ttk.Button(left, text="Connect", command=self._connect).pack(pady=10)
        ttk.Button(left, text="Disconnect", command=self._disconnect).pack(pady=2)

        ttk.Label(left, text="Запись", style="Title.TLabel").pack(anchor="w", pady=(20, 10))

        ttk.Button(left, text="Выбрать файл", command=self._choose_file).pack(pady=5)

        self.path_var = tk.StringVar(value="Файл не выбран")
        ttk.Label(left, textvariable=self.path_var, wraplength=180).pack(pady=4)

        ttk.Button(left, text="Старт записи", command=self._start_rec).pack(pady=5)
        ttk.Button(left, text="Стоп запись", command=self._stop_rec).pack(pady=5)

        ttk.Button(left, text="Очистить график", command=self._clear_graph).pack(pady=15)

        self.status = tk.StringVar(value="Статус: отключено")
        ttk.Label(left, textvariable=self.status, foreground=ACCENT).pack(pady=(10, 0))

        graph_frame = ttk.Frame(self.root, padding=10, style="Panel.TFrame")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(GRAPH_BG)
        ax.set_facecolor(GRAPH_BG)
        ax.set_xlim(0, 500)
        ax.set_ylim(0, 300)
        ax.set_title("Neuro Signal", color=TEXT)
        ax.grid(color=GRAPH_GRID, linestyle="--", alpha=0.5)
        ax.tick_params(colors=TEXT)
        ax.spines["bottom"].set_color(TEXT)
        ax.spines["left"].set_color(TEXT)

        self.fig = fig
        self.ax = ax
        self.line, = ax.plot([], [], color=GRAPH_LINE, linewidth=1.8)

        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def _list_ports(self):
        ports = serial.tools.list_ports.comports()
        names = [p.device for p in ports]
        self.port_combo["values"] = names
        if names:
            self.port_var.set(names[0])

    def _connect(self):
        try:
            self.serial_obj = serial.Serial(
                self.port_var.get(),
                int(self.baud_var.get()),
                timeout=1
            )
            time.sleep(2)
            self.serial_obj.reset_input_buffer()
            self.data_buffer.clear()
            self.status.set("Статус: подключено")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.status.set("Статус: ошибка подключения")

    def _disconnect(self):
        if self.serial_obj and self.serial_obj.is_open:
            self.serial_obj.close()
        self.status.set("Статус: отключено")

    def _start_thread(self):
        def read_loop():
            while self.active:
                if self.serial_obj and self.serial_obj.is_open:
                    try:
                        available = self.serial_obj.in_waiting
                        if available > 0:
                            self.data_buffer.extend(self.serial_obj.read(available))
                            self._parse_buffer()
                        time.sleep(0.001)
                    except Exception as err:
                        print("Ошибка чтения:", err)
                        self.status.set(f"Ошибка чтения: {err}")
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)

        threading.Thread(target=read_loop, daemon=True).start()

    def _parse_buffer(self):
        i = 0
        while i < len(self.data_buffer) - 2:
            if self.data_buffer[i] in (65, 66):  # 'A'/'B'
                if 48 <= self.data_buffer[i + 1] <= 53:
                    channel = f"{chr(self.data_buffer[i])}{chr(self.data_buffer[i + 1])}"
                    if channel == self.channel_var.get():
                        value = self.data_buffer[i + 2]
                        self.x_vals.append(self.idx)
                        self.y_vals.append(value)
                        self.idx += 1

                        if self.is_recording and self.writer:
                            self.writer.writerow([time.time(), channel, value])

                        self.root.after(0, self._update_graph)

                    i += 3
                else:
                    i += 1
            else:
                i += 1

        if i > 0:
            del self.data_buffer[:i]

    def _update_graph(self):
        if not self.x_vals:
            return

        self.line.set_data(self.x_vals, self.y_vals)
        self.ax.set_xlim(max(0, self.idx - 500), max(500, self.idx))

        y_min, y_max = min(self.y_vals), max(self.y_vals)
        if y_max > y_min:
            margin = (y_max - y_min) * 0.1
            self.ax.set_ylim(y_min - margin, y_max + margin)

        self.canvas.draw_idle()

    def _choose_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if path:
            self.path_var.set(path)

    def _start_rec(self):
        if self.path_var.get() == "Файл не выбран":
            messagebox.showerror("Ошибка", "Укажи файл для записи")
            return

        try:
            self.file = open(self.path_var.get(), "w", newline="", encoding="utf-8")
            self.writer = csv.writer(self.file)
            self.writer.writerow(["timestamp", "channel", "value"])
            self.is_recording = True
            self.status.set("Статус: запись включена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _stop_rec(self):
        if self.is_recording:
            self.is_recording = False
            if self.file:
                self.file.close()
            self.file = None
            self.writer = None
            self.status.set("Статус: запись остановлена")

    def _clear_graph(self):
        self.x_vals.clear()
        self.y_vals.clear()
        self.idx = 0
        self.line.set_data([], [])
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(0, 300)
        self.canvas.draw()

    def stop(self):
        self.active = False
        self._stop_rec()
        if self.serial_obj and self.serial_obj.is_open:
            self.serial_obj.close()
