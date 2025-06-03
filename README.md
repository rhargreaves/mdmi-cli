# Mega Drive MIDI Interface CLI

Python CLI for controlling the Mega Drive MIDI Interface (MDMI). Supports loading presets in WOPN, DMP, and TFI formats with instrument selection for WOPN files.

## Features

- **Multi-format preset support**: Load presets in WOPN, DMP, and TFI formats to MDMI user presets (programs 0-127)
- **Advanced WOPN support**: Choose specific bank, instrument, and bank type (melody/percussion) from WOPN files
- **Intelligent format detection**: Automatic detection of preset formats based on file headers and structure
- **Environment variable support**: Set `MDMI_MIDI_PORT` once to avoid specifying `--port` repeatedly
- **Preset management**: Clear individual user presets or all presets at once
- **WOPN browsing**: List WOPN file contents to explore available banks and instruments
- **Hardware MIDI support**: Works with MIDI hardware for real-time preset loading
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

Set the `MDMI_MIDI_PORT` environment variable to avoid specifying `--port` in every command:

```bash
# Set for current session
export MDMI_MIDI_PORT="USB MIDI Interface"

# Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export MDMI_MIDI_PORT="USB MIDI Interface"' >> ~/.bashrc
```

With the environment variable set, you can omit `--port` from all commands:

```bash
# These commands will automatically use MDMI_MIDI_PORT
mdmi load-preset example.tfi --program 0
mdmi clear-preset --program 5
mdmi clear-all-presets --confirm
```

### Load a preset

```bash
# Load TFI preset to program 0 (uses MDMI_MIDI_PORT if set)
mdmi load-preset example.tfi --program 0

# Load DMP preset to program 5 via specific MIDI port
mdmi load-preset example.dmp --program 5 --port "USB MIDI Interface"

# Load specific WOPN instrument to program 10
mdmi load-preset soundbank.wopn --program 10 --bank 0 --instrument 5 --bank-type melody

# List available MIDI ports
mdmi list-ports
```

### WOPN file management

```bash
# List contents of a WOPN file
mdmi list-wopn soundbank.wopn

# Load percussion instrument from WOPN
mdmi load-preset soundbank.wopn --program 20 --bank 0 --instrument 3 --bank-type percussion

# Load from different melody bank
mdmi load-preset soundbank.wopn --program 15 --bank 1 --instrument 65 --bank-type melody
```

### Clear presets

```bash
# Clear preset at program 5 (uses MDMI_MIDI_PORT if set)
mdmi clear-preset --program 5

# Clear all presets (with confirmation)
mdmi clear-all-presets

# Clear all presets (skip confirmation) with specific port
mdmi clear-all-presets --confirm --port "My MIDI Device"
```

## Configuration

### Environment Variables

- **`MDMI_MIDI_PORT`**: Default MIDI output port name
  - Used automatically when `--port` is not specified
  - Can be overridden by the `--port` option for individual commands
  - Improves workflow efficiency when consistently using the same MIDI device

### Command-line Options

All commands support:
- `--port TEXT`: MIDI output port name (overrides `MDMI_MIDI_PORT`)

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
- Support for multiple banks per type

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
