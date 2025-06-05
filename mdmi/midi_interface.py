"""MIDI interface abstraction for real and fake MIDI devices."""

from typing import List, Optional
import mido
import time


class MIDIInterface:
    """Real MIDI interface using mido."""

    def __init__(self, port_name: str, input_port_name: Optional[str] = None):
        """Initialize MIDI interface with specified port(s).

        Args:
            port_name: Name of the MIDI output port
            input_port_name: Name of the MIDI input port (optional, defaults to port_name)

        Raises:
            ValueError: If output port is not found
        """
        self.port_name = port_name
        self.input_port_name = input_port_name or port_name

        # Check if output port exists
        available_output_ports = mido.get_output_names()
        if port_name not in available_output_ports:
            raise ValueError(f"MIDI output port '{port_name}' not found. Available ports: {available_output_ports}")

        self.output_port = mido.open_output(port_name)

        # Try to open input port
        self.input_port = None
        available_input_ports = mido.get_input_names()
        if self.input_port_name in available_input_ports:
            self.input_port = mido.open_input(self.input_port_name)
        elif input_port_name is not None:
            # User explicitly specified an input port that doesn't exist
            raise ValueError(f"MIDI input port '{input_port_name}' not found. Available ports: {available_input_ports}")

    def send_sysex(self, data: bytes) -> None:
        """Send SysEx data to MIDI interface.

        Args:
            data: Complete SysEx message including F0/F7
        """
        # Convert bytes to mido SysEx message
        # Remove F0 start and F7 end bytes as mido adds them
        sysex_data = list(data[1:-1])
        msg = mido.Message("sysex", data=sysex_data)
        self.output_port.send(msg)

    def wait_for_sysex(self, timeout: float = 5.0) -> Optional[bytes]:
        """Wait for incoming SysEx message.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Complete SysEx message including F0/F7, or None if timeout
        """
        if not self.input_port:
            return None

        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check for incoming messages with a small timeout
            try:
                for msg in self.input_port.iter_pending():
                    if msg.type == "sysex":
                        # Reconstruct complete SysEx message with F0/F7
                        return bytes([0xF0] + list(msg.data) + [0xF7])

                # Small sleep to avoid busy waiting
                time.sleep(0.001)

            except Exception as e:
                print(f"Exception in wait_for_sysex: {e}")
                # Handle any MIDI errors gracefully
                break

        return None

    def close(self) -> None:
        """Close the MIDI ports."""
        if hasattr(self, "output_port") and self.output_port:
            self.output_port.close()
        if hasattr(self, "input_port") and self.input_port:
            self.input_port.close()

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()


class FakeMIDIInterface:
    """Fake MIDI interface for testing."""

    def __init__(self):
        """Initialize fake MIDI interface."""
        self.port_name = "Fake MIDI Interface"
        self.sent_messages: List[bytes] = []
        self.simulate_pong = True  # Whether to simulate pong responses

    def send_sysex(self, data: bytes) -> None:
        """Record SysEx data for testing.

        Args:
            data: Complete SysEx message including F0/F7
        """
        # Print the SysEx message for debugging
        hex_data = " ".join(f"{b:02X}" for b in data)
        print(f"FakeMIDIInterface: Sending SysEx ({len(data)} bytes): {hex_data}")

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
            # Return a pong response (00 22 77 02)
            pong_response = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
            print(f"FakeMIDIInterface: Simulating pong response: {' '.join(f'{b:02X}' for b in pong_response)}")
            return pong_response

        elif cmd == 0x0D:  # Dump request (00 22 77 0D <type> <program>)
            if len(last_msg) >= 8:
                preset_type = last_msg[5]  # Should be 0 for FM
                program = last_msg[6]

                # Generate a fake dump response (00 22 77 0E <type> <program> <preset_data>)
                dump_response = [0xF0, 0x00, 0x22, 0x77, 0x0E, preset_type, program]

                # Add realistic FM preset data based on program number
                # Use program number to create variation in the preset
                algorithm = program % 8  # Algorithm 0-7
                feedback = (program * 2) % 8  # Feedback 0-7
                lfo_ams = program % 4  # AMS 0-3
                lfo_fms = (program * 3) % 8  # FMS 0-7

                dump_response.extend([algorithm, feedback, lfo_ams, lfo_fms])

                # Add 4 realistic operators (11 bytes each)
                for op_num in range(4):
                    # Create variation based on program and operator number
                    base = (program + op_num * 10) % 128

                    # Realistic FM operator parameters
                    mul = 1 + (base % 15)  # Multiple 1-15
                    dt = base % 8  # Detune 0-7
                    ar = 15 + (base % 16)  # Attack Rate 15-31 (reasonable range)
                    rs = base % 4  # Rate Scaling 0-3
                    dr = 5 + (base % 16)  # Decay Rate 5-20
                    am = base % 2  # AM 0-1
                    sl = base % 16  # Sustain Level 0-15
                    sr = base % 16  # Sustain Rate 0-15
                    rr = 1 + (base % 16)  # Release Rate 1-16
                    tl = (base % 64) + (op_num * 16)  # Total Level 0-127, higher for higher operators
                    ssg = 0 if base % 3 == 0 else (8 + (base % 8))  # SSG-EG: 0 or 8-15

                    dump_response.extend([mul, dt, ar, rs, dr, am, sl, sr, rr, tl, ssg])

                dump_response.append(0xF7)
                dump_response = bytes(dump_response)

                print(
                    f"FakeMIDIInterface: Simulating dump response for program {program} "
                    + f"(ALG:{algorithm}, FB:{feedback}): {' '.join(f'{b:02X}' for b in dump_response)}"
                )
                return dump_response

        elif cmd == 0x0F:  # Channel dump request (00 22 77 0F <type> <midi_channel>)
            if len(last_msg) >= 8:
                preset_type = last_msg[5]  # Should be 0 for FM
                midi_channel = last_msg[6]

                # Generate a fake channel dump response (00 22 77 10 <type> <midi_channel> <preset_data>)
                dump_response = [0xF0, 0x00, 0x22, 0x77, 0x10, preset_type, midi_channel]

                # Add realistic FM preset data based on MIDI channel number
                # Use channel number to create variation in the preset
                algorithm = midi_channel % 8  # Algorithm 0-7
                feedback = (midi_channel * 3) % 8  # Feedback 0-7
                lfo_ams = midi_channel % 4  # AMS 0-3
                lfo_fms = (midi_channel * 5) % 8  # FMS 0-7

                dump_response.extend([algorithm, feedback, lfo_ams, lfo_fms])

                # Add 4 realistic operators (11 bytes each)
                for op_num in range(4):
                    # Create variation based on channel and operator number
                    base = (midi_channel + op_num * 20) % 128

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

                    dump_response.extend([mul, dt, ar, rs, dr, am, sl, sr, rr, tl, ssg])

                dump_response.append(0xF7)
                dump_response = bytes(dump_response)

                print(
                    f"FakeMIDIInterface: Simulating channel dump response for MIDI channel {midi_channel} "
                    + f"(ALG:{algorithm}, FB:{feedback}): {' '.join(f'{b:02X}' for b in dump_response)}"
                )
                return dump_response

        return None

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
