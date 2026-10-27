import sys
import time

import pytest

import main as entrypoint
from cli import main_cli


@pytest.mark.parametrize(
    "argv",
    [
        ["--frequency", "0"],
        ["--frequency", "-5"],
        ["--frequency", "nan"],
        ["--frequency", "100000"],
        ["--duration", "-1"],
        ["--duration", "0"],
        ["--duration", "inf"],
        ["--volume", "5"],
        ["--volume", "nan"],
        ["--pan", "-0.1"],
        ["--phase_shift", "inf"],
        ["--wave_type", "square", "--duty_cycle", "0"],
        ["--wave_type", "square", "--duty_cycle", "2"],
    ],
)
def test_parse_args_rejects_out_of_range_values(argv):
    with pytest.raises(SystemExit) as excinfo:
        main_cli.parse_args(argv)
    assert excinfo.value.code == 2


def test_parse_args_accepts_valid_values():
    args = main_cli.parse_args(
        ["--frequency", "880", "--duration", "2", "--volume", "1", "--pan", "0",
         "--wave_type", "square", "--duty_cycle", "0.3"]
    )
    assert args.frequency == 880 and args.duty_cycle == 0.3


class FakeToneGenerator:
    sample_rate = 44100

    def __init__(self):
        self.started_with = None
        self.stopped = False

    def start(self, waveform, pan=0.5):
        self.started_with = (waveform, pan)

    def stop(self):
        self.stopped = True


@pytest.fixture
def fake_generator(monkeypatch):
    generator = FakeToneGenerator()
    monkeypatch.setattr(main_cli, "ToneGenerator", lambda: generator)
    return generator


def _run_cli(monkeypatch, argv, input_func):
    monkeypatch.setattr(sys, "argv", ["main_cli"] + argv)
    monkeypatch.setattr("builtins.input", input_func)
    started = time.monotonic()
    main_cli.main()
    return time.monotonic() - started


def test_cli_passes_pan_to_playback(monkeypatch, fake_generator):
    # Previously --pan was parsed but never passed to ToneGenerator.start.
    _run_cli(monkeypatch, ["--pan", "0.0", "--duration", "0.05"], lambda: (_ for _ in ()).throw(EOFError))
    assert fake_generator.started_with[1] == 0.0
    assert fake_generator.stopped


def test_cli_quit_key_stops_before_duration(monkeypatch, fake_generator):
    # Previously 'q' called sys.exit() in a daemon thread, which only ended that thread,
    # so playback kept running until --duration elapsed.
    elapsed = _run_cli(monkeypatch, ["--duration", "30"], lambda: "q")
    assert elapsed < 5
    assert fake_generator.stopped


def test_cli_closed_stdin_does_not_crash(monkeypatch, fake_generator):
    # Previously input() raised EOFError when stdin was not interactive.
    def eof():
        raise EOFError

    _run_cli(monkeypatch, ["--duration", "0.05"], eof)
    assert fake_generator.stopped


def test_long_duration_does_not_allocate_full_length_buffer(monkeypatch, fake_generator):
    # Previously a buffer of duration * sample_rate samples was allocated up front.
    _run_cli(monkeypatch, ["--duration", "1000000"], lambda: "q")
    waveform, _ = fake_generator.started_with
    assert len(waveform) == fake_generator.sample_rate


def test_cli_mode_does_not_import_gui(monkeypatch):
    # Previously main.py imported the GUI at module load, so CLI mode failed without tkinter.
    calls = []
    monkeypatch.setitem(sys.modules, "gui.main_gui", None)  # any import of it now fails
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "cli", "--duration", "1"])
    monkeypatch.setattr(main_cli, "main", lambda: calls.append(sys.argv))
    entrypoint.main()
    assert calls == [["main.py", "--duration", "1"]]
