# Mega Drive MIDI Interface CLI

Python CLI for controlling the Mega Drive MIDI Interface (MDMI). Supports loading presets in WOPN, DMP, and TFI formats with instrument selection for WOPN files.

## Features

- **Multi-format preset support**: Load presets in WOPN, DMP, and TFI formats to MDMI user presets (programs 0-127)
- **Advanced WOPN support**: Choose specific bank, instrument, and bank type (melody/percussion) from WOPN files
- **Intelligent format detection**: Automatic detection of preset formats based on file headers and structure
- **Preset management**: Clear individual user presets or all presets at once
- **WOPN browsing**: List WOPN file contents to explore available banks and instruments
- **Flexible MIDI support**: Works with both real MIDI hardware and fake interface for testing
- **Comprehensive testing**: Full test coverage including real-world data validation

## Installation (from PyPi)

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

### Load a preset

```bash
# Load TFI preset to program 0
mdmi load-preset example.tfi --program 0

# Load DMP preset to program 5 via real MIDI port
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
# Clear preset at program 5
mdmi clear-preset --program 5

# Clear all presets (with confirmation)
mdmi clear-all-presets

# Clear all presets (skip confirmation)
mdmi clear-all-presets --confirm
```

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
```
## Dependencies

- **click**: Command-line interface framework for robust CLI development
- **mido**: MIDI library for hardware communication and SysEx handling
- **bitstruct**: Binary data parsing library for efficient preset format parsing
- **pytest**: Testing framework for comprehensive test coverage

## License

This project is open source. Please check the license file for details.
