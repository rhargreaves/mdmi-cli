"""End-to-end integration tests."""

from pathlib import Path
import tempfile

from mdmi.preset_parsers import detect_preset_format, parse_preset
from mdmi.sysex_generator import SysExGenerator
from mdmi.fake_midi_interface import FakeMidiInterface


class TestE2E:
    """End-to-end integration tests."""

    def test_tfi_preset_loading_e2e(self):
        """Test complete TFI preset loading workflow."""
        # Create a minimal TFI file (42 bytes)
        tfi_data = bytearray(42)
        tfi_data[0] = 0x03  # Algorithm 3
        tfi_data[1] = 0x04  # Feedback 4

        # Add some operator data (pattern similar to real TFI format)
        for i in range(4):  # 4 operators
            offset = 2 + (i * 10)
            tfi_data[offset] = 0x15  # MUL=5, DT1=1
            tfi_data[offset + 1] = 0x40  # TL=64
            tfi_data[offset + 2] = 0x9F  # AR=31, RS=2

        # Detect format
        assert detect_preset_format(bytes(tfi_data)) == "TFI"

        # Parse preset
        preset = parse_preset(bytes(tfi_data), "TFI")

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=5)

        # Send via fake interface
        interface = FakeMidiInterface()
        interface.send_sysex(sysex_data)

        # Verify
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex is not None
        assert sent_sysex[0] == 0xF0  # SysEx start
        assert sent_sysex[-1] == 0xF7  # SysEx end
        assert sent_sysex[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sent_sysex[6] == 5  # Program number

    def test_dmp_preset_loading_e2e(self):
        """Test complete DMP preset loading workflow."""
        # Create a DMP file (version 8 format)
        dmp_data = bytearray()
        dmp_data.append(8)  # Version 8
        dmp_data.append(1)  # Instrument mode (FM)
        dmp_data.append(0)  # Unknown byte

        # FM parameters
        dmp_data.extend([0x03, 0x04, 0x05, 0x02])  # LFO_FMS, Feedback, Algorithm, LFO_AMS

        # Operator data (4 operators × 11 bytes each)
        for i in range(4):
            dmp_data.extend([0x01, 0x40, 0x1F, 0x0F, 0x0F, 0x00, 0x02, 0x03, 0x00, 0x00, 0x00])

        # Detect format
        assert detect_preset_format(bytes(dmp_data)) == "DMP"

        # Parse preset
        preset = parse_preset(bytes(dmp_data), "DMP")

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program=10)

        # Send via fake interface
        interface = FakeMidiInterface()
        interface.send_sysex(sysex_data)

        # Verify
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex is not None
        assert sent_sysex[0] == 0xF0  # SysEx start
        assert sent_sysex[-1] == 0xF7  # SysEx end
        assert sent_sysex[1:4] == bytes([0x00, 0x22, 0x77])  # MDMI ID
        assert sent_sysex[6] == 10  # Program number

    def test_multiple_presets_e2e(self):
        """Test loading multiple presets to different programs."""
        interface = FakeMidiInterface()
        generator = SysExGenerator()

        # Load TFI to program 0
        tfi_data = bytearray(42)
        tfi_data[0] = 0x02  # Algorithm 2
        tfi_data[1] = 0x03  # Feedback 3
        # Add minimal operator data
        for i in range(4):
            offset = 2 + (i * 10)
            tfi_data[offset] = 0x01  # Some operator data

        tfi_preset = parse_preset(bytes(tfi_data), "TFI")
        tfi_sysex = generator.generate_preset_load(tfi_preset, program=0)
        interface.send_sysex(tfi_sysex)

        # Create and load DMP to program 1
        dmp_data = bytearray([8, 1, 0, 0x03, 0x04, 0x05, 0x02])  # Header + FM params
        for i in range(4):  # 4 operators
            dmp_data.extend([0x01, 0x40, 0x1F, 0x0F, 0x0F, 0x00, 0x02, 0x03, 0x00, 0x00, 0x00])

        dmp_preset = parse_preset(bytes(dmp_data), "DMP")
        dmp_sysex = generator.generate_preset_load(dmp_preset, program=1)
        interface.send_sysex(dmp_sysex)

        # Verify both messages were sent
        assert len(interface.sent_messages) == 2

        # Verify program assignments
        assert interface.sent_messages[0][6] == 0  # TFI to program 0
        assert interface.sent_messages[1][6] == 1  # DMP to program 1

    def test_file_io_e2e(self):
        """Test end-to-end with actual file I/O."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a TFI file
            tfi_path = Path(tmpdir) / "test.tfi"
            tfi_data = bytearray(42)
            tfi_data[0] = 0x05  # Algorithm 5
            tfi_data[1] = 0x07  # Feedback 7
            # Add minimal operator data
            for i in range(4):
                offset = 2 + (i * 10)
                tfi_data[offset] = 0x01
            tfi_path.write_bytes(tfi_data)

            # Parse from file
            data = tfi_path.read_bytes()
            format_type = detect_preset_format(data)
            assert format_type == "TFI"

            preset = parse_preset(data, format_type)

            # Generate and send SysEx
            generator = SysExGenerator()
            sysex_data = generator.generate_preset_load(preset, program=15)

            interface = FakeMidiInterface()
            interface.send_sysex(sysex_data)

            # Verify
            sent_sysex = interface.get_last_sysex()
            assert sent_sysex is not None
            assert sent_sysex[6] == 15  # Program 15
            assert preset.algorithm == 5
