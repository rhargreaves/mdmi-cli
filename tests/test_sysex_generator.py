"""Tests for SysEx generator."""

import pytest

from mdmi.sysex_generator import SysExGenerator
from mdmi.preset_parsers import Preset, FMOperator


class TestSysExGenerator:
    """Tests for SysEx generator."""

    def test_generate_preset_load_sysex_tfi(self):
        """Test generating SysEx for TFI preset."""
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

        sysex_data = generator.generate_preset_load(preset, channel=0)

        # Check SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x43  # Manufacturer ID (example)
        assert sysex_data[-1] == 0xF7  # SysEx end
        assert len(sysex_data) > 10  # Should have substantial data

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

        sysex_data = generator.generate_preset_load(preset, channel=1)

        # Check SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1] == 0x43  # Manufacturer ID
        assert sysex_data[-1] == 0xF7  # SysEx end

    def test_generate_preset_load_invalid_channel(self):
        """Test generating SysEx with invalid channel."""
        generator = SysExGenerator()

        preset = Preset(format_type="TFI")

        error_msg = "Channel must be between 0 and 5"
        with pytest.raises(ValueError, match=error_msg):
            generator.generate_preset_load(preset, channel=10)

    def test_generate_preset_load_unsupported_format(self):
        """Test generating SysEx for unsupported format."""
        generator = SysExGenerator()

        preset = Preset(format_type="UNKNOWN")

        error_msg = "Unsupported preset format"
        with pytest.raises(ValueError, match=error_msg):
            generator.generate_preset_load(preset, channel=0)
