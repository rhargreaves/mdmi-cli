"""SysEx generator for Mega Drive MIDI Interface preset loading."""

from typing import List
from .preset_parsers import Preset


class SysExGenerator:
    """Generates SysEx messages for the Mega Drive MIDI Interface."""

    # MDMI SysEx constants based on Mega Drive MIDI Interface spec
    MANUFACTURER_ID = 0x43  # Yamaha manufacturer ID (YM2612 compatibility)
    DEVICE_ID = 0x76  # MDMI device ID
    PRESET_LOAD_CMD = 0x10  # Command for loading presets

    def generate_preset_load(self, preset: Preset, channel: int) -> bytes:
        """Generate SysEx message to load preset to specified channel.

        Args:
            preset: The preset to load
            channel: Target FM channel (0-5)

        Returns:
            bytes: Complete SysEx message

        Raises:
            ValueError: If channel is invalid or format unsupported
        """
        if not (0 <= channel <= 5):
            raise ValueError("Channel must be between 0 and 5")

        supported_formats = ["TFI", "DMP", "WOPN"]
        if preset.format_type not in supported_formats:
            msg = f"Unsupported preset format: {preset.format_type}"
            raise ValueError(msg)

        # Build SysEx message
        sysex = [0xF0]  # Start of SysEx
        sysex.append(self.MANUFACTURER_ID)  # Manufacturer ID
        sysex.append(self.DEVICE_ID)  # Device ID
        sysex.append(self.PRESET_LOAD_CMD)  # Command
        sysex.append(channel)  # Target channel

        # Add preset data based on format
        if preset.format_type == "TFI":
            sysex.extend(self._encode_tfi_preset(preset))
        elif preset.format_type == "DMP":
            sysex.extend(self._encode_dmp_preset(preset))
        elif preset.format_type == "WOPN":
            sysex.extend(self._encode_wopn_preset(preset))

        # Add checksum (simple XOR checksum)
        checksum = 0
        for byte in sysex[1:]:  # Exclude F0
            checksum ^= byte
        sysex.append(checksum & 0x7F)  # Ensure 7-bit value

        sysex.append(0xF7)  # End of SysEx

        return bytes(sysex)

    def _encode_tfi_preset(self, preset: Preset) -> List[int]:
        """Encode TFI preset data for SysEx."""
        data = []

        # Algorithm and feedback
        alg_fb = (preset.feedback << 3) | (preset.algorithm & 0x07)
        data.append(alg_fb & 0x7F)

        # LFO settings
        lfo = (preset.lfo_fms << 4) | (preset.lfo_ams & 0x03)
        data.append(lfo & 0x7F)

        # Operator data (4 operators)
        for op in preset.operators[:4]:  # Ensure max 4 operators
            # Pack operator parameters into 7-bit values
            data.append(op.mul & 0x7F)
            data.append(op.dt1 & 0x7F)
            data.append(op.ar & 0x7F)
            data.append(op.rs & 0x7F)
            data.append(op.d1r & 0x7F)
            data.append(op.am & 0x7F)
            data.append(op.d1l & 0x7F)
            data.append(op.d2r & 0x7F)
            data.append(op.rr & 0x7F)
            data.append(op.tl & 0x7F)
            data.append(op.ssg & 0x7F)

        return data

    def _encode_dmp_preset(self, preset: Preset) -> List[int]:
        """Encode DMP preset data for SysEx."""
        data = []

        # Algorithm and feedback
        alg_fb = (preset.feedback << 3) | (preset.algorithm & 0x07)
        data.append(alg_fb & 0x7F)

        # LFO settings
        lfo = (preset.lfo_fms << 4) | (preset.lfo_ams & 0x03)
        data.append(lfo & 0x7F)

        # For DMP, we may not have operator data, so send minimal
        # This would need to be expanded based on actual DMP content
        return data

    def _encode_wopn_preset(self, preset: Preset) -> List[int]:
        """Encode WOPN preset data for SysEx."""
        data = []

        # For WOPN, we would need to select a specific instrument
        # from the bank and encode its parameters
        # This is a simplified implementation
        data.append(0x00)  # Bank number
        data.append(0x00)  # Instrument number

        return data
