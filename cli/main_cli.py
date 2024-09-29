import argparse
import time
import sys
import threading
from audio.playback import ToneGenerator
from audio.waveform import generate_sine_wave, generate_square_wave, generate_triangle_wave, generate_sawtooth_wave

def parse_args():
    parser = argparse.ArgumentParser(description="Tone Generator CLI")
    parser.add_argument("--frequency", type=float, default=440, help="Frequency of the tone in Hz")
    parser.add_argument("--duration", type=float, help="Duration of the tone in seconds (default is infinite)")
    parser.add_argument("--volume", type=float, default=0.5, help="Volume level (0.0 to 1.0)")
    parser.add_argument("--wave_type", type=str, choices=["sine", "square", "triangle", "sawtooth"], default="sine", help="Waveform type")
    parser.add_argument("--duty_cycle", type=float, default=None, help="Duty cycle for square wave (0.01 to 1.0, required for square wave)")
    parser.add_argument("--phase_shift", type=float, default=0, help="Phase shift in degrees (0 to 360)")
    parser.add_argument("--pan", type=float, default=0.5, help="Pan control (0.0 for full left, 1.0 for full right)")
    
    args = parser.parse_args()

    # Ensure duty_cycle is provided if square wave is selected
    if args.wave_type == "square" and args.duty_cycle is None:
        parser.error("--duty_cycle must be specified when --wave_type is 'square'.")

    # Prevent duty_cycle from being specified if the waveform is not square
    if args.wave_type != "square" and args.duty_cycle is not None:
        parser.error("--duty_cycle can only be used with --wave_type 'square'.")

    return args

def listen_for_quit(tone_generator):
    while True:
        user_input = input()
        if user_input.lower() == 'q':
            tone_generator.stop()
            sys.exit()

def main():
    args = parse_args()
    tone_generator = ToneGenerator()

    waveform_type = args.wave_type
    sample_rate = tone_generator.sample_rate

    if waveform_type == "sine":
        waveform = generate_sine_wave(args.frequency, args.duration or 1.0, sample_rate, args.volume, args.phase_shift)
    elif waveform_type == "square":
        waveform = generate_square_wave(args.frequency, args.duration or 1.0, sample_rate, args.volume, args.duty_cycle)
    elif waveform_type == "triangle":
        waveform = generate_triangle_wave(args.frequency, args.duration or 1.0, sample_rate, args.volume, args.phase_shift)
    elif waveform_type == "sawtooth":
        waveform = generate_sawtooth_wave(args.frequency, args.duration or 1.0, sample_rate, args.volume, args.phase_shift)

    tone_generator.start(waveform)
    print(f"Playing {waveform_type} wave at {args.frequency} Hz. Press 'q' to quit.")

    if args.duration:
        quit_listener = threading.Thread(target=listen_for_quit, args=(tone_generator,))
        quit_listener.daemon = True
        quit_listener.start()

        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            pass
        finally:
            tone_generator.stop()
    else:
        listen_for_quit(tone_generator)

if __name__ == "__main__":
    main()
