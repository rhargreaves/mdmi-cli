# Mega Drive MIDI Interface CLI

[![PyPI](https://img.shields.io/pypi/v/mdmi-cli)](https://pypi.org/project/mdmi-cli/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mdmi-cli)](https://pypi.org/project/mdmi-cli/)
[![PyPI - License](https://img.shields.io/pypi/l/mdmi-cli)](https://github.com/rhargreaves/mdmi-cli/blob/main/LICENSE)
[![Build](https://github.com/rhargreaves/mdmi-cli/actions/workflows/build.yml/badge.svg)](https://github.com/rhargreaves/mdmi-cli/actions/workflows/build.yml)

Python CLI for controlling the Mega Drive MIDI Interface (MDMI). Supports loading presets in WOPN, DMP, and TFI formats with instrument selection for WOPN files.

## Features

- **Multi-format preset support**: Load presets in WOPN, DMP, and TFI formats to MDMI user presets (programs 0-127)
- **Advanced WOPN support**: Choose specific bank, instrument, and bank type (melody/percussion) from WOPN files
- **Intelligent format detection**: Automatic detection of preset formats based on file headers and structure
- **Flexible MIDI port configuration**: Separate input/output port support with environment variables
- **Preset management**: Clear individual user presets or all presets at once
- **WOPN browsing**: List WOPN file contents to explore available banks and instruments
- **Connectivity testing**: Ping/pong functionality to test MDMI connectivity and measure round-trip latency
- **Hardware MIDI support**: Works with MIDI hardware for real-time preset loading and bidirectional communication
- **Testing support**: Fake MIDI interface mode for development and testing
- **Comprehensive testing**: Full test coverage including real-world data validation

## Installation (from PyPI)

```bash
pip install mdmi-cli
```

## Installation (from source)

```bash
make install
```

## Build

### Add Requirements
```bash
pip install -r requirements.txt
```

## Usage

### Environment Variable Setup (Optional)

Set MIDI port environment variables to avoid specifying ports in every command:

```bash
# Set output port (for sending to MDMI)
export MDMI_MIDI_OUT="IAC Driver Bus 1"

# Set input port (for receiving from MDMI)
export MDMI_MIDI_IN="IAC Driver Bus 2"

# Legacy support: MDMI_MIDI_PORT (used as fallback for output)
export MDMI_MIDI_PORT="IAC Driver Bus 1"

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export MDMI_MIDI_OUT="IAC Driver Bus 1"' >> ~/.bashrc
echo 'export MDMI_MIDI_IN="IAC Driver Bus 2"' >> ~/.bashrc
```

With environment variables set, you can omit `--midi-out` and `--midi-in` from commands:

```bash
# These commands will automatically use environment variables
mdmi load-preset example.tfi --program 0
mdmi clear-preset --program 5
mdmi ping
```

### Load a preset

```bash
# Load TFI preset to program 0 (uses MDMI_MIDI_OUT if set)
mdmi load-preset example.tfi --program 0

# Load DMP preset to program 5 via specific MIDI port
mdmi load-preset example.dmp --program 5 --midi-out "IAC Driver Bus 1"

# Load specific WOPN instrument to program 10
mdmi load-preset soundbank.wopn --program 10 --bank 0 --instrument 5 --bank-type melody

# Test with fake interface (for development)
mdmi load-preset example.tfi --program 0 --fake
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

- **`MDMI_MIDI_OUT`**: Default MIDI output port name (takes precedence)
- **`MDMI_MIDI_IN`**: Default MIDI input port name
- **`MDMI_MIDI_PORT`**: Legacy fallback for MIDI output port
  - Used automatically when port options are not specified
  - Can be overridden by command-line options for individual commands
  - Improves workflow efficiency when consistently using the same MIDI device

### Command-line Options

Most commands support:
- `--midi-out TEXT`: MIDI output port name (overrides environment variables)

Commands with bidirectional communication (ping) also support:
- `--midi-in TEXT`: MIDI input port name (overrides `MDMI_MIDI_IN`)

## Supported Formats

### TFI (42 bytes)
- Direct YM2612 FM parameter files
- Algorithm and feedback as separate bytes
- 4 operators with 10 bytes each
- Commonly used with Deflemask and other trackers

### DMP (DefleMask preset format)
- **Version 8**: Basic FM parameters with operator data
- **Version 9**: Enhanced format with additional features
- **Version 11**: Full format with system type specification
- Automatic version detection and proper parsing
- Support for both `.DMP` signature and direct version byte formats

### WOPN (libOPNMIDI bank format)
- Multi-bank instrument collections with proper `WOPN2-B2NK` header support
- Separate melody and percussion banks
- Advanced instrument selection by bank index and instrument index
- Bank type selection (melody/percussion)
- Comprehensive bank browsing with `list-wopn` command
- Support for multiple banks per type with `--full` option for complete listings

## Development

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_cli.py -v

# Run with coverage
pytest --cov=mdmi tests/
```

## Dependencies

- **click**: Command-line interface framework for robust CLI development
- **mido**: MIDI library for hardware communication and SysEx handling
- **bitstruct**: Binary data parsing library for efficient preset format parsing

### Development Dependencies
- **pytest**: Testing framework for comprehensive test coverage
- **pytest-mock**: Mocking library for isolated testing
- **ruff**: Fast Python linter and formatter

## License

This project is open source. Please check the license file for details.
