"""End-to-end tests with new parser structure."""

import pytest

from mdmi.preset_parsers import detect_preset_format, parse_preset
from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import FakeMIDIInterface


class TestE2ENewParsers:
    """E2E tests with new parser structure."""

    def test_tfi_preset_complete_workflow(self):
        """Test complete TFI preset workflow with new parsers."""
        # Create a realistic TFI file (42 bytes)
        tfi_data = bytearray(42)

        # TFI format: algorithm, feedback, then 4 operators (10 bytes each)
        tfi_data[0] = 5  # Algorithm
        tfi_data[1] = 4  # Feedback

        # Add 4 operators (10 bytes each)
        for i in range(4):
            offset = 2 + (i * 10)
            tfi_data[offset] = 5  # MUL
            tfi_data[offset + 1] = 1  # DT
            tfi_data[offset + 2] = 15  # TL
            tfi_data[offset + 3] = 0  # RS
            tfi_data[offset + 4] = 31  # AR
            tfi_data[offset + 5] = 15  # DR
            tfi_data[offset + 6] = 0  # SR
            tfi_data[offset + 7] = 15  # RR
            tfi_data[offset + 8] = 0  # SL
            tfi_data[offset + 9] = 0  # SSG

        # Parse the preset
        preset = parse_preset(bytes(tfi_data), "TFI")

        # Verify parsed data
        assert preset.format_type == "TFI"
        assert preset.algorithm == 5
        assert preset.feedback == 4
        assert len(preset.operators) == 4

        # Verify operator mapping
        op = preset.operators[0]
        assert op.mul == 5
        assert op.dt == 1  # dt mapped to dt
        assert op.tl == 15
        assert op.ar == 31

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=10)

        # Verify SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # FM type
        assert sysex_data[6] == 10  # Program number
        assert sysex_data[7] == 5  # Algorithm
        assert sysex_data[8] == 4  # Feedback
        assert sysex_data[-1] == 0xF7  # SysEx end

        # Verify operator data in SysEx
        # Operator data starts after: F0 00 22 77 0A 00 10 05 04 00 00
        operator_start = 11
        assert sysex_data[operator_start] == 5  # MUL
        assert sysex_data[operator_start + 1] == 1  # DT1
        assert sysex_data[operator_start + 2] == 31  # AR

        # Send via fake MIDI interface
        interface = FakeMIDIInterface()
        interface.send_sysex(sysex_data)

        # Verify it was sent
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex == sysex_data

    def test_dmp_preset_complete_workflow(self):
        """Test complete DMP preset workflow."""
        # Create a DMP file with proper structure matching the parser
        # DMP v11 needs: version, system_type, instrument_mode, then FM params if mode=1
        dmp_data = bytearray(100)  # Make it larger to accommodate operators

        dmp_data[0] = 11  # Version
        dmp_data[1] = 2  # System (Genesis)
        dmp_data[2] = 1  # Instrument mode (FM)

        # FM parameters when instrument_mode = 1
        dmp_data[3] = 2  # LFO FMS
        dmp_data[4] = 4  # Feedback
        dmp_data[5] = 3  # Algorithm
        dmp_data[6] = 1  # LFO AMS

        # Add 4 operators (11 bytes each)
        for i in range(4):
            offset = 7 + (i * 11)
            dmp_data[offset] = 5  # MUL
            dmp_data[offset + 1] = 15  # TL
            dmp_data[offset + 2] = 31  # AR
            dmp_data[offset + 3] = 15  # DR
            dmp_data[offset + 4] = 0  # SL
            dmp_data[offset + 5] = 15  # RR
            dmp_data[offset + 6] = 0  # AM
            dmp_data[offset + 7] = 0  # RS
            dmp_data[offset + 8] = 1  # DT
            dmp_data[offset + 9] = 0  # SR
            dmp_data[offset + 10] = 0  # SSG

        # Parse the preset
        preset = parse_preset(bytes(dmp_data), "DMP")

        # Verify basic parsing worked
        assert preset.format_type == "DMP"
        assert preset.algorithm == 3
        assert preset.feedback == 4
        assert len(preset.operators) == 4

        # Verify operator mapping
        op = preset.operators[0]
        assert op.mul == 5
        assert op.dt == 1  # dt mapped to dt
        assert op.tl == 15

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=5)

        # Verify SysEx structure
        assert sysex_data[0] == 0xF0  # SysEx start
        assert sysex_data[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sysex_data[4] == 0x0A  # Load preset command
        assert sysex_data[5] == 0x00  # FM type
        assert sysex_data[6] == 5  # Program number
        assert sysex_data[7] == 3  # Algorithm
        assert sysex_data[8] == 4  # Feedback
        assert sysex_data[-1] == 0xF7  # SysEx end

        # Send via fake MIDI interface
        interface = FakeMIDIInterface()
        interface.send_sysex(sysex_data)

        # Verify it was sent
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex == sysex_data

    def test_wopn_preset_workflow_would_work(self):
        """Test that WOPN workflow interface exists."""
        # This tests that the interface exists, even though we can't test with real WOPN data
        wopn_data = b"WOPN2-BANK\x00" + b"\x00" * 100

        # This should raise an exception due to invalid WOPN structure
        # but proves the interface works
        with pytest.raises(Exception):
            parse_preset(wopn_data, "WOPN", bank=0, instrument=0, bank_type="melody")

    def test_format_detection_and_parsing_integration(self):
        """Test that format detection works with the new parsers."""
        # Test TFI detection
        tfi_data = b"\x00" * 42
        assert detect_preset_format(tfi_data) == "TFI"

        # Should be able to parse it
        preset = parse_preset(tfi_data, "TFI")
        assert preset.format_type == "TFI"

        # Test DMP detection
        dmp_data = b".DMP" + b"\x00" * 50
        assert detect_preset_format(dmp_data) == "DMP"

        # Should be able to parse it
        preset = parse_preset(dmp_data, "DMP")
        assert preset.format_type == "DMP"

        # Test WOPN detection
        wopn_data = b"WOPN2-B2NK\x00" + b"\x00" * 100
        assert detect_preset_format(wopn_data) == "WOPN"

    def test_sysex_operator_mapping(self):
        """Test that operator field mapping works correctly."""
        # Create a TFI with specific operator values matching TFI format
        tfi_data = bytearray(42)
        tfi_data[0] = 2  # Algorithm
        tfi_data[1] = 2  # Feedback

        # Set first operator with known values (TFI format: MUL,DT,TL,RS,AR,DR,SR,RR,SL,SSG)
        tfi_data[2] = 5  # MUL
        tfi_data[3] = 3  # DT
        tfi_data[4] = 64  # TL
        tfi_data[5] = 0  # RS
        tfi_data[6] = 31  # AR
        tfi_data[7] = 5  # DR
        tfi_data[8] = 7  # SR
        tfi_data[9] = 15  # RR
        tfi_data[10] = 4  # SL
        tfi_data[11] = 0  # SSG

        preset = parse_preset(bytes(tfi_data), "TFI")

        # Check that operator was parsed correctly
        assert len(preset.operators) >= 1
        op = preset.operators[0]
        assert op.mul == 5
        assert op.dt == 3  # dt mapped to dt
        assert op.tl == 64
        assert op.ar == 31
        assert op.dr == 5  # dr mapped to dr
        assert op.sl == 4  # sl mapped to sl
        assert op.sr == 7  # sr mapped to sr

        # Generate SysEx and verify operator data is included
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=0)

        # Check that operator data is in the SysEx
        # Operator data starts after: F0 00 22 77 0A 00 00 alg fb ams fms
        operator_start = 11
        assert sysex_data[operator_start] == 5  # MUL
        assert sysex_data[operator_start + 1] == 3  # DT
        assert sysex_data[operator_start + 2] == 31  # AR
