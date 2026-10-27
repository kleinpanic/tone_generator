import argparse
import math
import threading
from audio.playback import ToneGenerator
from audio.waveform import generate_sine_wave, generate_square_wave, generate_triangle_wave, generate_sawtooth_wave

# Highest frequency representable at the playback sample rate (Nyquist limit)
MAX_FREQUENCY = 22050
# Length of the looped waveform buffer; a fixed size keeps memory bounded for any --duration
BUFFER_SECONDS = 1.0

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Tone Generator CLI")
    parser.add_argument("--frequency", type=float, default=440, help="Frequency of the tone in Hz")
    parser.add_argument("--duration", type=float, help="Duration of the tone in seconds (default is infinite)")
    parser.add_argument("--volume", type=float, default=0.5, help="Volume level (0.0 to 1.0)")
    parser.add_argument("--wave_type", type=str, choices=["sine", "square", "triangle", "sawtooth"], default="sine", help="Waveform type")
    parser.add_argument("--duty_cycle", type=float, default=None, help="Duty cycle for square wave (0.01 to 1.0, required for square wave)")
    parser.add_argument("--phase_shift", type=float, default=0, help="Phase shift in degrees (0 to 360)")
    parser.add_argument("--pan", type=float, default=0.5, help="Pan control (0.0 for full left, 1.0 for full right)")
    
    args = parser.parse_args(argv)

    # Range checks are written as "not (low <= x <= high)" so NaN is rejected too
    if not (0 < args.frequency <= MAX_FREQUENCY):
        parser.error(f"--frequency must be greater than 0 and at most {MAX_FREQUENCY} Hz.")
    if args.duration is not None and not (0 < args.duration <= threading.TIMEOUT_MAX):
        parser.error("--duration must be a positive number of seconds.")
    if not (0.0 <= args.volume <= 1.0):
        parser.error("--volume must be between 0.0 and 1.0.")
    if not (0.0 <= args.pan <= 1.0):
        parser.error("--pan must be between 0.0 and 1.0.")
    if not math.isfinite(args.phase_shift):
        parser.error("--phase_shift must be a finite number of degrees.")
    if args.duty_cycle is not None and not (0.01 <= args.duty_cycle <= 1.0):
        parser.error("--duty_cycle must be between 0.01 and 1.0.")

    # Ensure duty_cycle is provided if square wave is selected
    if args.wave_type == "square" and args.duty_cycle is None:
        parser.error("--duty_cycle must be specified when --wave_type is 'square'.")

    # Prevent duty_cycle from being specified if the waveform is not square
    if args.wave_type != "square" and args.duty_cycle is not None:
        parser.error("--duty_cycle can only be used with --wave_type 'square'.")

    return args

def listen_for_quit(stop_event):
    while not stop_event.is_set():
        try:
            user_input = input()
        except EOFError:
            return  # stdin is closed; playback ends on --duration or Ctrl+C
        if user_input.strip().lower() == 'q':
            stop_event.set()
            return

def main():
    args = parse_args()
    tone_generator = ToneGenerator()

    waveform_type = args.wave_type
    sample_rate = tone_generator.sample_rate

    if waveform_type == "sine":
        waveform = generate_sine_wave(args.frequency, BUFFER_SECONDS, sample_rate, args.volume, args.phase_shift)
    elif waveform_type == "square":
        waveform = generate_square_wave(args.frequency, BUFFER_SECONDS, sample_rate, args.volume, args.duty_cycle)
    elif waveform_type == "triangle":
        waveform = generate_triangle_wave(args.frequency, BUFFER_SECONDS, sample_rate, args.volume, args.phase_shift)
    elif waveform_type == "sawtooth":
        waveform = generate_sawtooth_wave(args.frequency, BUFFER_SECONDS, sample_rate, args.volume, args.phase_shift)

    tone_generator.start(waveform, pan=args.pan)
    print(f"Playing {waveform_type} wave at {args.frequency} Hz. Press 'q' then Enter to quit.")

    stop_event = threading.Event()
    quit_listener = threading.Thread(target=listen_for_quit, args=(stop_event,))
    quit_listener.daemon = True
    quit_listener.start()

    try:
        # Returns when 'q' is entered or, if a duration was given, when it elapses
        stop_event.wait(timeout=args.duration)
    except KeyboardInterrupt:
        pass
    finally:
        tone_generator.stop()

if __name__ == "__main__":
    main()
