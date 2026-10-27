# Tone Generator

Generate sine, square, triangle and sawtooth tones from a Tk GUI or the command line.

## Requirements

- Linux (the install script uses `apt-get`/`dpkg`, so Debian/Ubuntu)
- Python 3.11 or newer, with `venv` (`python3-venv`)
- PortAudio: `libportaudio2`
- For the GUI only: Tk for Python (`python3-tk`)

```sh
sudo apt-get install libportaudio2 python3-venv python3-tk
```

## Install

```sh
./build/install.sh
```

Choose `1` to install for the current user (creates `venv/` in the repository) or `2` to
install system-wide (venv in `/lib/python-venvs/tone-generator-env`, sources in
`/usr/local/share/tone-generator/src`, launcher at `/usr/local/bin/tone_generator`).

To set things up by hand instead:

```sh
python3 -m venv venv
venv/bin/pip install -r build/requirements.txt
```

## Run

`--mode` is required.

```sh
# Local install
./build/tone_generator.sh --mode gui
./build/tone_generator.sh --mode cli --frequency 440 --wave_type sine

# System-wide install
tone_generator --mode gui

# Manual setup
venv/bin/python main.py --mode cli --frequency 440
```

CLI options (all optional):

| Option | Default | Range |
| --- | --- | --- |
| `--frequency` | 440 | above 0 up to 22050 Hz |
| `--duration` | play until quit | seconds, greater than 0 |
| `--volume` | 0.5 | 0.0 to 1.0 |
| `--wave_type` | sine | `sine`, `square`, `triangle`, `sawtooth` |
| `--duty_cycle` | — | 0.01 to 1.0; required for, and only allowed with, `square` |
| `--phase_shift` | 0 | degrees |
| `--pan` | 0.5 | 0.0 (left) to 1.0 (right) |

Type `q` and press Enter to stop, or press Ctrl+C. In the GUI, press `q` to quit.

## Uninstall

```sh
./build/uninstall.sh
```

Removes the local `venv/` and/or the system-wide install, whichever is present.

## Development

```sh
python3 -m venv venv
venv/bin/pip install -r build/requirements-dev.txt
venv/bin/ruff check .
venv/bin/mypy .
venv/bin/pytest
venv/bin/pip-audit -r build/requirements.txt
```

CI runs the same steps on Python 3.11–3.13 (`.github/workflows/ci.yml`).
