# MDMI CLI

Python CLI for controlling the Mega Drive MIDI Interface (MDMI) via SysEx commands. Supports loading presets in WOPN, DMP, and TFI formats with proper instrument selection for WOPN files.

## Features

- Load presets in WOPN, DMP, and TFI formats to MDMI user presets
- WOPN instrument selection: choose specific bank, instrument, and bank type
- Clear individual user presets
- Clear all user presets
- List WOPN file contents for easy instrument browsing
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

# Load specific WOPN instrument to program 10
python -m mdmi.cli load-preset soundbank.wopn --program 10 --bank 0 --instrument 5 --bank-type melody --fake

# List available MIDI ports
python -m mdmi.cli load-preset --list-ports
```

### WOPN file management

```bash
# List contents of a WOPN file
python -m mdmi.cli list-wopn soundbank.wopn

# Load percussion instrument from WOPN
python -m mdmi.cli load-preset soundbank.wopn --program 20 --bank 0 --instrument 3 --bank-type percussion --fake
```

### Clear presets

```bash
# Clear preset at program 5
python -m mdmi.cli clear-preset --program 5 --fake

# Clear all presets (with confirmation)
python -m mdmi.cli clear-all-presets --fake

# Clear all presets (skip confirmation)
python -m mdmi.cli clear-all-presets --fake --confirm
```

## SysEx Format

The MDMI uses the following SysEx format for preset operations:

### Load Preset
```
F0 00 22 77 0A 00 <program> <alg> <fb> <ams> <fms> <operators> F7
```

### Clear Preset
```
F0 00 22 77 0B 00 <program> F7
```

### Clear All Presets
```
F0 00 22 77 0C 00 F7
```

## Supported Formats

### TFI (42 bytes)
- Direct YM2612 FM parameter files
- Algorithm, feedback, and 4 operators
- Commonly used with Deflemask and other trackers

### DMP (DefleMask preset format)
- Supports versions 8, 9, and 11
- FM instruments with full operator data
- Name extraction and version detection

### WOPN (libOPNMIDI bank format)
- Multi-bank instrument collections
- Melody and percussion banks
- Instrument selection by bank/index
- Bank browsing with `list-wopn` command

## Architecture

The CLI uses a modular parser architecture:

- **Format Detection**: Automatic detection based on file headers/size
- **Modular Parsers**: Separate parsers for each format in `mdmi/presets/`
- **Unified Interface**: Common `Preset` and `FMOperator` classes for SysEx generation
- **Field Mapping**: Automatic mapping between format-specific and MDMI field names

## Development

```bash
# Run tests
make test

# Run specific test suites
python -m pytest tests/test_preset_parsers.py -v
python -m pytest tests/test_sysex_generator.py -v
python -m pytest tests/test_e2e_new_parsers.py -v

# Install dependencies
pip install -r requirements.txt

# Check code style
make lint
```

## Dependencies

- `click`: Command-line interface framework
- `mido`: MIDI library for hardware communication
- `bitstruct`: Binary data parsing for preset formats
- `pytest`: Testing framework
