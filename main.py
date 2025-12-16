import tkinter as tk
from tkinter import ttk
from analyzer.analyzer_tab import EEGAnalyzerTab
from recorder.recorder_tab import EEGRecorderTab
import psutil, os


class MainApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("EEG NeuroSuite Dark")
        self.root.geometry("1600x900")
        self.root.configure(bg="#0d1226")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        analyzer_tab = EEGAnalyzerTab(notebook)
        notebook.add(analyzer_tab, text="Анализ EEG")

        recorder_tab = EEGRecorderTab(notebook)
        notebook.add(recorder_tab, text="Снятие сигнала")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)

    process = psutil.Process(os.getpid())
    #print(f"Память после запуска GUI: {process.memory_info().rss / 1024 / 1024:.2f} MB")

    root.mainloop()
