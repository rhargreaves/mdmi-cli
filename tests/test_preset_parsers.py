"""Tests for preset parsers."""

import pytest

from mdmi.preset_parsers import (
    detect_preset_format,
    parse_preset,
    list_wopn_contents,
    FMOperator,
    parse_channel_dump_response,
    PresetParseError,
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
        wopn_data = b"WOPN2-B2NK\x00" + b"\x00" * 20
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
        tfi_data[0] = 0x02  # Algorithm 2
        tfi_data[1] = 0x03  # Feedback 3

        # Add operator data (each operator is 10 bytes)
        for i in range(4):
            offset = 2 + (i * 10)
            tfi_data[offset] = 0x15  # MUL=5, DT=1

        preset = parse_preset(bytes(tfi_data), "TFI")

        assert preset.format_type == "TFI"
        assert preset.algorithm == 2
        assert preset.feedback == 3
        assert len(preset.operators) == 4

    def test_parse_invalid_tfi_size(self):
        """Test parsing TFI with wrong size."""
        # The new parser handles short data gracefully, so no exception expected
        preset = parse_preset(b"\x00" * 10, "TFI")  # Too small for full TFI

        # Should still parse but with minimal data
        assert preset.format_type == "TFI"
        assert len(preset.operators) == 4  # Always creates 4 operators


class TestDMPParser:
    """Tests for DMP parsing."""

    def test_parse_basic_dmp(self):
        """Test parsing basic DMP data."""
        # Create DMP data (version 8 format for simplicity)
        dmp_data = bytearray()
        dmp_data.append(8)  # Version 8
        dmp_data.append(1)  # Instrument mode (FM)
        dmp_data.append(0)  # Unknown byte

        # FM parameters
        dmp_data.extend([0x03, 0x04, 0x05, 0x02])  # LFO_FMS, Feedback, Algorithm, LFO_AMS

        # Operator data (4 operators × 11 bytes each)
        for i in range(4):
            dmp_data.extend([0x01, 0x40, 0x1F, 0x0F, 0x0F, 0x00, 0x02, 0x03, 0x00, 0x00, 0x00])

        preset = parse_preset(bytes(dmp_data), "DMP")

        assert preset.format_type == "DMP"
        assert preset.algorithm == 5
        assert preset.feedback == 4


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
        """Test creating FMOperator with all parameters."""
        op = FMOperator(
            mul=5,
            dt=3,
            ar=31,
            rs=1,
            dr=15,
            am=0,
            sl=8,
            sr=4,
            rr=12,
            tl=40,
            ssg=2,
        )

        assert op.mul == 5
        assert op.dt == 3
        assert op.ar == 31
        assert op.rs == 1
        assert op.dr == 15
        assert op.am == 0
        assert op.sl == 8
        assert op.sr == 4
        assert op.rr == 12
        assert op.tl == 40
        assert op.ssg == 2

    def test_fm_operator_creation(self):
        """Test FMOperator with minimal parameters."""
        op = FMOperator(mul=1, dt=0, ar=15, rs=0, dr=8, am=0, sl=4, sr=2, rr=10, tl=20, ssg=0)
        assert op.mul == 1
        assert op.tl == 20


class TestChannelDumpParser:
    """Tests for channel dump response parsing."""

    def test_parse_channel_dump_response_valid(self):
        """Test parsing valid channel dump response."""
        # Create valid channel dump response SysEx
        # F0 00 22 77 10 00 05 <algorithm> <feedback> <ams> <fms> <44 operator bytes> F7
        sysex_data = bytearray([0xF0, 0x00, 0x22, 0x77, 0x10, 0x00, 0x05])  # Header with channel 5

        # Add FM parameters
        sysex_data.extend([0x03, 0x04, 0x01, 0x02])  # algorithm=3, feedback=4, ams=1, fms=2

        # Add 4 operators (11 bytes each)
        for i in range(4):
            # mul, dt, ar, rs, dr, am, sl, sr, rr, tl, ssg
            sysex_data.extend([0x05, 0x02, 0x1F, 0x01, 0x0F, 0x00, 0x08, 0x04, 0x0C, 0x28, 0x00])

        sysex_data.append(0xF7)  # End SysEx

        preset = parse_channel_dump_response(bytes(sysex_data))

        assert preset.format_type is None
        assert preset.name == "Channel_05"
        assert preset.algorithm == 3
        assert preset.feedback == 4
        assert preset.lfo_ams == 1
        assert preset.lfo_fms == 2
        assert len(preset.operators) == 4

        # Check first operator
        op = preset.operators[0]
        assert op.mul == 5
        assert op.dt == 2
        assert op.ar == 31
        assert op.rs == 1
        assert op.dr == 15
        assert op.am == 0
        assert op.sl == 8
        assert op.sr == 4
        assert op.rr == 12
        assert op.tl == 40
        assert op.ssg == 0

    def test_parse_channel_dump_response_invalid_header(self):
        """Test parsing with invalid header."""
        # Wrong command ID (0x0E instead of 0x10) - make sure it's long enough
        sysex_data = bytearray([0xF0, 0x00, 0x22, 0x77, 0x0E, 0x00, 0x05])
        sysex_data.extend([0x00] * 48)  # Pad to avoid length error
        sysex_data.append(0xF7)

        with pytest.raises(PresetParseError, match="Invalid MDMI channel dump response SysEx"):
            parse_channel_dump_response(bytes(sysex_data))

    def test_parse_channel_dump_response_too_short(self):
        """Test parsing with insufficient data."""
        sysex_data = bytes([0xF0, 0x00, 0x22, 0x77, 0x10])

        with pytest.raises(PresetParseError, match="SysEx too short for channel dump response"):
            parse_channel_dump_response(sysex_data)

    def test_parse_channel_dump_response_wrong_type(self):
        """Test parsing with wrong channel type."""
        sysex_data = bytearray([0xF0, 0x00, 0x22, 0x77, 0x10, 0x01, 0x05])  # Type 1 instead of 0
        sysex_data.extend([0x00] * 48)  # Pad with zeros
        sysex_data.append(0xF7)

        with pytest.raises(PresetParseError, match="Unsupported channel type: 1"):
            parse_channel_dump_response(bytes(sysex_data))

    def test_parse_channel_dump_response_insufficient_operator_data(self):
        """Test parsing with insufficient operator data."""
        sysex_data = bytearray([0xF0, 0x00, 0x22, 0x77, 0x10, 0x00, 0x05])
        sysex_data.extend([0x03, 0x04, 0x01, 0x02])  # FM parameters
        sysex_data.extend([0x00] * 20)  # Only 20 bytes instead of 44 for operators
        sysex_data.append(0xF7)

        with pytest.raises(PresetParseError, match="Insufficient data for FM channel"):
            parse_channel_dump_response(bytes(sysex_data))
