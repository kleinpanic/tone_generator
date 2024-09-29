import tkinter as tk
from tkinter import Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class WaveformVisualizer:
    def __init__(self, master, get_waveform_snapshot_callback):
        self.master = master
        self.get_waveform_snapshot_callback = get_waveform_snapshot_callback
        self.window = None
        self.canvas = None
        self.figure = None
        self.ax = None
        self.plot_line = None
        self.is_open = False

    def open_window(self):
        if self.is_open:
            self.window.lift()
            return

        self.window = Toplevel(self.master)
        self.window.title("Waveform Visualization")
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        # Create the matplotlib figure and axis
        self.figure, self.ax = plt.subplots()
        self.ax.set_title('Waveform')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Amplitude')
        self.ax.grid(True)

        # Create a Tkinter-compatible canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Reset the plot line when the window is reopened
        self.plot_line = None

        # Start updating the plot
        self.is_open = True
        self.update_plot()

    def update_plot(self):
        if not self.is_open:
            return

        # Get a snapshot of the current waveform
        waveform_snapshot = self.get_waveform_snapshot_callback()
        if waveform_snapshot is not None:
            time_data = np.linspace(0, len(waveform_snapshot) / 44100, len(waveform_snapshot))
            if self.plot_line is None:
                self.plot_line, = self.ax.plot(time_data, waveform_snapshot, color='blue')  # Set plot color to blue
            else:
                self.plot_line.set_ydata(waveform_snapshot)
                self.plot_line.set_xdata(time_data)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()

        # Schedule the next update
        self.window.after(100, self.update_plot)  # Update every 100ms

    def close_window(self):
        self.is_open = False
        if self.window is not None:
            self.window.destroy()
        self.window = None  # Reset the window so it can be recreated

    def toggle_window(self):
        if self.is_open:
            self.close_window()
        else:
            self.open_window()

