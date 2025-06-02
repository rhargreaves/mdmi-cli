"""Tests for MIDI interface."""

import pytest
from unittest.mock import Mock, patch

from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


class TestMIDIInterface:
    """Tests for MIDI interface."""

    @patch("mido.get_output_names")
    @patch("mido.open_output")
    def test_real_midi_interface_init(self, mock_open, mock_names):
        """Test real MIDI interface initialization."""
        mock_names.return_value = ["Test Port"]
        mock_port = Mock()
        mock_open.return_value = mock_port

        interface = MIDIInterface("Test Port")

        assert interface.port_name == "Test Port"
        mock_open.assert_called_once_with("Test Port")

    @patch("mido.get_output_names")
    def test_real_midi_interface_invalid_port(self, mock_names):
        """Test real MIDI interface with invalid port."""
        mock_names.return_value = ["Other Port"]

        with pytest.raises(ValueError, match="MIDI port 'Invalid' not found"):
            MIDIInterface("Invalid")

    @patch("mido.get_output_names")
    @patch("mido.open_output")
    def test_send_sysex(self, mock_open, mock_names):
        """Test sending SysEx message."""
        mock_names.return_value = ["Test Port"]
        mock_port = Mock()
        mock_open.return_value = mock_port

        interface = MIDIInterface("Test Port")
        sysex_data = b"\xf0\x43\x76\x10\x00\x42\xf7"

        interface.send_sysex(sysex_data)

        mock_port.send.assert_called_once()
        sent_msg = mock_port.send.call_args[0][0]
        assert sent_msg.type == "sysex"
        assert bytes(sent_msg.data) == sysex_data[1:-1]  # Exclude F0/F7


class TestFakeMIDIInterface:
    """Tests for fake MIDI interface."""

    def test_fake_midi_interface_init(self):
        """Test fake MIDI interface initialization."""
        interface = FakeMIDIInterface()

        assert interface.port_name == "Fake MIDI Interface"
        assert interface.sent_messages == []

    def test_fake_send_sysex(self):
        """Test sending SysEx to fake interface."""
        interface = FakeMIDIInterface()
        sysex_data = b"\xf0\x43\x76\x10\x00\x42\xf7"

        interface.send_sysex(sysex_data)

        assert len(interface.sent_messages) == 1
        assert interface.sent_messages[0] == sysex_data

    def test_fake_get_last_sysex(self):
        """Test getting last SysEx message from fake interface."""
        interface = FakeMIDIInterface()

        # Send multiple messages
        sysex1 = b"\xf0\x43\x76\x10\x00\x42\xf7"
        sysex2 = b"\xf0\x43\x76\x10\x01\x43\xf7"

        interface.send_sysex(sysex1)
        interface.send_sysex(sysex2)

        assert interface.get_last_sysex() == sysex2

    def test_fake_get_last_sysex_empty(self):
        """Test getting last SysEx when no messages sent."""
        interface = FakeMIDIInterface()

        assert interface.get_last_sysex() is None

    def test_fake_clear_messages(self):
        """Test clearing sent messages."""
        interface = FakeMIDIInterface()
        interface.send_sysex(b"\xf0\x43\x76\x10\x00\x42\xf7")

        interface.clear_messages()

        assert interface.sent_messages == []
        assert interface.get_last_sysex() is None
