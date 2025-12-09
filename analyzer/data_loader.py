import pandas as pd
import numpy as np


def load_eeg(path):
    df = pd.read_csv(path, sep=';', header=None)
    t = df.iloc[:, 0].values
    sig = df.iloc[:, 1].values
    fs = 1 / np.mean(np.diff(t))
    return t, sig, fs
