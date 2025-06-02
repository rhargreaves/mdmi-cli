"""End-to-end integration tests."""

from pathlib import Path
import tempfile

from mdmi.preset_parsers import TFIParser, DMPParser
from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import FakeMIDIInterface


class TestE2E:
    """End-to-end integration tests."""

    def test_tfi_preset_loading_e2e(self):
        """Test complete TFI preset loading workflow."""
        # Create a minimal TFI file
        tfi_data = bytearray(42)
        tfi_data[0] = 0x23  # Algorithm 3, Feedback 4

        # Add some operator data
        for i in range(4):  # 4 operators
            offset = 1 + (i * 10)
            tfi_data[offset] = 0x15  # MUL=5, DT1=1
            tfi_data[offset + 1] = 0x9F  # AR=31, RS=2
            tfi_data[offset + 5] = 0x40  # TL=64

        # Parse preset
        parser = TFIParser()
        preset = parser.parse(bytes(tfi_data))

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, channel=2)

        # Send via fake interface
        interface = FakeMIDIInterface()
        interface.send_sysex(sysex_data)

        # Verify
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex is not None
        assert sent_sysex[0] == 0xF0  # SysEx start
        assert sent_sysex[-1] == 0xF7  # SysEx end
        assert sent_sysex[1] == 0x43  # Manufacturer ID
        assert sent_sysex[4] == 2  # Channel

    def test_dmp_preset_loading_e2e(self):
        """Test complete DMP preset loading workflow."""
        # Create a minimal DMP file
        dmp_data = bytearray()
        dmp_data.extend(b".DMP")  # Signature
        dmp_data.append(11)  # Version 11
        dmp_data.append(1)  # System (YM2612)

        # Name (32 bytes)
        name = b"Test DMP Preset\x00"
        name_padded = name + b"\x00" * (32 - len(name))
        dmp_data.extend(name_padded)

        # FM parameters (11 bytes)
        dmp_data.extend([0x35, 0x12] + [0x00] * 9)  # Alg=5, FB=6, LFO

        # Parse preset
        parser = DMPParser()
        preset = parser.parse(bytes(dmp_data))

        # Generate SysEx
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, channel=1)

        # Send via fake interface
        interface = FakeMIDIInterface()
        interface.send_sysex(sysex_data)

        # Verify
        sent_sysex = interface.get_last_sysex()
        assert sent_sysex is not None
        assert sent_sysex[0] == 0xF0  # SysEx start
        assert sent_sysex[-1] == 0xF7  # SysEx end
        assert sent_sysex[4] == 1  # Channel
        assert preset.name == "Test DMP Preset"
        assert preset.algorithm == 5
        assert preset.feedback == 6

    def test_multiple_presets_e2e(self):
        """Test loading multiple presets to different channels."""
        interface = FakeMIDIInterface()
        generator = SysExGenerator()

        # Load TFI to channel 0
        tfi_data = b"\x00" * 42
        tfi_parser = TFIParser()
        tfi_preset = tfi_parser.parse(tfi_data)
        tfi_sysex = generator.generate_preset_load(tfi_preset, channel=0)
        interface.send_sysex(tfi_sysex)

        # Create and load DMP to channel 1
        dmp_data = (
            b".DMP\x0b\x01"  # Signature, version, system
            + b"DMP Test\x00"
            + b"\x00" * 22  # Name padded to 32 bytes
            + b"\x1a\x25"
            + b"\x00" * 9  # FM parameters
        )
        dmp_parser = DMPParser()
        dmp_preset = dmp_parser.parse(dmp_data)
        dmp_sysex = generator.generate_preset_load(dmp_preset, channel=1)
        interface.send_sysex(dmp_sysex)

        # Verify both messages were sent
        assert len(interface.sent_messages) == 2

        # Verify channel assignments
        assert interface.sent_messages[0][4] == 0  # TFI to channel 0
        assert interface.sent_messages[1][4] == 1  # DMP to channel 1

    def test_file_io_e2e(self):
        """Test end-to-end with actual file I/O."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a TFI file
            tfi_path = Path(tmpdir) / "test.tfi"
            tfi_data = b"\x23" + b"\x00" * 41  # Algorithm 3, rest zeros
            tfi_path.write_bytes(tfi_data)

            # Parse from file
            data = tfi_path.read_bytes()
            parser = TFIParser()
            preset = parser.parse(data)

            # Generate and send SysEx
            generator = SysExGenerator()
            sysex_data = generator.generate_preset_load(preset, channel=3)

            interface = FakeMIDIInterface()
            interface.send_sysex(sysex_data)

            # Verify
            sent_sysex = interface.get_last_sysex()
            assert sent_sysex is not None
            assert sent_sysex[4] == 3  # Channel 3
            assert preset.algorithm == 3
