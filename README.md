# Mega Drive MIDI Interface CLI

[![PyPI](https://img.shields.io/pypi/v/mdmi-cli)](https://pypi.org/project/mdmi-cli/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mdmi-cli)](https://pypi.org/project/mdmi-cli/)
[![PyPI - License](https://img.shields.io/pypi/l/mdmi-cli)](https://github.com/rhargreaves/mdmi-cli/blob/main/LICENSE)
[![Build](https://github.com/rhargreaves/mdmi-cli/actions/workflows/build.yml/badge.svg)](https://github.com/rhargreaves/mdmi-cli/actions/workflows/build.yml)

CLI for controlling the [Mega Drive MIDI Interface (MDMI)](https://github.com/rhargreaves/mega-drive-midi-interface). Helps you load presets from instrument files, clear presets, list WOPN instruments, and test connectivity.

## Features

* Load presets from instrument files:
    * DefleMask preset versions 8, 9 and 11
    * [WOPN](https://github.com/Wohlstand/libOPNMIDI/blob/master/fm_banks/wopn%20specification.txt) versions 1 and 2, as used by libOPNMIDI
    * [TFI](https://vgmrips.net/wiki/TFI_File_Format)
* Dump presets from MDMI to files (DMP or TFI format)
* Dump FM channel parameters from MDMI to files (DMP or TFI format)
* Clear presets. Individual user presets or all presets at once
* List WOPN instruments
* Connectivity testing: Ping/pong functionality to test MDMI connectivity

## Installation

Latest version from PyPI:

```bash
pip install mdmi-cli
```

## Usage

### Load a preset

```bash
# Load TFI preset to program 0 (uses MDMI_MIDI_OUT if set)
mdmi load-preset example.tfi --program 0

# Load DMP preset to program 5 via specific MIDI port
mdmi load-preset example.dmp --program 5 --midi-out "IAC Driver Bus 1"

# Load specific WOPN instrument to program 10
mdmi load-preset soundbank.wopn --program 10 --bank 0 --instrument 5 --bank-type melody

# Test with fake interface (for development)
mdmi load-preset example.tfi --program 0 --dry-run
```

### Dump presets

```bash
# Dump preset from program 5 to DMP file (uses MDMI_MIDI_OUT/IN if set)
mdmi dump-preset --program 5 --format dmp --filename my_preset.dmp

# Dump preset from program 10 to TFI file
mdmi dump-preset --program 10 --format tfi --filename my_preset.tfi

# Dump with auto-generated filename (preset_5.dmp)
mdmi dump-preset --program 5

# Test dump with fake interface
mdmi dump-preset --program 0 --dry-run

# Dump with custom timeout and specific ports
mdmi dump-preset --program 3 --timeout 10.0 --midi-out "IAC Driver Bus 1" --midi-in "IAC Driver Bus 2"
```

### Dump FM channel parameters

```bash
# Dump FM channel parameters from MIDI channel 5 to DMP file
mdmi dump-channel --channel 5 --format dmp --filename channel_5.dmp

# Dump FM channel parameters from MIDI channel 3 to TFI file
mdmi dump-channel --channel 3 --format tfi --filename channel_3.tfi

# Dump with auto-generated filename (channel_05.dmp)
mdmi dump-channel --channel 5

# Test channel dump with fake interface
mdmi dump-channel --channel 0 --dry-run

# Dump with custom timeout and specific ports
mdmi dump-channel --channel 7 --timeout 10.0 --midi-out "IAC Driver Bus 1" --midi-in "IAC Driver Bus 2"
```

### WOPN file management

```bash
# List contents of a WOPN file (first 10 instruments per bank)
mdmi list-wopn soundbank.wopn

# List all instruments in WOPN file
mdmi list-wopn soundbank.wopn --full

# Load percussion instrument from WOPN
mdmi load-preset soundbank.wopn --program 20 --bank 0 --instrument 3 --bank-type percussion

# Load from different melody bank
mdmi load-preset soundbank.wopn --program 15 --bank 1 --instrument 65 --bank-type melody
```

### Clear presets

```bash
# Clear preset at program 5 (uses MDMI_MIDI_OUT if set)
mdmi clear-preset --program 5

# Clear all presets (with confirmation)
mdmi clear-all-presets

# Clear all presets (skip confirmation) with specific port
mdmi clear-all-presets --confirm --midi-out "IAC Driver Bus 1"
```

### Test connectivity

```bash
# Test MDMI connectivity with ping/pong
mdmi ping

# Test with custom timeout
mdmi ping --timeout 10.0

# Test with specific ports
mdmi ping --midi-out "IAC Driver Bus 1" --midi-in "IAC Driver Bus 2"
```

### List available MIDI ports

```bash
# List all available MIDI input and output ports
mdmi list-ports
```

## Configuration

### Environment Variables

- **`MDMI_MIDI_OUT`**: Default MIDI output port name
- **`MDMI_MIDI_IN`**: Default MIDI input port name
- **`MDMI_MIDI_PORT`**: Legacy fallback for MIDI output port

### Command-line Options

Most commands support:
- `--midi-out TEXT`: MIDI output port name (overrides environment variables)

Commands with bidirectional communication (`ping`, `dump-preset`, `dump-channel`) also support:
- `--midi-in TEXT`: MIDI input port name (overrides `MDMI_MIDI_IN`)

## Development

### Build

```bash
# Install cli (from source)
make install

# Run tests
make test
```
