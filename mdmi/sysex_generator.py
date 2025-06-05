"""SysEx generator for MDMI communication."""

from mdmi.preset_parsers import Preset


class SysExGenerator:
    """Generator for MDMI SysEx messages."""

    MDMI_MANUFACTURER_ID = [0x00, 0x22, 0x77]
    LOAD_PRESET_CMD = 0x0A
    CLEAR_PRESET_CMD = 0x0B
    CLEAR_ALL_CMD = 0x0C
    DUMP_PRESET_CMD = 0x0D
    DUMP_CHANNEL_CMD = 0x0F
    FM_TYPE = 0x00

    def generate_preset_load(self, preset: Preset, program: int) -> bytes:
        """Generate SysEx message to load preset to program number.

        Args:
            preset: The preset to convert to SysEx
            program: MIDI program number

        Returns:
            SysEx message as bytes

        Raises:
            ValueError: If format is unsupported or program is invalid
        """
        if not (0 <= program <= 127):
            raise ValueError("Program must be between 0 and 127")

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
                        op.dt or 0,
                        op.ar or 0,
                        op.rs or 0,
                        op.dr or 0,
                        op.am or 0,
                        op.sl or 0,
                        op.sr or 0,
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
            program: MIDI program number to clear

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
            program: MIDI program number to dump

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

    def generate_dump_channel_request(self, midi_channel: int) -> bytes:
        """Generate SysEx message to request FM channel parameter dump.

        Args:
            midi_channel: MIDI channel (0-15) assigned to the FM channel

        Returns:
            SysEx message as bytes

        Raises:
            ValueError: If midi_channel is invalid
        """
        if not (0 <= midi_channel <= 15):
            raise ValueError("MIDI channel must be between 0 and 15")

        message = [0xF0] + self.MDMI_MANUFACTURER_ID
        message.extend([self.DUMP_CHANNEL_CMD, self.FM_TYPE, midi_channel, 0xF7])

        return bytes(message)
