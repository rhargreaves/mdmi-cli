"""Tests for SysEx generator."""

import pytest

from mdmi.sysex_generator import SysExGenerator
from mdmi.preset_parsers import Preset, FMOperator


class TestSysExGenerator:
    """Tests for SysEx generator."""

    def test_generate_preset_load_sysex_tfi(self):
        """Test generating complete SysEx for TFI preset with correct MDMI format."""
        generator = SysExGenerator()

        # Create a TFI preset with specific operator values
        operators = [
            FMOperator(mul=1, dt=2, ar=31, rs=1, dr=15, am=0, sl=14, sr=0, rr=15, tl=39, ssg=0),
            FMOperator(mul=4, dt=6, ar=24, rs=1, dr=9, am=0, sl=6, sr=9, rr=7, tl=36, ssg=0),
            FMOperator(mul=2, dt=7, ar=31, rs=3, dr=23, am=0, sl=9, sr=15, rr=1, tl=4, ssg=0),
            FMOperator(mul=1, dt=3, ar=27, rs=2, dr=4, am=0, sl=10, sr=4, rr=6, tl=2, ssg=0),
        ]

        preset = Preset(
            format_type="TFI",
            algorithm=2,
            feedback=5,
            lfo_ams=1,
            lfo_fms=3,
            operators=operators,
        )

        sysex_data = generator.generate_preset_load(preset, program=10)

        # Expected complete message structure:
        # F0 00 22 77 0A 00 0A 02 05 01 03 [44 operator bytes] F7
        expected = [
            0xF0,  # SysEx start
            0x00,
            0x22,
            0x77,  # MDMI manufacturer ID
            0x0A,  # Load preset command
            0x00,  # FM type
            0x0A,  # Program number (10)
            0x02,  # Algorithm (2)
            0x05,  # Feedback (5)
            0x01,  # LFO AMS (1)
            0x03,  # LFO FMS (3)
            # Operator 1: mul=1, dt=2, ar=31, rs=1, dr=15, am=0, sl=14, sr=0, rr=15, tl=39, ssg=0
            0x01,
            0x02,
            0x1F,
            0x01,
            0x0F,
            0x00,
            0x0E,
            0x00,
            0x0F,
            0x27,
            0x00,
            # Operator 2: mul=4, dt=6, ar=24, rs=1, dr=9, am=0, sl=6, sr=9, rr=7, tl=36, ssg=0
            0x04,
            0x06,
            0x18,
            0x01,
            0x09,
            0x00,
            0x06,
            0x09,
            0x07,
            0x24,
            0x00,
            # Operator 3: mul=2, dt=7, ar=31, rs=3, dr=23, am=0, sl=9, sr=15, rr=1, tl=4, ssg=0
            0x02,
            0x07,
            0x1F,
            0x03,
            0x17,
            0x00,
            0x09,
            0x0F,
            0x01,
            0x04,
            0x00,
            # Operator 4: mul=1, dt=3, ar=27, rs=2, dr=4, am=0, sl=10, sr=4, rr=6, tl=2, ssg=0
            0x01,
            0x03,
            0x1B,
            0x02,
            0x04,
            0x00,
            0x0A,
            0x04,
            0x06,
            0x02,
            0x00,
            0xF7,  # SysEx end
        ]

        assert list(sysex_data) == expected
        assert len(sysex_data) == 56  # 6 header + 5 parameters + 44 operator bytes + 1 end

    def test_generate_preset_load_sysex_dmp(self):
        """Test generating complete SysEx for DMP preset."""
        generator = SysExGenerator()

        # Create DMP preset with 2 operators
        operators = [
            FMOperator(mul=3, dt=1, ar=20, rs=2, dr=10, am=1, sl=8, sr=5, rr=12, tl=50, ssg=2),
            FMOperator(mul=7, dt=4, ar=25, rs=1, dr=8, am=0, sl=12, sr=7, rr=9, tl=30, ssg=0),
        ]

        preset = Preset(
            format_type="DMP",
            name="Test Preset",
            algorithm=3,
            feedback=7,
            lfo_ams=1,
            lfo_fms=2,
            operators=operators,
        )

        sysex_data = generator.generate_preset_load(preset, program=15)

        # Expected complete message structure:
        # F0 00 22 77 0A 00 0F 03 07 01 02 [44 operator bytes] F7
        expected = [
            0xF0,  # SysEx start
            0x00,
            0x22,
            0x77,  # MDMI manufacturer ID
            0x0A,  # Load preset command
            0x00,  # FM type
            0x0F,  # Program number (15)
            0x03,  # Algorithm (3)
            0x07,  # Feedback (7)
            0x01,  # LFO AMS (1)
            0x02,  # LFO FMS (2)
            # Operator 1: mul=3, dt=1, ar=20, rs=2, dr=10, am=1, sl=8, sr=5, rr=12, tl=50, ssg=2
            0x03,
            0x01,
            0x14,
            0x02,
            0x0A,
            0x01,
            0x08,
            0x05,
            0x0C,
            0x32,
            0x02,
            # Operator 2: mul=7, dt=4, ar=25, rs=1, dr=8, am=0, sl=12, sr=7, rr=9, tl=30, ssg=0
            0x07,
            0x04,
            0x19,
            0x01,
            0x08,
            0x00,
            0x0C,
            0x07,
            0x09,
            0x1E,
            0x00,
            # Operator 3: empty (all zeros)
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            # Operator 4: empty (all zeros)
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0xF7,  # SysEx end
        ]

        assert list(sysex_data) == expected
        assert len(sysex_data) == 56  # 6 header + 5 parameters + 44 operator bytes + 1 end

    def test_generate_preset_load_wopn(self):
        """Test generating complete SysEx for WOPN preset."""
        generator = SysExGenerator()

        # Create WOPN preset with all 4 operators
        operators = [
            FMOperator(mul=2, dt=3, ar=30, rs=0, dr=12, am=0, sl=5, sr=8, rr=14, tl=20, ssg=1),
            FMOperator(mul=1, dt=0, ar=28, rs=1, dr=10, am=1, sl=7, sr=6, rr=11, tl=40, ssg=0),
            FMOperator(mul=5, dt=2, ar=26, rs=2, dr=14, am=0, sl=9, sr=10, rr=8, tl=15, ssg=3),
            FMOperator(mul=3, dt=1, ar=22, rs=1, dr=6, am=0, sl=3, sr=4, rr=13, tl=60, ssg=0),
        ]

        preset = Preset(
            format_type="WOPN",
            name="WOPN Instrument",
            algorithm=5,
            feedback=3,
            lfo_ams=2,
            lfo_fms=1,
            operators=operators,
        )

        sysex_data = generator.generate_preset_load(preset, program=127)

        # Expected complete message structure:
        # F0 00 22 77 0A 00 7F 05 03 02 01 [44 operator bytes] F7
        expected = [
            0xF0,  # SysEx start
            0x00,
            0x22,
            0x77,  # MDMI manufacturer ID
            0x0A,  # Load preset command
            0x00,  # FM type
            0x7F,  # Program number (127)
            0x05,  # Algorithm (5)
            0x03,  # Feedback (3)
            0x02,  # LFO AMS (2)
            0x01,  # LFO FMS (1)
            # Operator 1: mul=2, dt=3, ar=30, rs=0, dr=12, am=0, sl=5, sr=8, rr=14, tl=20, ssg=1
            0x02,
            0x03,
            0x1E,
            0x00,
            0x0C,
            0x00,
            0x05,
            0x08,
            0x0E,
            0x14,
            0x01,
            # Operator 2: mul=1, dt=0, ar=28, rs=1, dr=10, am=1, sl=7, sr=6, rr=11, tl=40, ssg=0
            0x01,
            0x00,
            0x1C,
            0x01,
            0x0A,
            0x01,
            0x07,
            0x06,
            0x0B,
            0x28,
            0x00,
            # Operator 3: mul=5, dt=2, ar=26, rs=2, dr=14, am=0, sl=9, sr=10, rr=8, tl=15, ssg=3
            0x05,
            0x02,
            0x1A,
            0x02,
            0x0E,
            0x00,
            0x09,
            0x0A,
            0x08,
            0x0F,
            0x03,
            # Operator 4: mul=3, dt=1, ar=22, rs=1, dr=6, am=0, sl=3, sr=4, rr=13, tl=60, ssg=0
            0x03,
            0x01,
            0x16,
            0x01,
            0x06,
            0x00,
            0x03,
            0x04,
            0x0D,
            0x3C,
            0x00,
            0xF7,  # SysEx end
        ]

        assert list(sysex_data) == expected
        assert len(sysex_data) == 56  # 6 header + 5 parameters + 44 operator bytes + 1 end

    def test_generate_preset_load_missing_operators(self):
        """Test generating SysEx when preset has fewer than 4 operators."""
        generator = SysExGenerator()

        # Create preset with only 1 operator
        operators = [
            FMOperator(mul=1, dt=2, ar=31, rs=1, dr=15, am=0, sl=14, sr=0, rr=15, tl=39, ssg=0),
        ]

        preset = Preset(
            format_type="TFI",
            algorithm=0,
            feedback=0,
            lfo_ams=0,
            lfo_fms=0,
            operators=operators,
        )

        sysex_data = generator.generate_preset_load(preset, program=0)

        # Should pad missing operators with zeros
        expected = [
            0xF0,  # SysEx start
            0x00,
            0x22,
            0x77,  # MDMI manufacturer ID
            0x0A,  # Load preset command
            0x00,  # FM type
            0x00,  # Program number (0)
            0x00,  # Algorithm (0)
            0x00,  # Feedback (0)
            0x00,  # LFO AMS (0)
            0x00,  # LFO FMS (0)
            # Operator 1: mul=1, dt=2, ar=31, rs=1, dr=15, am=0, sl=14, sr=0, rr=15, tl=39, ssg=0
            0x01,
            0x02,
            0x1F,
            0x01,
            0x0F,
            0x00,
            0x0E,
            0x00,
            0x0F,
            0x27,
            0x00,
            # Operators 2-4: empty (all zeros)
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0xF7,  # SysEx end
        ]

        assert list(sysex_data) == expected
        assert len(sysex_data) == 56  # 6 header + 5 parameters + 44 operator bytes + 1 end

    def test_generate_preset_load_invalid_program(self):
        """Test generating SysEx with invalid program number."""
        generator = SysExGenerator()

        preset = Preset(format_type="TFI")

        with pytest.raises(ValueError, match="Program must be between 0 and 127"):
            generator.generate_preset_load(preset, program=128)

        with pytest.raises(ValueError, match="Program must be between 0 and 127"):
            generator.generate_preset_load(preset, program=-1)

    def test_generate_clear_preset_sysex(self):
        """Test generating complete SysEx to clear a specific preset."""
        generator = SysExGenerator()

        sysex_data = generator.generate_clear_preset(program=42)

        # Check complete clear preset SysEx: F0 00 22 77 0B 00 2A F7
        expected = [0xF0, 0x00, 0x22, 0x77, 0x0B, 0x00, 0x2A, 0xF7]
        assert list(sysex_data) == expected
        assert len(sysex_data) == 8

    def test_generate_clear_preset_invalid_program(self):
        """Test clear preset with invalid program numbers."""
        generator = SysExGenerator()

        with pytest.raises(ValueError, match="Program must be between 0 and 127"):
            generator.generate_clear_preset(program=128)

        with pytest.raises(ValueError, match="Program must be between 0 and 127"):
            generator.generate_clear_preset(program=-1)

    def test_generate_clear_all_presets_sysex(self):
        """Test generating complete SysEx to clear all presets."""
        generator = SysExGenerator()

        sysex_data = generator.generate_clear_all_presets()

        # Check complete clear all SysEx: F0 00 22 77 0C 00 F7
        expected = [0xF0, 0x00, 0x22, 0x77, 0x0C, 0x00, 0xF7]
        assert list(sysex_data) == expected
        assert len(sysex_data) == 7

    def test_generate_dump_channel_request(self):
        """Test generating SysEx for channel dump request."""
        generator = SysExGenerator()

        # Test with various MIDI channels
        for channel in [0, 5, 15]:
            sysex_data = generator.generate_dump_channel_request(channel)

            # Expected format: F0 00 22 77 0F 00 <channel> F7
            expected = [0xF0, 0x00, 0x22, 0x77, 0x0F, 0x00, channel, 0xF7]
            assert list(sysex_data) == expected
            assert len(sysex_data) == 8

    def test_generate_dump_channel_request_invalid_channel(self):
        """Test generating channel dump request with invalid MIDI channel."""
        generator = SysExGenerator()

        # Test invalid channels
        with pytest.raises(ValueError, match="MIDI channel must be between 0 and 15"):
            generator.generate_dump_channel_request(16)

        with pytest.raises(ValueError, match="MIDI channel must be between 0 and 15"):
            generator.generate_dump_channel_request(-1)
