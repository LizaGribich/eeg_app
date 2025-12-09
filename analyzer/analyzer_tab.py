import tkinter as tk
from .main_analyzer import EEGApp


class EEGAnalyzerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#0d1226")

        container = tk.Frame(self, bg="#0d1226")
        container.pack(fill="both", expand=True)

        self.app = EEGApp(container)
