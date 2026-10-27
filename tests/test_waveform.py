import numpy as np
import pytest

from audio.waveform import (
    generate_sawtooth_wave,
    generate_sine_wave,
    generate_square_wave,
    generate_triangle_wave,
)

SAMPLE_RATE = 44100


def test_square_wave_duty_cycle_is_fraction_of_each_period():
    # Previously duty_cycle was compared against absolute time, so the second
    # half of a 1 s buffer at duty 0.5 was pure silence.
    wave = generate_square_wave(441, 1.0, SAMPLE_RATE, 1.0, 0.25)
    assert np.count_nonzero(wave[SAMPLE_RATE // 2:]) == SAMPLE_RATE // 2
    assert np.mean(wave > 0) == pytest.approx(0.25, abs=0.01)
    assert set(np.unique(wave)) == {-1.0, 1.0}


def test_triangle_wave_stays_within_amplitude_and_is_centered():
    # Previously the triangle ranged from 0 to 2 * amplitude (clipping above 0.5 volume).
    wave = generate_triangle_wave(440, 1.0, SAMPLE_RATE, 0.8, 0)
    assert wave.max() <= 0.8 + 1e-9
    assert wave.min() >= -0.8 - 1e-9
    assert abs(wave.mean()) < 1e-2


@pytest.mark.parametrize("generator", [generate_triangle_wave, generate_sawtooth_wave])
def test_phase_shift_is_applied(generator):
    # Previously phase_shift was accepted but ignored for triangle and sawtooth.
    base = generator(441, 1.0, SAMPLE_RATE, 1.0, 0)
    shifted = generator(441, 1.0, SAMPLE_RATE, 1.0, 90)
    quarter_period = SAMPLE_RATE // 441 // 4
    assert not np.allclose(base, shifted)
    # Allow a few samples to differ where rounding lands on the opposite side of a sawtooth jump
    matches = np.isclose(shifted[:-quarter_period], base[quarter_period:], atol=1e-6)
    assert matches.mean() > 0.999


def test_sine_wave_unchanged():
    wave = generate_sine_wave(440, 1.0, SAMPLE_RATE, 0.5, 0)
    assert len(wave) == SAMPLE_RATE
    assert wave.max() == pytest.approx(0.5, abs=1e-4)
