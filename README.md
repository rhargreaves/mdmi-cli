# MDMI CLI

Python CLI for controlling the Mega Drive MIDI Interface (MDMI) via SysEx commands. Supports loading presets in WOPN, DMP, and TFI formats with sophisticated instrument selection for WOPN files.

## Features

- **Multi-format preset support**: Load presets in WOPN, DMP, and TFI formats to MDMI user presets (programs 0-127)
- **Advanced WOPN support**: Choose specific bank, instrument, and bank type (melody/percussion) from WOPN files
- **Intelligent format detection**: Automatic detection of preset formats based on file headers and structure
- **Preset management**: Clear individual user presets or all presets at once
- **WOPN browsing**: List WOPN file contents to explore available banks and instruments
- **Flexible MIDI support**: Works with both real MIDI hardware and fake interface for testing
- **Comprehensive testing**: Full test coverage including real-world data validation

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
python -m mdmi.cli list-ports
```

### WOPN file management

```bash
# List contents of a WOPN file
python -m mdmi.cli list-wopn soundbank.wopn

# Load percussion instrument from WOPN
python -m mdmi.cli load-preset soundbank.wopn --program 20 --bank 0 --instrument 3 --bank-type percussion --fake

# Load from different melody bank
python -m mdmi.cli load-preset soundbank.wopn --program 15 --bank 1 --instrument 65 --bank-type melody --fake
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
- `00 22 77`: MDMI manufacturer ID
- `0A`: Load preset command
- `00`: FM instrument type
- `<program>`: Target program number (0-127)
- `<operators>`: 44 bytes of operator data (4 operators × 11 bytes each)

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

## Architecture

The CLI uses a sophisticated modular parser architecture:

- **Format Detection**: Automatic detection based on file headers, signatures, and size validation
- **Modular Parsers**: Dedicated parsers for each format in `mdmi/presets/` using bitstruct for binary parsing
- **Unified Interface**: Common `Preset` and `FMOperator` classes for consistent SysEx generation
- **Field Mapping**: Intelligent mapping between format-specific field names (e.g., `dt`→`dt1`, `dr`→`d1r`, `sl`→`d1l`)
- **Adapter Layer**: Seamless integration between file-based parsers and byte-based CLI interface
- **Error Handling**: Graceful handling of invalid formats and missing instruments

## Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test suites
python -m pytest tests/test_preset_parsers.py -v
python -m pytest tests/test_sysex_generator.py -v
python -m pytest tests/test_real_data.py -v

# Run end-to-end tests
python -m pytest tests/test_e2e_new_parsers.py -v

# Test with real sample data
python -m pytest tests/test_real_data.py::TestRealData::test_wopn_real_data -v
```

### Working with Sample Data

The project includes real sample data for testing:

```bash
# Test TFI loading
python -m mdmi.cli load-preset tests/data/sample.tfi --program 5 --fake

# Test DMP variants
python -m mdmi.cli load-preset tests/data/sample.dmp --program 10 --fake      # Version 8
python -m mdmi.cli load-preset tests/data/sample_v9.dmp --program 11 --fake   # Version 9
python -m mdmi.cli load-preset tests/data/sample_new.dmp --program 12 --fake  # Version 11

# Explore WOPN contents
python -m mdmi.cli list-wopn tests/data/sample.wopn

# Load specific WOPN instruments
python -m mdmi.cli load-preset tests/data/sample.wopn --program 20 --bank 0 --instrument 0 --bank-type melody --fake
python -m mdmi.cli load-preset tests/data/sample.wopn --program 25 --bank 0 --instrument 35 --bank-type percussion --fake
```

### Project Structure

```
mdmi/
├── __init__.py
├── cli.py                    # Main CLI interface
├── midi_interface.py         # MIDI communication layer
├── preset_parsers.py         # Parser adapter and format detection
├── sysex_generator.py        # SysEx message generation
├── preset.py                # Base preset classes
├── fm_operator.py           # FM operator data structures
├── util.py                  # Utility functions
├── ui.py                    # User interface helpers
└── presets/                 # Modular format parsers
    ├── wopn_parser.py       # WOPN format parser
    ├── dmp_parser.py        # DMP format parser
    ├── tfi_parser.py        # TFI format parser
    ├── wopn.py              # WOPN data structures
    ├── dmp.py               # DMP data structures
    ├── tfi.py               # TFI data structures
    ├── wopn_bank.py         # WOPN bank structures
    └── wopn_instrument.py   # WOPN instrument structures

tests/
├── test_cli.py              # CLI interface tests
├── test_e2e.py              # End-to-end workflow tests
├── test_e2e_new_parsers.py  # E2E tests with new parser structure
├── test_midi_interface.py   # MIDI interface tests
├── test_preset_parsers.py   # Parser functionality tests
├── test_real_data.py        # Real sample data validation tests
├── test_sysex_generator.py  # SysEx generation tests
└── data/                    # Real sample data for testing
    ├── sample.tfi           # TFI sample (42 bytes)
    ├── sample.dmp           # DMP v8 sample
    ├── sample_v9.dmp        # DMP v9 sample
    ├── sample_new.dmp       # DMP v11 sample
    └── sample.wopn          # WOPN sample (61KB with multiple banks)
```

## Dependencies

- **click**: Command-line interface framework for robust CLI development
- **mido**: MIDI library for hardware communication and SysEx handling
- **bitstruct**: Binary data parsing library for efficient preset format parsing
- **pytest**: Testing framework for comprehensive test coverage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

## License

This project is open source. Please check the license file for details.
