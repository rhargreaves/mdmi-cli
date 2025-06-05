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
* Performance testing: Continuous latency measurement with statistics and histogram generation

## Installation

Latest version from PyPI:

```bash
pip install mdmi-cli
```

## Usage

### Load a preset

```bash
# Load TFI preset to program 0
mdmi load-preset example.tfi --program 0

# Load DMP preset to program 5
mdmi load-preset example.dmp --program 5

# Load specific WOPN instrument to program 10
mdmi load-preset soundbank.wopn --program 10 --bank 0 --instrument 5 --bank-type melody
```

### Dump presets

```bash
# Dump preset from program 5 to DMP file
mdmi dump-preset --program 5 --format dmp --filename my_preset.dmp

# Dump preset with auto-generated filename (preset_5.dmp)
mdmi dump-preset --program 5

# Dump preset to TFI file
mdmi dump-preset --program 10 --format tfi --filename my_preset.tfi
```

### Dump FM channel parameters

```bash
# Dump FM channel parameters from MIDI channel 5 to DMP file
mdmi dump-channel --channel 5 --format dmp --filename channel_5.dmp

# Dump with auto-generated filename (channel_05.dmp)
mdmi dump-channel --channel 5

# Dump to TFI file
mdmi dump-channel --channel 3 --format tfi --filename channel_3.tfi
```

### WOPN file management

```bash
# List contents of a WOPN file (first 10 instruments per bank)
mdmi list-wopn soundbank.wopn

# List all instruments in WOPN file
mdmi list-wopn soundbank.wopn --full

# Load percussion instrument from WOPN
mdmi load-preset soundbank.wopn --program 20 --bank 0 --instrument 3 --bank-type percussion
```

### Clear presets

```bash
# Clear preset at program 5
mdmi clear-preset --program 5

# Clear all presets (with confirmation)
mdmi clear-all-presets

# Clear all presets (skip confirmation)
mdmi clear-all-presets --confirm
```

### Test connectivity

```bash
# Test MDMI connectivity with ping/pong
mdmi ping

# Test with custom timeout
mdmi ping --timeout 10.0
```

### Performance testing

```bash
# Run continuous ping/pong latency test (stop with Ctrl+C)
mdmi perf-test

# Run test for specific duration with custom interval
mdmi perf-test --duration 30 --interval 0.05

# Customize histogram filename
mdmi perf-test --hist-filename my_latency_test.png

# Test with custom timeout for individual pings
mdmi perf-test --timeout 1.0 --duration 60
```

### List available MIDI ports

```bash
# List all available MIDI input and output ports
mdmi list-ports
```

## Common Options

All commands support these common options:

### MIDI Port Selection

```bash
# Use specific MIDI ports instead of environment variables
mdmi load-preset example.tfi --program 0 --midi-out "IAC Driver Bus 1"

# Commands with bidirectional communication support input ports
mdmi ping --midi-out "IAC Driver Bus 1" --midi-in "IAC Driver Bus 2"
mdmi dump-preset --program 5 --midi-out "Port 1" --midi-in "Port 2"
```

### Dry Run

```bash
# Test with fake interface (no real MIDI hardware required)
mdmi load-preset example.tfi --program 0 --dry-run
mdmi perf-test --dry-run --duration 5
mdmi ping --dry-run
```

### Timeout

```bash
# Custom timeouts for bidirectional commands
mdmi ping --timeout 10.0
mdmi dump-preset --program 3 --timeout 5.0
```

## Configuration

### Environment Variables

- **`MDMI_MIDI_OUT`**: Default MIDI output port name
- **`MDMI_MIDI_IN`**: Default MIDI input port name
- **`MDMI_MIDI_PORT`**: Legacy fallback for MIDI output port

### Command-line Options

- `--midi-out TEXT`: MIDI output port name (overrides environment variables)
- `--midi-in TEXT`: MIDI input port name for bidirectional commands (overrides `MDMI_MIDI_IN`)
- `--dry-run`: Use fake MIDI interface for testing
- `--timeout FLOAT`: Timeout for bidirectional commands (default varies by command)

## Development

### Build

```bash
# Install cli (from source)
make install

# Run tests
make test
```
