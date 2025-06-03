# MDMI CLI

Python CLI for controlling the Mega Drive MIDI Interface (MDMI) via SysEx commands.

## Features

- Load presets in WOPN, DMP, and TFI formats to MDMI user presets
- Clear individual user presets
- Clear all user presets
- Support for both real MIDI hardware and fake interface for testing

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Load a preset

```bash
# Load TFI preset to program 0
python -m mdmi.cli load-preset example.tfi --program 0 --fake

# Load DMP preset to program 5 via real MIDI port
python -m mdmi.cli load-preset example.dmp --program 5 --port "USB MIDI Interface"

# List available MIDI ports
python -m mdmi.cli load-preset --list-ports
```

### Clear presets

```bash
# Clear preset at program 5
python -m mdmi.cli clear-preset --program 5 --fake

# Clear all user presets (with confirmation)
python -m mdmi.cli clear-all-presets --fake

# Clear all user presets (skip confirmation)
python -m mdmi.cli clear-all-presets --fake --confirm
```

## MDMI SysEx Format

The CLI generates SysEx messages following the MDMI specification:

### Load User FM Preset
```
F0 00 22 77 0A 00 <program> <alg> <fb> <ams> <fms> <op1> <op2> <op3> <op4> F7
```

### Clear User FM Preset
```
F0 00 22 77 0B 00 <program> F7
```

### Clear All User FM Presets
```
F0 00 22 77 0C 00 F7
```

## Supported Preset Formats

- **TFI**: 42-byte FM parameter files
- **DMP**: DefleMask preset format
- **WOPN**: libOPNMIDI bank format

## Development

```bash
# Run tests
make test

# Run linter
make lint

# Install in development mode
make install
```

## Testing

The CLI includes comprehensive tests using pytest and supports a fake MIDI interface for hardware-free testing:

```bash
# Run all tests
python -m pytest

# Test with fake interface
python -m mdmi.cli load-preset example.tfi --program 0 --fake
```

## Architecture

- `mdmi/preset_parsers.py`: Parsers for different preset formats
- `mdmi/sysex_generator.py`: MDMI SysEx message generation
- `mdmi/midi_interface.py`: MIDI communication layer
- `mdmi/cli.py`: Click-based command line interface
