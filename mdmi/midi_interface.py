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
                        return bytes([0xF0] + msg.data + [0xF7])

                # Small sleep to avoid busy waiting
                time.sleep(0.001)

            except Exception:
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
            Simulated pong response if last sent message was a ping
        """
        if not self.simulate_pong:
            return None

        # Check if the last sent message was a ping (00 22 77 01)
        if self.sent_messages and len(self.sent_messages[-1]) >= 6:
            last_msg = self.sent_messages[-1]
            if last_msg[0] == 0xF0 and last_msg[1:5] == bytes([0x00, 0x22, 0x77, 0x01]) and last_msg[-1] == 0xF7:
                # Simulate a small delay
                time.sleep(0.01)

                # Return a pong response (00 22 77 02)
                pong_response = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
                print(f"FakeMIDIInterface: Simulating pong response: {' '.join(f'{b:02X}' for b in pong_response)}")
                return pong_response

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
