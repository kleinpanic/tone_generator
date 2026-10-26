import numpy as np

from audio.playback import ToneGenerator


def _callback(generator, frames):
    out = np.full((frames, 2), 123.0, dtype=np.float32)
    generator.audio_callback(out, frames, None, None)
    return out


def test_callback_wraps_waveform_shorter_than_block():
    # Previously this raised "could not broadcast input array" inside the audio thread.
    generator = ToneGenerator()
    generator.adjust_pan(0.0)
    generator.waveform = np.arange(100, dtype=float)
    out = _callback(generator, 512)
    np.testing.assert_allclose(out[:, 0], np.arange(512) % 100)
    np.testing.assert_allclose(out[:, 1], 0.0, atol=1e-6)
    assert generator.waveform[0] == 512 % 100


def test_callback_outputs_silence_without_waveform():
    # The output buffer is not zeroed by PortAudio; leaving it untouched plays noise.
    generator = ToneGenerator()
    generator.adjust_pan(0.5)
    out = _callback(generator, 256)
    assert not out.any()
