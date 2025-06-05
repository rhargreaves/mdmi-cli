"""SysEx generator for MDMI communication."""

from mdmi.preset_parsers import Preset


class SysExGenerator:
    """Generator for MDMI SysEx messages."""

    MDMI_MANUFACTURER_ID = [0x00, 0x22, 0x77]
    LOAD_PRESET_CMD = 0x0A
    CLEAR_PRESET_CMD = 0x0B
    CLEAR_ALL_CMD = 0x0C
    DUMP_PRESET_CMD = 0x0D
    FM_TYPE = 0x00

    def generate_preset_load(self, preset: Preset, program: int) -> bytes:
        """Generate SysEx message to load preset to program number.

        Args:
            preset: The preset to convert to SysEx
            program: MIDI program number (0-127)

        Returns:
            SysEx message as bytes

        Raises:
            ValueError: If format is unsupported or program is invalid
        """
        if not (0 <= program <= 127):
            raise ValueError("Program must be between 0 and 127")

        if preset.format_type not in ["TFI", "DMP", "WOPN"]:
            msg = f"Unsupported preset format: {preset.format_type}"
            raise ValueError(msg)

        # Start with MDMI SysEx header
        message = [0xF0] + self.MDMI_MANUFACTURER_ID
        message.extend([self.LOAD_PRESET_CMD, self.FM_TYPE, program])

        # Add FM channel parameters
        message.append(preset.algorithm or 0)
        message.append(preset.feedback or 0)
        message.append(preset.lfo_ams or 0)
        message.append(preset.lfo_fms or 0)

        # Add operator data (4 operators)
        operators = preset.operators or []
        for i in range(4):
            if i < len(operators):
                op = operators[i]
                message.extend(
                    [
                        op.mul or 0,
                        op.dt1 or 0,
                        op.ar or 0,
                        op.rs or 0,
                        op.d1r or 0,
                        op.am or 0,
                        op.d1l or 0,
                        op.d2r or 0,
                        op.rr or 0,
                        op.tl or 0,
                        op.ssg or 0,
                    ]
                )
            else:
                # Fill with zeros if operator doesn't exist
                message.extend([0] * 11)

        # End SysEx
        message.append(0xF7)

        return bytes(message)

    def generate_clear_preset(self, program: int) -> bytes:
        """Generate SysEx message to clear a specific preset.

        Args:
            program: MIDI program number (0-127) to clear

        Returns:
            SysEx message as bytes

        Raises:
            ValueError: If program is invalid
        """
        if not (0 <= program <= 127):
            raise ValueError("Program must be between 0 and 127")

        message = [0xF0] + self.MDMI_MANUFACTURER_ID
        message.extend([self.CLEAR_PRESET_CMD, self.FM_TYPE, program, 0xF7])

        return bytes(message)

    def generate_clear_all_presets(self) -> bytes:
        """Generate SysEx message to clear all presets.

        Returns:
            SysEx message as bytes
        """
        message = [0xF0] + self.MDMI_MANUFACTURER_ID
        message.extend([self.CLEAR_ALL_CMD, self.FM_TYPE, 0xF7])

        return bytes(message)

    def generate_dump_preset_request(self, program: int) -> bytes:
        """Generate SysEx message to request preset dump.

        Args:
            program: MIDI program number (0-127) to dump

        Returns:
            SysEx message as bytes

        Raises:
            ValueError: If program is invalid
        """
        if not (0 <= program <= 127):
            raise ValueError("Program must be between 0 and 127")

        message = [0xF0] + self.MDMI_MANUFACTURER_ID
        message.extend([self.DUMP_PRESET_CMD, self.FM_TYPE, program, 0xF7])

        return bytes(message)
