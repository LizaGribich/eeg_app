import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def embed_plot(parent, fig):
    frame = tk.Frame(parent, bg="#0d1226")
    frame.pack(fill="x", pady=20)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()
