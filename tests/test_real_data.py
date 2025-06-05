"""Tests using real test data files."""

import pytest
from pathlib import Path

from mdmi.preset_parsers import detect_preset_format, parse_preset, list_wopn_contents
from mdmi.sysex_generator import SysExGenerator
from mdmi.fake_midi_interface import FakeMidiInterface


class TestRealData:
    """Tests using real test data files."""

    def test_tfi_real_data(self):
        """Test with real TFI data."""
        tfi_path = Path("tests/data/sample.tfi")
        data = tfi_path.read_bytes()

        # Test format detection
        assert detect_preset_format(data) == "TFI"

        # Test parsing
        preset = parse_preset(data, "TFI")
        assert preset.format_type == "TFI"
        assert preset.name == "tfi_data"  # Name comes from BytesIO approach
        assert len(preset.operators) == 4

        # Test SysEx generation
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=5)

        # Verify SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # FM type
        assert sysex_data[6] == 5  # Program number
        assert sysex_data[-1] == 0xF7  # SysEx end

        # Test MIDI interface
        interface = FakeMidiInterface()
        interface.send_sysex(sysex_data)
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex == sysex_data

    def test_dmp_real_data_v8(self):
        """Test with real DMP version 8 data."""
        dmp_path = Path("tests/data/sample.dmp")
        data = dmp_path.read_bytes()

        # Test format detection
        assert detect_preset_format(data) == "DMP"

        # Test parsing
        preset = parse_preset(data, "DMP")
        assert preset.format_type == "DMP"
        assert preset.name == "dmp_data"  # Name comes from BytesIO approach

        # Test SysEx generation
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=10)

        # Verify SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # FM type
        assert sysex_data[6] == 10  # Program number
        assert sysex_data[-1] == 0xF7  # SysEx end

    def test_dmp_real_data_v9(self):
        """Test with real DMP version 9 data."""
        dmp_path = Path("tests/data/sample_v9.dmp")
        data = dmp_path.read_bytes()

        # Test format detection
        assert detect_preset_format(data) == "DMP"

        # Test parsing
        preset = parse_preset(data, "DMP")
        assert preset.format_type == "DMP"
        assert preset.name == "dmp_data"  # Name comes from BytesIO approach

    def test_dmp_real_data_new(self):
        """Test with real new DMP data."""
        dmp_path = Path("tests/data/sample_new.dmp")
        data = dmp_path.read_bytes()

        # Test format detection
        assert detect_preset_format(data) == "DMP"

        # Test parsing
        preset = parse_preset(data, "DMP")
        assert preset.format_type == "DMP"
        assert preset.name == "dmp_data"  # Name comes from BytesIO approach

    def test_wopn_real_data(self):
        """Test with real WOPN data."""
        wopn_path = Path("tests/data/sample.wopn")
        data = wopn_path.read_bytes()

        # Test format detection
        assert detect_preset_format(data) == "WOPN"

        # Test listing contents
        contents = list_wopn_contents(data)
        assert "melody_banks" in contents
        assert "percussion_banks" in contents
        assert len(contents["melody_banks"]) == 2
        assert len(contents["percussion_banks"]) == 5

        # Test parsing specific instruments
        preset = parse_preset(data, "WOPN", bank=0, instrument=0, bank_type="melody")
        assert preset.format_type == "WOPN"
        assert preset.name == "* GrandPiano"
        assert len(preset.operators) == 4

        # Test percussion bank
        preset = parse_preset(data, "WOPN", bank=0, instrument=35, bank_type="percussion")
        assert preset.format_type == "WOPN"
        assert preset.name == "* BassDrum "

        # Test SysEx generation for WOPN
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=25)

        # Verify SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # FM type
        assert sysex_data[6] == 25  # Program number
        assert sysex_data[-1] == 0xF7  # SysEx end

    def test_wopn_different_banks(self):
        """Test WOPN with different banks and instruments."""
        wopn_path = Path("tests/data/sample.wopn")
        data = wopn_path.read_bytes()

        # Test different melody bank
        preset = parse_preset(data, "WOPN", bank=1, instrument=65, bank_type="melody")
        assert preset.format_type == "WOPN"
        assert preset.name == "DoorSqek"

        # Test different percussion bank
        preset = parse_preset(data, "WOPN", bank=1, instrument=3, bank_type="percussion")
        assert preset.format_type == "WOPN"
        assert preset.name == "KEK :3"

    def test_all_formats_sysex_validity(self):
        """Test that all formats generate valid SysEx messages."""
        generator = SysExGenerator()

        # Test TFI
        tfi_data = Path("tests/data/sample.tfi").read_bytes()
        preset = parse_preset(tfi_data, "TFI")
        sysex = generator.generate_preset_load(preset, program=1)
        assert len(sysex) > 50  # Should have substantial data
        assert sysex[0] == 0xF0 and sysex[-1] == 0xF7  # Valid SysEx

        # Test DMP
        dmp_data = Path("tests/data/sample.dmp").read_bytes()
        preset = parse_preset(dmp_data, "DMP")
        sysex = generator.generate_preset_load(preset, program=2)
        assert len(sysex) > 50
        assert sysex[0] == 0xF0 and sysex[-1] == 0xF7

        # Test WOPN
        wopn_data = Path("tests/data/sample.wopn").read_bytes()
        preset = parse_preset(wopn_data, "WOPN", bank=0, instrument=0, bank_type="melody")
        sysex = generator.generate_preset_load(preset, program=3)
        assert len(sysex) > 50
        assert sysex[0] == 0xF0 and sysex[-1] == 0xF7

    def test_error_handling_with_real_data(self):
        """Test error handling with real data."""
        wopn_data = Path("tests/data/sample.wopn").read_bytes()

        # Test invalid bank index
        with pytest.raises(Exception):
            parse_preset(wopn_data, "WOPN", bank=99, instrument=0, bank_type="melody")

        # Test invalid instrument index
        with pytest.raises(Exception):
            parse_preset(wopn_data, "WOPN", bank=0, instrument=999, bank_type="melody")
