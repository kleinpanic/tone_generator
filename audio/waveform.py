
import numpy as np

def _cycle_position(frequency, duration, sample_rate, phase_shift):
    # Position within each cycle as a fraction in [0, 1), including the phase shift
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.mod(t * frequency + phase_shift / 360.0, 1.0)

def generate_sine_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return amplitude * np.sin(2 * np.pi * frequency * t + np.deg2rad(phase_shift))

def generate_square_wave(frequency, duration, sample_rate, amplitude, duty_cycle):
    # duty_cycle is the fraction (0 to 1) of each period spent high
    position = _cycle_position(frequency, duration, sample_rate, 0)
    return amplitude * np.where(position < duty_cycle, 1.0, -1.0)

def generate_triangle_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    position = _cycle_position(frequency, duration, sample_rate, phase_shift)
    return amplitude * (1 - 4 * np.abs(position - 0.5))

def generate_sawtooth_wave(frequency, duration, sample_rate, amplitude, phase_shift):
    position = _cycle_position(frequency, duration, sample_rate, phase_shift)
    return amplitude * (2 * np.mod(position + 0.5, 1.0) - 1)
