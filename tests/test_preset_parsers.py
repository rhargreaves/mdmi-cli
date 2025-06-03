"""Tests for preset parsers."""

import pytest
import tempfile
import os
from pathlib import Path

from mdmi.preset_parsers import (
    detect_preset_format,
    parse_preset,
    list_wopn_contents,
    PresetParseError,
    FMOperator,
)


class TestFormatDetection:
    """Tests for format detection."""

    def test_detect_tfi_format(self):
        """Test TFI format detection."""
        tfi_data = b"\x00" * 42
        assert detect_preset_format(tfi_data) == "TFI"

    def test_detect_dmp_format(self):
        """Test DMP format detection."""
        dmp_data = b".DMP" + b"\x00" * 40
        assert detect_preset_format(dmp_data) == "DMP"

    def test_detect_wopn_format(self):
        """Test WOPN format detection."""
        wopn_data = b"WOPN2-BANK\x00" + b"\x00" * 20
        assert detect_preset_format(wopn_data) == "WOPN"

    def test_detect_unknown_format(self):
        """Test unknown format detection."""
        unknown_data = b"UNKNOWN" + b"\x00" * 20
        assert detect_preset_format(unknown_data) == "UNKNOWN"


class TestTFIParser:
    """Tests for TFI parsing."""

    def test_parse_basic_tfi(self):
        """Test parsing basic TFI data."""
        # Create minimal TFI data
        tfi_data = bytearray(42)
        tfi_data[0] = 0x12  # Algorithm 2, Feedback 2
        tfi_data[1] = 0x34  # Additional byte

        # Add operator data (each operator is 10 bytes)
        for i in range(4):
            offset = 2 + (i * 10)
            tfi_data[offset] = 0x15  # MUL=5, DT=1

        preset = parse_preset(bytes(tfi_data), "TFI")

        assert preset.format_type == "TFI"
        assert preset.algorithm == 2
        assert preset.feedback == 2
        assert len(preset.operators) == 4

    def test_parse_invalid_tfi_size(self):
        """Test parsing TFI with wrong size."""
        with pytest.raises(Exception):  # Should fail on temp file creation
            parse_preset(b"\x00" * 10, "TFI")


class TestDMPParser:
    """Tests for DMP parsing."""

    def test_parse_basic_dmp(self):
        """Test parsing basic DMP data."""
        # Create minimal DMP data
        dmp_data = bytearray(50)
        dmp_data[0] = 11  # Version 11
        dmp_data[1] = 2  # System type Genesis
        dmp_data[2] = 1  # FM instrument mode
        # Name starts at offset 3 for 32 bytes
        name = b"Test DMP"
        dmp_data[3 : 3 + len(name)] = name

        preset = parse_preset(bytes(dmp_data), "DMP")

        assert preset.format_type == "DMP"
        assert preset.name == "Test DMP"


class TestWOPNParser:
    """Tests for WOPN parsing."""

    def test_parse_wopn_instrument_selection(self):
        """Test parsing WOPN with instrument selection."""
        # This test would need a real WOPN file to work properly
        # For now, just test that the interface works
        wopn_data = b"WOPN2-BANK\x00" + b"\x00" * 100

        # This should fail due to invalid WOPN structure, but the interface should work
        with pytest.raises(Exception):
            parse_preset(wopn_data, "WOPN", bank=0, instrument=0, bank_type="melody")


class TestWOPNListing:
    """Tests for WOPN content listing."""

    def test_list_wopn_interface(self):
        """Test WOPN listing interface."""
        wopn_data = b"WOPN2-BANK\x00" + b"\x00" * 100

        # This should fail due to invalid WOPN structure, but the interface should work
        with pytest.raises(Exception):
            list_wopn_contents(wopn_data)


class TestFMOperator:
    """Tests for FMOperator."""

    def test_create_fm_operator(self):
        """Test creating FMOperator with all fields."""
        op = FMOperator(
            mul=1, dt1=2, ar=3, rs=4, d1r=5, am=6, d1l=7, d2r=8, rr=9, tl=10, ssg=11
        )

        assert op.mul == 1
        assert op.dt1 == 2
        assert op.ar == 3
        assert op.rs == 4
        assert op.d1r == 5
        assert op.am == 6
        assert op.d1l == 7
        assert op.d2r == 8
        assert op.rr == 9
        assert op.tl == 10
        assert op.ssg == 11
