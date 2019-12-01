#!/usr/bin/env python3

import math
import os
import time

from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
import matplotlib.pyplot as plt
import numpy as np

def main():
    plt.ion()

    window = Tk()
    window.resizable(False, False)
    window.title("Perseid")

    row = 0

    lbl_power = Label(window, text="IQ file settings", font="Helvetica 11 bold")
    lbl_power.grid(column=1, row=row)

    row += 1

    label_width = 30
    entry_width = 30

    lbl_iq_file = Label(window, text="IQ file: ", width=label_width, anchor="e")
    lbl_iq_file.grid(column=0, row=row)

    str_iq_file = StringVar()

    txt_iq_file = Entry(window, width=entry_width, textvariable=str_iq_file)
    txt_iq_file.grid(column=1, row=row)

    def btn_iq_file_clicked():
        str_iq_file.set(filedialog.askopenfilename(parent=window, title="Choose an IQ file"))

    btn_iq_file = Button(window, text="Browse", command=btn_iq_file_clicked)
    btn_iq_file.grid(column=2, row=row, padx=(5, 5))

    row += 1

    lbl_bw = Label(window, text="Bandwidth (kHz): ", width=label_width, anchor="e")
    lbl_bw.grid(column=0, row=row)

    str_bw = StringVar()
    str_bw.set("2")

    txt_bw = Entry(window, width=entry_width, textvariable=str_bw)
    txt_bw.grid(column=1, row=row)

    row += 1

    lbl_nothing = Label(window, text="")
    lbl_nothing.grid(column=0, row=row)

    row += 1

    lbl_power = Label(window, text="Power plot settings", font="Helvetica 11 bold")
    lbl_power.grid(column=1, row=row)

    row += 1

    lbl_power_dt = Label(window, text="Temporal resolution (sec): ", width=label_width, anchor="e")
    lbl_power_dt.grid(column=0, row=row)

    str_power_dt = StringVar()
    str_power_dt.set("5")

    txt_power_dt = Entry(window, width=entry_width, textvariable=str_power_dt)
    txt_power_dt.grid(column=1, row=row)

    row += 1

    lbl_power_n = Label(window, text="FFT size: ", width=label_width, anchor="e")
    lbl_power_n.grid(column=0, row=row)

    str_power_n = StringVar()
    str_power_n.set("1024")

    txt_power_n = Entry(window, width=entry_width, textvariable=str_power_n)
    txt_power_n.grid(column=1, row=row)

    row += 1

    lbl_power_notch_bw = Label(window, text="Center notch filter bandwidth (Hz): ", width=label_width, anchor="e")
    lbl_power_notch_bw.grid(column=0, row=row)

    str_power_notch_bw = StringVar()
    str_power_notch_bw.set("20")

    txt_power_notch_bw = Entry(window, width=entry_width, textvariable=str_power_notch_bw)
    txt_power_notch_bw.grid(column=1, row=row)

    row += 1

    def power_plot():
        try:
            bw = float(str_bw.get()) * 1E3
        except:
            messagebox.showerror("Error", "Bad bandwidth setting.")
            return
        if bw <= 0:
            messagebox.showerror("Error", "Bandwidth must be greater than zero.")
            return

        try:
            dt = float(str_power_dt.get())
        except:
            messagebox.showerror("Error", "Bad temporal resolution setting.")
            return
        if dt <= 0:
            messagebox.showerror("Error", "Temporal resolution must be greater than zero.")
            return

        try:
            notch_bw = float(str_power_notch_bw.get())
        except:
            messagebox.showerror("Error", "Bad center notch filter bandwidth setting.")
            return
        if notch_bw <= 0:
            messagebox.showerror("Error", "Center notch filter bandwidth setting must be greater than zero.")
            return

        n = int(str_power_n.get())

        index_dt = int(dt*bw)
        power = []
        iq_len = os.path.getsize(str_iq_file.get()) // 8
        f = open(str_iq_file.get(), "rb")

        win_progress = Toplevel()
        win_progress.attributes('-type', 'dialog')
        win_progress.grab_set()
        win_progress.title("Power plot")
        lbl_step = Label(win_progress)
        lbl_step.grid(column=0, row=0, pady=(5, 5), padx=(5, 5))
        progress = ttk.Progressbar(win_progress, orient=HORIZONTAL, length=100, mode='determinate')
        progress.grid(column=0, row=1, pady=(0, 5), padx=(5, 5))

        next_win_update = time.time() + 0.2

        for i in range(int(iq_len//index_dt)):

            if time.time() > next_win_update:
                lbl_step.configure(text=f"Crunching FFT ({i}/{iq_len//index_dt})")
                progress.config(mode="determinate",maximum=iq_len//index_dt, value=i)
                win_progress.update()
                window.update()
                next_win_update += 0.2

            f.seek(i*index_dt*8)

            # Load a chunk of the data for processing.
            iq_slice = np.fromfile(f, np.complex64, count=index_dt)

            # Find the spectrum of the chunk.
            fft = 20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(iq_slice, n=n))))

            # Notch out the center frequency.
            blank = notch_bw/bw*len(fft)
            for j in range(int(len(fft)/2-blank/2), int(len(fft)/2+blank/2)):
                fft[j] = -np.Inf

            power.append(max(fft) - np.median(fft))

        win_progress.destroy()

        plt.figure()
        plt.title(str_iq_file.get())
        plt.xlabel("Time (sec)")
        plt.ylabel("Power (dB)")
        t = np.arange(0, iq_len/bw, dt)
        plt.plot(t[:len(power)], power)
        plt.show()

    btn_power_plot = Button(window, text="Power plot", command=power_plot)
    btn_power_plot.grid(column=1, row=row, pady=(5, 5))

    row += 1

    lbl_nothing2 = Label(window, text="")
    lbl_nothing2.grid(column=0, row=row)

    row += 1

    lbl_power = Label(window, text="Spectrogram settings", font="Helvetica 11 bold")
    lbl_power.grid(column=1, row=row)

    row += 1

    lbl_spectrogram_N = Label(window, text="FFT size: ", width=label_width, anchor="e")
    lbl_spectrogram_N.grid(column=0, row=row)

    str_spectrogram_N = StringVar()
    str_spectrogram_N.set("1024")

    txt_spectrogram_N = Entry(window, width=entry_width, textvariable=str_spectrogram_N)
    txt_spectrogram_N.grid(column=1, row=row)

    row += 1

    lbl_spectrogram_t0 = Label(window, text="Start time (sec): ", width=label_width, anchor="e")
    lbl_spectrogram_t0.grid(column=0, row=row)

    str_spectrogram_t0 = StringVar()

    txt_spectrogram_t0 = Entry(window, width=entry_width, textvariable=str_spectrogram_t0)
    txt_spectrogram_t0.grid(column=1, row=row)

    row += 1

    lbl_spectrogram_t1 = Label(window, text="End time (sec): ", width=label_width, anchor="e")
    lbl_spectrogram_t1.grid(column=0, row=row)

    str_spectrogram_t1 = StringVar()

    txt_spectrogram_t1 = Entry(window, width=entry_width, textvariable=str_spectrogram_t1)
    txt_spectrogram_t1.grid(column=1, row=row)

    row += 1

    def spectrogram_plot():
        try:
            bw = float(str_bw.get()) * 1E3
        except:
            messagebox.showerror("Error", "Bad bandwidth setting.")
            return
        if bw <= 0:
            messagebox.showerror("Error", "Bandwidth must be greater than zero.")
            return

        try:
            t0 = float(str_spectrogram_t0.get())
        except:
            messagebox.showerror("Error", "Bad start time.")
            return
        if t0 < 0:
            messagebox.showerror("Error", "Start time cannot be negative.")
            return

        try:
            t1 = float(str_spectrogram_t1.get())
        except:
            messagebox.showerror("Error", "Bad end time.")
            return
        if t1 <= t0:
            messagebox.showerror("Error", "End time must be greater than start time.")
            return

        iq_len = os.path.getsize(str_iq_file.get()) // 8

        index_t0 = int(t0*bw)
        if index_t0 >= iq_len:
            messagebox.showerror("Error", "Start time is beyond the data.")
            return

        index_t1 = int(t1*bw)
        if index_t1 <= index_t0:
            messagebox.showerror("Error", "End time must be greater than start time.")
            return
        if index_t1 > iq_len:
            messagebox.showerror("Error", "End time is beyond the data.")
            return

        f = open(str_iq_file.get(), "rb")
        f.seek(index_t0*8)
        iq_slice = np.fromfile(f, np.complex64, count=index_t1-index_t0)

        plt.figure()
        NFFT = int(str_spectrogram_N.get())
        Pxx, freqs, bins, im = plt.specgram(iq_slice, NFFT=NFFT, Fs=bw, noverlap=NFFT/2, cmap=plt.get_cmap("magma"), xextent=(t0,t1))

        plt.ylabel("Doppler shift (Hz)")
        plt.xlabel("Time (sec)")

        # Rescale the plot's colors so that the median noise power is black.
        vmin = 10*math.log10(np.median(Pxx))
        vmax = 10*math.log10(np.max(Pxx))
        im.set_clim(vmin=vmin, vmax=vmax)

        plt.colorbar(im).set_label("Power (dB)")
        plt.show()

    btn_spectrogram_plot = Button(window, text="Spectrogram plot", command=spectrogram_plot)
    btn_spectrogram_plot.grid(column=1, row=row, pady=(5, 5))

    window.mainloop()

if __name__ == "__main__":
        main()
