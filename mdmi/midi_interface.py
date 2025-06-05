"""MIDI interface protocol definition."""

from typing import Protocol, Optional


class MidiInterface(Protocol):
    """Protocol defining the contract for MIDI interfaces.

    Both real and mock MIDI interfaces must implement these methods.
    """

    port_name: str

    def send_sysex(self, data: bytes) -> None:
        """Send SysEx data to the interface.

        Args:
            data: Complete SysEx message including F0/F7
        """
        ...

    def wait_for_sysex(self, timeout: float = 5.0) -> Optional[bytes]:
        """Wait for incoming SysEx message.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            Complete SysEx message including F0/F7, or None if timeout
        """
        ...

    def close(self) -> None:
        """Close the MIDI interface and clean up resources."""
        ...
