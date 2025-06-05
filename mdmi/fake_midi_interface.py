"""Fake MIDI interface for testing and development."""

from typing import List, Optional
import time


class FakeMidiInterface:
    """Fake MIDI interface for testing."""

    def __init__(self):
        """Initialize fake MIDI interface."""
        self.port_name = "Fake MIDI Interface"
        self.input_port_name = "Fake MIDI Interface"
        self.sent_messages: List[bytes] = []
        self.simulate_pong = True  # Whether to simulate pong responses

    def send_sysex(self, data: bytes) -> None:
        """Record SysEx data for testing.

        Args:
            data: Complete SysEx message including F0/F7
        """
        # Print the SysEx message for debugging
        hex_data = " ".join(f"{b:02X}" for b in data)
        print(f"FakeMidiInterface: Sending SysEx ({len(data)} bytes): {hex_data}")

        self.sent_messages.append(data)

    def wait_for_sysex(self, timeout: float = 5.0) -> Optional[bytes]:
        """Simulate waiting for SysEx message.

        Args:
            timeout: Maximum time to wait in seconds (ignored in fake)

        Returns:
            Simulated response if last sent message was a ping or dump request
        """
        if not self.simulate_pong:
            return None

        # Check if we have any sent messages
        if not self.sent_messages or len(self.sent_messages[-1]) < 6:
            return None

        last_msg = self.sent_messages[-1]

        # Must start with F0 00 22 77 and end with F7
        if last_msg[0] != 0xF0 or last_msg[1:4] != bytes([0x00, 0x22, 0x77]) or last_msg[-1] != 0xF7:
            return None

        # Simulate a small delay
        time.sleep(0.01)

        # Check message type
        cmd = last_msg[4]

        if cmd == 0x01:  # Ping (00 22 77 01)
            return self._generate_ping_response()
        elif cmd == 0x0D:  # Dump request (00 22 77 0D <type> <program>)
            return self._generate_preset_dump_response(last_msg)
        elif cmd == 0x0F:  # Channel dump request (00 22 77 0F <type> <midi_channel>)
            return self._generate_channel_dump_response(last_msg)

        return None

    def _generate_ping_response(self) -> bytes:
        """Generate a ping response."""
        pong_response = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        print(f"FakeMIDIInterface: Simulating pong response: {' '.join(f'{b:02X}' for b in pong_response)}")
        return pong_response

    def _generate_preset_dump_response(self, request_msg: bytes) -> Optional[bytes]:
        """Generate a fake preset dump response."""
        if len(request_msg) < 8:
            return None

        preset_type = request_msg[5]  # Should be 0 for FM
        program = request_msg[6]

        # Generate a fake dump response (00 22 77 0E <type> <program> <preset_data>)
        dump_response = [0xF0, 0x00, 0x22, 0x77, 0x0E, preset_type, program]

        # Add realistic FM preset data based on program number
        algorithm, feedback, lfo_ams, lfo_fms = self._generate_fm_parameters(program)
        dump_response.extend([algorithm, feedback, lfo_ams, lfo_fms])

        # Add 4 realistic operators
        dump_response.extend(self._generate_operators(program))
        dump_response.append(0xF7)

        response = bytes(dump_response)
        print(
            f"FakeMIDIInterface: Simulating dump response for program {program} "
            + f"(ALG:{algorithm}, FB:{feedback}): {' '.join(f'{b:02X}' for b in response)}"
        )
        return response

    def _generate_channel_dump_response(self, request_msg: bytes) -> Optional[bytes]:
        """Generate a fake channel dump response."""
        if len(request_msg) < 8:
            return None

        preset_type = request_msg[5]  # Should be 0 for FM
        midi_channel = request_msg[6]

        # Generate a fake channel dump response (00 22 77 10 <type> <midi_channel> <preset_data>)
        dump_response = [0xF0, 0x00, 0x22, 0x77, 0x10, preset_type, midi_channel]

        # Add realistic FM preset data based on MIDI channel number
        algorithm, feedback, lfo_ams, lfo_fms = self._generate_fm_parameters(midi_channel)
        dump_response.extend([algorithm, feedback, lfo_ams, lfo_fms])

        # Add 4 realistic operators
        dump_response.extend(self._generate_operators(midi_channel))
        dump_response.append(0xF7)

        response = bytes(dump_response)
        print(
            f"FakeMIDIInterface: Simulating channel dump response for MIDI channel {midi_channel} "
            + f"(ALG:{algorithm}, FB:{feedback}): {' '.join(f'{b:02X}' for b in response)}"
        )
        return response

    def _generate_fm_parameters(self, seed: int) -> tuple[int, int, int, int]:
        """Generate realistic FM parameters based on seed value."""
        algorithm = seed % 8  # Algorithm 0-7
        feedback = (seed * 3) % 8  # Feedback 0-7
        lfo_ams = seed % 4  # AMS 0-3
        lfo_fms = (seed * 5) % 8  # FMS 0-7
        return algorithm, feedback, lfo_ams, lfo_fms

    def _generate_operators(self, seed: int) -> List[int]:
        """Generate 4 realistic FM operators based on seed value."""
        operators = []
        for op_num in range(4):
            # Create variation based on seed and operator number
            base = (seed + op_num * 20) % 128

            # Realistic FM operator parameters
            mul = 1 + (base % 15)  # Multiple 1-15
            dt = base % 8  # Detune 0-7
            ar = 20 + (base % 12)  # Attack Rate 20-31 (reasonable range)
            rs = base % 4  # Rate Scaling 0-3
            dr = 8 + (base % 12)  # Decay Rate 8-19
            am = base % 2  # AM 0-1
            sl = base % 16  # Sustain Level 0-15
            sr = base % 16  # Sustain Rate 0-15
            rr = 5 + (base % 12)  # Release Rate 5-16
            tl = (base % 48) + (op_num * 12)  # Total Level 0-99, higher for higher operators
            ssg = 0 if base % 4 == 0 else (8 + (base % 8))  # SSG-EG: 0 or 8-15

            operators.extend([mul, dt, ar, rs, dr, am, sl, sr, rr, tl, ssg])

        return operators

    def get_last_sysex(self) -> Optional[bytes]:
        """Get the last sent SysEx message.

        Returns:
            Last SysEx message or None if no messages sent
        """
        if self.sent_messages:
            return self.sent_messages[-1]
        return None

    def clear_messages(self) -> None:
        """Clear all recorded messages."""
        self.sent_messages.clear()

    def close(self) -> None:
        """No-op for fake interface."""
        pass
