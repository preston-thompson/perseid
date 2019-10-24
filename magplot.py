#!/usr/bin/env python3

import os
import sys

import PySimpleGUI as sg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

plt.ion()

layout = [
    [sg.Text("Magnitude file:"), sg.Input(), sg.FileBrowse()],
    [sg.Text("Magnitude rate (Hz):"), sg.Input()],
    [sg.Button("Plot")]
]

window = sg.Window("MagPlot", layout)

while True:
    event, values = window.Read()
    if event is None:
        sys.exit(0)
    if event is "Plot":
        filename = values[0]
        mag_rate = float(values[1])
        if not os.path.exists(filename):
            sg.Popup("File does not exist")
            continue
        mag = np.fromfile(open(filename, "rb"), np.float32)
        plt.figure()
        plt.title(filename)
        plt.xlabel("Time (sec)")
        plt.ylabel("Magnitude (dB)")
        plt.plot(np.arange(0, float(len(mag))/mag_rate, 1/mag_rate), mag)
        plt.show()

