import sounddevice as sd
import numpy as np

class ToneGenerator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.stream = None
        self.waveform = None
        self.is_playing = False

    def start(self, waveform, pan=0.5):
        self.waveform = waveform
        self.stream = sd.OutputStream(callback=self.audio_callback, samplerate=self.sample_rate, channels=2)
        self.is_playing = True
        
        # Adjust waveform for panning
        self.adjust_pan(pan)
        
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.is_playing = False

    def audio_callback(self, outdata, frames, time, status):
        if self.waveform is None or len(self.waveform) == 0:
            outdata.fill(0)  # The buffer is not zeroed for us; silence instead of noise
            return
        # Wrap around so waveforms shorter than the requested block still fill it
        chunk = np.take(self.waveform, np.arange(frames), mode="wrap")
        outdata[:, 0] = chunk * self.left_gain  # Left channel
        outdata[:, 1] = chunk * self.right_gain  # Right channel
        self.waveform = np.roll(self.waveform, -(frames % len(self.waveform)))

    def adjust_pan(self, pan):
        # Calculate left and right channel gains based on pan
        self.left_gain = np.cos(pan * np.pi / 2)
        self.right_gain = np.sin(pan * np.pi / 2)

