import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import messagebox
import argparse
import sys
import os
import threading
import time

# Global variables to hold the current sound data and duration limit
current_stream = None
duration_limit = 60  # Default duration limit
update_delay = 100  # Delay between updates in milliseconds
stop_event = threading.Event()  # Event to signal stopping the tone

def set_system_volume(volume):
    os.system(f"amixer set Master {int(volume * 100)}%")

def generate_wave(frequency, duration, sample_rate, wave_type='sine', duty_cycle=0.5, phase_shift=0):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False, dtype=np.float64)
    phase_shift_radians = phase_shift * (2 * np.pi)
    
    if wave_type == 'sine':
        wave = np.sin(2 * np.pi * frequency * t + phase_shift_radians)
    elif wave_type == 'square':
        wave = np.sign(np.sin(2 * np.pi * frequency * t + phase_shift_radians))
        wave = np.where(wave > 0, 1.0, 0.0) * (wave < duty_cycle) + np.where(wave <= 0, -1.0, 0.0) * (wave >= duty_cycle)
    elif wave_type == 'triangle':
        wave = 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
    elif wave_type == 'sawtooth':
        wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    else:
        raise ValueError("Unsupported wave type")
    
    return np.ascontiguousarray(wave.astype(np.float32))

def apply_pan(wave, pan):
    left = np.clip(1 - pan, 0, 1)
    right = np.clip(pan, 0, 1)
    stereo_wave = np.array([wave * left, wave * right], dtype=np.float32).T
    return np.ascontiguousarray(stereo_wave)

def play_tone_continuously():
    global current_stream, stop_event
    
    sample_rate = 44100
    last_values = {
        "frequency": frequency_slider.get(),
        "volume": volume_slider.get(),
        "pan": pan_slider.get(),
        "phase_shift": phase_shift_slider.get(),
        "wave_type": wave_type_var.get(),
        "duty_cycle": duty_cycle_slider.get() if wave_type_var.get() == 'square' else 0.5
    }

    while not stop_event.is_set():
        frequency = float(frequency_slider.get())
        volume = float(volume_slider.get())
        pan = float(pan_slider.get())
        phase_shift = np.deg2rad(float(phase_shift_slider.get()))
        wave_type = wave_type_var.get()
        duty_cycle = float(duty_cycle_slider.get()) if wave_type == 'square' else 0.5

        if (frequency != last_values["frequency"] or
            volume != last_values["volume"] or
            pan != last_values["pan"] or
            phase_shift != last_values["phase_shift"] or
            wave_type != last_values["wave_type"] or
            duty_cycle != last_values["duty_cycle"]):

            wave = generate_wave(frequency, duration_limit, sample_rate, wave_type, duty_cycle, phase_shift)
            wave = volume * wave
            wave = apply_pan(wave, pan)

            if current_stream:
                current_stream.stop()
                current_stream.close()

            current_stream = sd.OutputStream(channels=2, samplerate=sample_rate)
            current_stream.start()
            current_stream.write(wave)

            last_values.update({
                "frequency": frequency,
                "volume": volume,
                "pan": pan,
                "phase_shift": phase_shift,
                "wave_type": wave_type,
                "duty_cycle": duty_cycle
            })

        time.sleep(update_delay / 1000.0)

def start_tone_thread():
    global stop_event

    stop_event.clear()
    tone_thread = threading.Thread(target=play_tone_continuously)
    tone_thread.start()

def stop_tone():
    global current_stream, stop_event
    stop_event.set()
    if current_stream:
        current_stream.stop()
        current_stream.close()
        current_stream = None

def gui_mode():
    global duration_limit, frequency_slider, volume_slider, phase_shift_slider, duty_cycle_slider, pan_slider, wave_type_var, root

    def start_tone():
        global duration_limit
        duration_limit = float(duration_entry.get() or 60)
        start_tone_thread()

    def stop_tone_gui():
        stop_tone()

    def reset_pan():
        pan_slider.set(0.5)

    def update_duty_cycle_visibility():
        if wave_type_var.get() == 'square':
            duty_cycle_frame.pack(fill='x', pady=5)
            duty_cycle_slider.pack()
        else:
            duty_cycle_slider.pack_forget()
            duty_cycle_frame.pack_forget()

    def on_key_press(event):
        if event.char.lower() == 'q':
            stop_tone_gui()
            root.destroy()

    root = tk.Tk()
    root.title("Tone Generator")
    root.bind('<KeyPress>', on_key_press)

    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10)

    tk.Label(main_frame, text="Frequency (Hz)").pack()
    frequency_slider = tk.Scale(main_frame, from_=20, to=20000, orient=tk.HORIZONTAL)
    frequency_slider.pack()

    tk.Label(main_frame, text="Volume").pack()
    volume_slider = tk.Scale(main_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL)
    volume_slider.pack()

    tk.Label(main_frame, text="Phase Shift (Degrees)").pack()
    phase_shift_slider = tk.Scale(main_frame, from_=0, to=360, orient=tk.HORIZONTAL)
    phase_shift_slider.pack()

    duration_frame = tk.Frame(main_frame)
    tk.Label(duration_frame, text="Duration Limit (Seconds)").pack()
    duration_entry = tk.Entry(duration_frame)
    duration_entry.pack()
    duration_frame.pack(fill='x', pady=5)

    wave_buttons_frame = tk.Frame(main_frame)
    wave_buttons_frame.pack(pady=5)
    wave_type_var = tk.StringVar(value='sine')
    for wave_type in ['sine', 'square', 'triangle', 'sawtooth']:
        tk.Radiobutton(wave_buttons_frame, text=wave_type.capitalize(), variable=wave_type_var, value=wave_type, command=update_duty_cycle_visibility).pack(side=tk.LEFT)

    duty_cycle_frame = tk.Frame(main_frame)
    duty_cycle_label = tk.Label(duty_cycle_frame, text="Duty Cycle (For Square Wave)")
    duty_cycle_label.pack()
    duty_cycle_slider = tk.Scale(duty_cycle_frame, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL)

    pan_frame = tk.Frame(main_frame)
    tk.Label(pan_frame, text="Pan Control (Left/Right)").pack()
    pan_slider = tk.Scale(pan_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL)
    pan_slider.set(0.5)
    pan_slider.pack()
    pan_reset_button = tk.Button(pan_frame, text="Reset Pan", command=reset_pan)
    pan_reset_button.pack()
    pan_frame.pack(fill='x', pady=5)

    start_button = tk.Button(main_frame, text="Start", command=start_tone)
    start_button.pack(pady=5)

    stop_button = tk.Button(main_frame, text="Stop", command=stop_tone_gui)
    stop_button.pack(pady=5)

    update_duty_cycle_visibility()
    root.mainloop()

if __name__ == "__main__":
    if '--cli' in sys.argv or '--CLI' in sys.argv:
        cli_mode()
    elif '--gui' in sys.argv or '--GUI' in sys.argv:
        gui_mode()
    else:
        print("Please run the script with either --cli or --gui flag.")

