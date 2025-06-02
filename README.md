# MDMI CLI

A command-line interface for controlling the Mega Drive MIDI Interface (MDMI) via SysEx. This tool allows you to load FM synthesis presets in WOPN, DMP, and TFI formats to your Mega Drive MIDI Interface.

## Features

- **Multiple Format Support**: Load WOPN, DMP, and TFI preset files
- **SysEx Generation**: Automatically converts presets to proper SysEx format for MDMI
- **Real & Fake MIDI**: Supports both real MIDI interfaces and fake interface for testing
- **Channel Targeting**: Load presets to specific FM channels (0-5)
- **Test-Driven Design**: Comprehensive test suite with E2E testing using fake MIDI interface
- **Modular Architecture**: Easily extensible for additional SysEx commands and features

## Installation

### Requirements

- Python 3.12+
- MIDI interface (for real hardware) or use fake interface for testing

### Install from source

```bash
git clone <repository-url>
cd mdmi-cli
pip install -e ".[dev]"
```

## Usage

### Basic Commands

```bash
# Show help
mdmi --help

# List available MIDI ports
mdmi load-preset --list-ports

# Load a TFI preset to channel 0 using fake interface (for testing)
mdmi load-preset my_preset.tfi --channel 0 --fake

# Load a DMP preset to channel 2 using real MIDI interface
mdmi load-preset my_preset.dmp --channel 2 --port "Your MIDI Interface"

# Load a WOPN preset to channel 1 (auto-detect MIDI port if only one available)
mdmi load-preset my_preset.wopn --channel 1
```

### Supported Formats

#### TFI (Twistring FM Instrument)
- 42-byte FM parameter files
- Contains complete operator settings
- Commonly used with YM2612 trackers

#### DMP (DefleMask Preset)
- DefleMask preset format
- Supports versions 8, 9, and 11
- Contains instrument name and FM parameters

#### WOPN (WOPN2-BANK)
- libOPNMIDI bank format
- Supports versions 1 and 2
- Contains multiple instruments in banks

### Examples

```bash
# Development workflow with fake interface
mdmi load-preset examples/bass.tfi --channel 0 --fake
mdmi load-preset examples/lead.dmp --channel 1 --fake

# Production use with real hardware
mdmi load-preset sounds/piano.wopn --channel 0 --port "MDMI Interface"
```

## Development

### Setup Development Environment

```bash
make install-dev  # Install with development dependencies
```

### Running Tests

```bash
make test         # Run all tests
make test-verbose # Run tests with verbose output
make lint         # Run linting checks
```

### Project Structure

```
mdmi-cli/
├── mdmi/                    # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI implementation
│   ├── preset_parsers.py   # WOPN/DMP/TFI parsers
│   ├── sysex_generator.py  # SysEx message generation
│   └── midi_interface.py   # MIDI interface abstraction
├── tests/                   # Test suite
│   ├── test_preset_parsers.py
│   ├── test_sysex_generator.py
│   ├── test_midi_interface.py
│   ├── test_cli.py
│   └── test_e2e.py         # End-to-end integration tests
├── requirements.txt
├── setup.py
├── Makefile
└── README.md
```

### Architecture

The MDMI CLI follows a modular architecture designed for extensibility:

1. **Preset Parsers** (`preset_parsers.py`)
   - Format-specific parsers for WOPN, DMP, TFI
   - Converts binary data to structured preset objects
   - Extensible for additional formats

2. **SysEx Generator** (`sysex_generator.py`)
   - Converts preset objects to MDMI SysEx format
   - Handles checksums and protocol specifics
   - Ready for additional SysEx commands

3. **MIDI Interface** (`midi_interface.py`)
   - Abstraction layer for real and fake MIDI
   - FakeMIDIInterface enables testing without hardware
   - Real interface uses `mido` library

4. **CLI** (`cli.py`)
   - Click-based command line interface
   - Handles file I/O, format detection, error handling
   - Modular command structure for future expansion

### Testing Strategy

The project uses Test-Driven Development (TDD) with comprehensive testing:

- **Unit Tests**: Each module has dedicated unit tests
- **Integration Tests**: Test interaction between modules
- **E2E Tests**: Full workflow tests using fake MIDI interface
- **Mock Testing**: Real MIDI interfaces are mocked for reliable testing

### Future Extensions

The modular design supports easy addition of:

- Additional preset formats
- More SysEx commands (CC support, parameter tweaking)
- Real-time parameter control
- Preset conversion between formats
- Bulk operations and scripting

## SysEx Protocol

The tool generates SysEx messages compatible with the Mega Drive MIDI Interface:

```
F0 43 76 10 <channel> <preset_data> <checksum> F7
```

Where:
- `F0`: SysEx start
- `43`: Yamaha manufacturer ID (YM2612 compatibility)
- `76`: MDMI device ID
- `10`: Preset load command
- `<channel>`: Target FM channel (0-5)
- `<preset_data>`: Encoded preset parameters
- `<checksum>`: XOR checksum
- `F7`: SysEx end

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Implement the feature
5. Ensure all tests pass: `make test`
6. Check code style: `make lint`
7. Submit a pull request

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## References

- [Mega Drive MIDI Interface](https://github.com/rhargreaves/mega-drive-midi-interface)
- [DefleMask Preset Viewer](https://github.com/rhargreaves/deflemask-preset-viewer) - Format reference
- [libOPNMIDI WOPN Format](https://github.com/Wohlstand/libOPNMIDI)
- [YM2612 Documentation](https://docs.rs/ym2612/latest/ym2612/)
