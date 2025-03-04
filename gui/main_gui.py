import tkinter as tk
from tkinter import ttk
from audio.playback import ToneGenerator
from audio.waveform import generate_sine_wave, generate_square_wave, generate_triangle_wave, generate_sawtooth_wave
from waveform_visualizer.waveform_visualizer import WaveformVisualizer  # Import the new module

class ToneGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tone Generator")
        self.geometry("500x500")  # Adjusted to be a bit taller for the dark mode button
        self.tone_generator = ToneGenerator()
        self.is_playing = False  # Track if the tone is currently playing
        self.duration = 1.0  # Default duration
        self.waveform_visualizer = WaveformVisualizer(self, self.get_current_waveform_snapshot)  # Initialize the visualizer
        self.dark_mode = False  # Track if dark mode is enabled
        self.style = ttk.Style()  # Create a style object for ttk widgets
        self.create_widgets()

        # Bind 'q' key to quit the application
        self.bind('<q>', self.quit_application)

    def create_widgets(self):
        # Waveform selection
        self.waveform_var = tk.StringVar(value="sine")
        waveform_options = ["sine", "square", "triangle", "sawtooth"]
        ttk.Label(self, text="Waveform:").pack(fill=tk.X, padx=5, pady=5)
        waveform_menu = ttk.Combobox(self, textvariable=self.waveform_var, values=waveform_options)
        waveform_menu.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind selection event to dynamically show/hide the Duty Cycle slider and label
        waveform_menu.bind("<<ComboboxSelected>>", self.on_waveform_change)
        
        # Frequency, Volume, Pan, and Phase Shift Sliders
        self.frequency_scale = self.create_scale("Frequency (Hz)", 20, 20000, 440)
        self.volume_scale = self.create_scale("Volume", 0.0, 1.0, 0.5)
        self.pan_frame = self.create_pan_control()  # Pan control with reset button
        
        # Duty Cycle Frame (Initially hidden)
        self.duty_cycle_frame = ttk.Frame(self)
        self.duty_cycle_label = ttk.Label(self.duty_cycle_frame, text="Duty Cycle")
        self.duty_cycle_label.pack(side="left")
        self.duty_cycle_scale = tk.Scale(self.duty_cycle_frame, from_=0, to=100, orient="horizontal")
        self.duty_cycle_scale.set(50)
        self.duty_cycle_scale.pack(side="right", fill=tk.X, expand=True)
        self.duty_cycle_frame.pack_forget()

        # Phase Shift Slider
        self.phase_scale = self.create_scale("Phase Shift", 0, 360, 0)

        # Start and Stop Buttons
        self.start_button = ttk.Button(self, text="Start", command=self.start_tone)
        self.start_button.pack(fill=tk.X, padx=5, pady=5)
        self.stop_button = ttk.Button(self, text="Stop", command=self.stop_tone)
        self.stop_button.pack(fill=tk.X, padx=5, pady=5)

        # Show/Hide Waveform Button
        self.waveform_button = ttk.Button(self, text="Show Waveform", command=self.toggle_waveform_window)
        self.waveform_button.pack(fill=tk.X, padx=5, pady=5)

        # Toggle Dark Mode Button
        self.dark_mode_button = ttk.Button(self, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(fill=tk.X, padx=5, pady=5)

        # Indicator dot to show if tone is playing
        self.indicator_dot = tk.Canvas(self, width=20, height=20, bg="black")
        self.indicator_dot.pack(pady=10)

        # Bind sliders to automatically update the tone if it's playing
        self.frequency_scale.config(command=self.update_tone)
        self.volume_scale.config(command=self.update_tone)
        self.pan_scale.config(command=self.update_tone)
        self.phase_scale.config(command=self.update_tone)
        self.duty_cycle_scale.config(command=self.update_tone)

    def create_scale(self, label, min_val, max_val, init_val):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        if label:
            ttk.Label(frame, text=label).pack(side="left")
        scale = tk.Scale(frame, from_=min_val, to=max_val, orient="horizontal", resolution=0.01 if max_val == 1 else 1)
        scale.set(init_val)
        scale.pack(side="right", fill=tk.X, expand=True)
        return scale

    def create_pan_control(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(frame, text="Pan").pack(side="left")
        self.pan_scale = tk.Scale(frame, from_=0.0, to=1.0, orient="horizontal", resolution=0.01)
        self.pan_scale.set(0.5)
        self.pan_scale.pack(side="left", fill=tk.X, expand=True)

        reset_button = ttk.Button(frame, text="Center", command=self.reset_pan)
        reset_button.pack(side="right")
        return frame

    def reset_pan(self):
        self.pan_scale.set(0.5)
        self.update_tone(None)

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.apply_light_mode()
        else:
            self.apply_dark_mode()
        self.dark_mode = not self.dark_mode  # Toggle the dark mode flag

        for widget in self.winfo_children():
            widget.update_idletasks()

    def apply_dark_mode(self):
        dark_bg = "#2E2E2E"
        light_fg = "#FFFFFF"
        
        self.configure(bg=dark_bg)
        
        # Apply styles to ttk widgets
        self.style.theme_use("clam")
        self.style.configure("TCombobox", fieldbackground=dark_bg, background=dark_bg, foreground=light_fg)
        self.style.configure("TLabel", background=dark_bg, foreground=light_fg)
        self.style.configure("TButton", background=dark_bg, foreground=light_fg)
        self.style.configure("TFrame", background=dark_bg)
        self.style.configure("Horizontal.TScale", background=dark_bg, troughcolor=dark_bg)

        for widget in self.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.configure(bg="black")
            widget.update_idletasks()

    def apply_light_mode(self):
        light_bg = "#FFFFFF"
        dark_fg = "#000000"
        
        self.configure(bg=light_bg)
        
        # Apply styles to ttk widgets
        self.style.theme_use("clam")
        self.style.configure("TCombobox", fieldbackground=light_bg, background=light_bg, foreground=dark_fg)
        self.style.configure("TLabel", background=light_bg, foreground=dark_fg)
        self.style.configure("TButton", background=light_bg, foreground=dark_fg)
        self.style.configure("TFrame", background=light_bg)
        self.style.configure("Horizontal.TScale", background=light_bg, troughcolor=light_bg)

        for widget in self.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.configure(bg="white")
            widget.update_idletasks()

    def on_waveform_change(self, event):
        selected_waveform = self.waveform_var.get()
        if selected_waveform == "square":
            self.duty_cycle_frame.pack(before=self.phase_scale.master)  # Show the Duty Cycle frame before the Phase Shift frame
        else:
            self.duty_cycle_frame.pack_forget()  # Hide the Duty Cycle frame
        self.update_tone(None)

    def start_tone(self):
        if self.is_playing:
            self.stop_tone()  # Ensure the previous tone is stopped

        frequency = self.frequency_scale.get()
        volume = self.volume_scale.get()
        pan = self.pan_scale.get()
        phase = self.phase_scale.get()

        waveform_type = self.waveform_var.get()
        if waveform_type == "square":
            duty_cycle = self.duty_cycle_scale.get() / 100.0  # Convert to a fraction
            waveform = generate_square_wave(frequency, self.duration, self.tone_generator.sample_rate, volume, duty_cycle)
        else:
            waveform = self.get_waveform(waveform_type, frequency, volume, phase)

        self.tone_generator.start(waveform, pan=pan)
        self.is_playing = True
        self.start_button.config(state="disabled")  # Disable the Start button
        self.update_indicator()

    def stop_tone(self):
        self.tone_generator.stop()
        self.is_playing = False
        self.start_button.config(state="normal")  # Re-enable the Start button
        self.update_indicator()

    def get_waveform(self, waveform_type, frequency, volume, phase):
        if waveform_type == "sine":
            return generate_sine_wave(frequency, self.duration, self.tone_generator.sample_rate, volume, phase)
        elif waveform_type == "triangle":
            return generate_triangle_wave(frequency, self.duration, self.tone_generator.sample_rate, volume, phase)
        elif waveform_type == "sawtooth":
            return generate_sawtooth_wave(frequency, self.duration, self.tone_generator.sample_rate, volume, phase)

    def toggle_waveform_window(self):
        self.waveform_visualizer.toggle_window()

    def update_tone(self, event):
        if self.is_playing:
            self.stop_tone()
            self.start_tone()

    def update_indicator(self):
        color = "green" if self.is_playing else "black"
        self.indicator_dot.config(bg=color)

    def quit_application(self, event=None):
        self.stop_tone()
        self.waveform_visualizer.close_window()
        self.destroy()

    def get_current_waveform_snapshot(self):
        # Fetch a snapshot of the current waveform without interrupting the playback
        if self.tone_generator.waveform is not None:
            # Return a small snapshot of the waveform
            snapshot_length = min(4410, len(self.tone_generator.waveform))  # Get a snapshot of 0.1 seconds
            return self.tone_generator.waveform[:snapshot_length]
        return None

if __name__ == "__main__":
    app = ToneGeneratorGUI()
    app.mainloop()

