"""Tests for preset parsers."""

import pytest

from mdmi.preset_parsers import WOPNParser, DMPParser, TFIParser
from mdmi.preset_parsers import PresetParseError


class TestWOPNParser:
    """Tests for WOPN preset parser."""

    def test_parse_valid_wopn_file(self):
        """Test parsing a valid WOPN file."""
        parser = WOPNParser()

        # Create minimal valid WOPN data with correct structure
        wopn_data = (
            b"WOPN2-BANK\x00"  # Header (12 bytes)
            b"\x02"  # Version 2 (byte 12)
            b"\x00\x00"  # Flags (bytes 13-14)
            b"\x02"  # Melody banks count (byte 15)
            b"\x01"  # Percussion banks count (byte 16)
            + b"\x00" * 32  # Bank names (32 bytes each)
            + b"\x00" * 32
            + b"\x00" * 32
            # Melody bank 0 instruments (128 instruments * 32 bytes)
            + b"\x00" * (128 * 32)
            + b"\x00" * (128 * 32)  # Melody bank 1 instruments
            + b"\x00" * (128 * 32)  # Percussion bank 0 instruments
        )

        preset = parser.parse(wopn_data)

        assert preset.format_type == "WOPN"
        assert preset.version == 2
        assert preset.melody_banks == 2
        assert preset.percussion_banks == 1

    def test_parse_invalid_header(self):
        """Test parsing WOPN with invalid header."""
        parser = WOPNParser()

        # Create data with valid length but invalid header
        invalid_data = b"INVALID\x00\x00\x00\x00\x02\x00\x00\x02\x01"

        with pytest.raises(PresetParseError, match="Invalid WOPN header"):
            parser.parse(invalid_data)

    def test_parse_empty_data(self):
        """Test parsing empty data."""
        parser = WOPNParser()

        with pytest.raises(PresetParseError, match="File too small"):
            parser.parse(b"")


class TestDMPParser:
    """Tests for DMP preset parser."""

    def test_parse_valid_dmp_file(self):
        """Test parsing a valid DMP file."""
        parser = DMPParser()

        # Create minimal valid DMP data (version 11)
        preset_name = "Test Preset"
        name_padded = (preset_name + "\x00" * 32)[:32].encode()

        dmp_data = (
            b".DMP"  # File signature
            b"\x0b"  # Version 11
            b"\x01"  # System (YM2612)
            + name_padded  # Name (32 bytes)
            + b"\x00" * 11  # 11 bytes of FM parameters
        )

        preset = parser.parse(dmp_data)

        assert preset.format_type == "DMP"
        assert preset.version == 11
        assert preset.system == 1  # YM2612
        assert preset.name == "Test Preset"

    def test_parse_invalid_signature(self):
        """Test parsing DMP with invalid signature."""
        parser = DMPParser()

        with pytest.raises(PresetParseError, match="Invalid DMP signature"):
            parser.parse(b"INVALID")


class TestTFIParser:
    """Tests for TFI preset parser."""

    def test_parse_valid_tfi_file(self):
        """Test parsing a valid TFI file."""
        parser = TFIParser()

        # Create minimal valid TFI data (42 bytes total)
        tfi_data = b"\x00" * 42  # 42 bytes of FM parameters

        preset = parser.parse(tfi_data)

        assert preset.format_type == "TFI"
        assert len(preset.fm_parameters) == 42

    def test_parse_invalid_size(self):
        """Test parsing TFI with invalid size."""
        parser = TFIParser()

        with pytest.raises(PresetParseError, match="Invalid TFI size"):
            parser.parse(b"\x00" * 10)  # Too small
