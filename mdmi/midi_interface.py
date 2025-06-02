"""MIDI interface abstraction for real and fake MIDI devices."""

from typing import List, Optional
import mido


class MIDIInterface:
    """Real MIDI interface using mido."""

    def __init__(self, port_name: str):
        """Initialize MIDI interface with specified port.

        Args:
            port_name: Name of the MIDI output port

        Raises:
            ValueError: If port is not found
        """
        self.port_name = port_name

        # Check if port exists
        available_ports = mido.get_output_names()
        if port_name not in available_ports:
            raise ValueError(
                f"MIDI port '{port_name}' not found. "
                f"Available ports: {available_ports}"
            )

        self.port = mido.open_output(port_name)

    def send_sysex(self, data: bytes) -> None:
        """Send SysEx data to MIDI interface.

        Args:
            data: Complete SysEx message including F0/F7
        """
        # Convert bytes to mido SysEx message
        # Remove F0 start and F7 end bytes as mido adds them
        sysex_data = list(data[1:-1])
        msg = mido.Message("sysex", data=sysex_data)
        self.port.send(msg)

    def close(self) -> None:
        """Close the MIDI port."""
        if hasattr(self, "port") and self.port:
            self.port.close()

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()


class FakeMIDIInterface:
    """Fake MIDI interface for testing."""

    def __init__(self):
        """Initialize fake MIDI interface."""
        self.port_name = "Fake MIDI Interface"
        self.sent_messages: List[bytes] = []

    def send_sysex(self, data: bytes) -> None:
        """Record SysEx data for testing.

        Args:
            data: Complete SysEx message including F0/F7
        """
        self.sent_messages.append(data)

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
