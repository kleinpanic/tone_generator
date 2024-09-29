import numpy as np

def generate_sine_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t + np.deg2rad(phase_shift))

def generate_square_wave(frequency, duration, sample_rate, amplitude, duty_cycle):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sign(np.sin(2 * np.pi * frequency * t)) * (t < duty_cycle)

def generate_triangle_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * 2 * np.abs(2 * (t * frequency - np.floor(1/2 + t * frequency)))

def generate_sawtooth_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * (2 * (t * frequency - np.floor(1/2 + t * frequency)))

