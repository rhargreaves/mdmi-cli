"""Tests for SysEx generator."""

import pytest

from mdmi.sysex_generator import SysExGenerator
from mdmi.preset_parsers import Preset, FMOperator


class TestSysExGenerator:
    """Tests for SysEx generator."""

    def test_generate_preset_load_sysex_tfi(self):
        """Test generating SysEx for TFI preset with correct MDMI format."""
        generator = SysExGenerator()

        # Create a TFI preset
        operators = [
            FMOperator(1, 2, 31, 1, 15, 0, 14, 0, 15, 39, 0),
            FMOperator(4, 6, 24, 1, 9, 0, 6, 9, 7, 36, 0),
            FMOperator(2, 7, 31, 3, 23, 0, 9, 15, 1, 4, 0),
            FMOperator(1, 3, 27, 2, 4, 0, 10, 4, 6, 2, 0),
        ]

        preset = Preset(
            format_type="TFI",
            algorithm=2,
            feedback=0,
            operators=operators,
        )

        sysex_data = generator.generate_preset_load(preset, program=5)

        # Check MDMI SysEx structure: F0 00 22 77 0A <type> <program> ...
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x00  # MDMI manufacturer ID part 1
        assert sysex_data[2] == 0x22  # MDMI manufacturer ID part 2
        assert sysex_data[3] == 0x77  # MDMI manufacturer ID part 3
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # Type: FM = 0
        assert sysex_data[6] == 0x05  # Program number = 5
        assert sysex_data[7] == 0x02  # Algorithm = 2
        assert sysex_data[8] == 0x00  # Feedback = 0
        assert sysex_data[-1] == 0xF7  # SysEx end
        assert len(sysex_data) > 50  # Should have substantial operator data

    def test_generate_preset_load_sysex_dmp(self):
        """Test generating SysEx for DMP preset."""
        generator = SysExGenerator()

        preset = Preset(
            format_type="DMP",
            name="Test Preset",
            algorithm=3,
            feedback=7,
            lfo_ams=1,
            lfo_fms=2,
        )

        sysex_data = generator.generate_preset_load(preset, program=10)

        # Check MDMI SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x00  # MDMI manufacturer ID
        assert sysex_data[2] == 0x22
        assert sysex_data[3] == 0x77
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # Type: FM = 0
        assert sysex_data[6] == 0x0A  # Program number = 10
        assert sysex_data[7] == 0x03  # Algorithm = 3
        assert sysex_data[8] == 0x07  # Feedback = 7
        assert sysex_data[9] == 0x01  # AMS = 1
        assert sysex_data[10] == 0x02  # FMS = 2
        assert sysex_data[-1] == 0xF7  # SysEx end

    def test_generate_preset_load_invalid_program(self):
        """Test generating SysEx with invalid program number."""
        generator = SysExGenerator()

        preset = Preset(format_type="TFI")

        with pytest.raises(ValueError, match="Program must be between 0 and 127"):
            generator.generate_preset_load(preset, program=128)

    def test_generate_preset_load_unsupported_format(self):
        """Test generating SysEx for unsupported format."""
        generator = SysExGenerator()

        preset = Preset(format_type="UNKNOWN")

        error_msg = "Unsupported preset format"
        with pytest.raises(ValueError, match=error_msg):
            generator.generate_preset_load(preset, program=0)

    def test_generate_clear_preset_sysex(self):
        """Test generating SysEx to clear a specific preset."""
        generator = SysExGenerator()

        sysex_data = generator.generate_clear_preset(program=5)

        # Check clear preset SysEx: F0 00 22 77 0B 00 <program> F7
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x00  # MDMI manufacturer ID
        assert sysex_data[2] == 0x22
        assert sysex_data[3] == 0x77
        assert sysex_data[4] == 0x0B  # Clear preset command
        assert sysex_data[5] == 0x00  # Type: FM = 0
        assert sysex_data[6] == 0x05  # Program number = 5
        assert sysex_data[7] == 0xF7  # SysEx end
        assert len(sysex_data) == 8

    def test_generate_clear_all_presets_sysex(self):
        """Test generating SysEx to clear all presets."""
        generator = SysExGenerator()

        sysex_data = generator.generate_clear_all_presets()

        # Check clear all SysEx: F0 00 22 77 0C 00 F7
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x00  # MDMI manufacturer ID
        assert sysex_data[2] == 0x22
        assert sysex_data[3] == 0x77
        assert sysex_data[4] == 0x0C  # Clear all presets command
        assert sysex_data[5] == 0x00  # Type: FM = 0
        assert sysex_data[6] == 0xF7  # SysEx end
        assert len(sysex_data) == 7
