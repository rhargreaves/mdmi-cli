"""Tests for MIDI interface."""

import pytest
from unittest.mock import Mock, patch

from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


class TestMIDIInterface:
    """Tests for MIDI interface."""

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    @patch("mido.open_output")
    def test_real_midi_interface_init(self, mock_open_output, mock_output_names, mock_input_names):
        """Test real MIDI interface initialization."""
        mock_output_names.return_value = ["Test Port"]
        mock_input_names.return_value = []  # No input ports available
        mock_port = Mock()
        mock_open_output.return_value = mock_port

        interface = MIDIInterface("Test Port")

        assert interface.port_name == "Test Port"
        assert interface.input_port_name == "Test Port"  # Defaults to output port name
        assert interface.input_port is None  # No input port available
        mock_open_output.assert_called_once_with("Test Port")

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    @patch("mido.open_input")
    @patch("mido.open_output")
    def test_real_midi_interface_with_separate_input(
        self, mock_open_output, mock_open_input, mock_output_names, mock_input_names
    ):
        """Test real MIDI interface initialization with separate input port."""
        mock_output_names.return_value = ["Test Out Port"]
        mock_input_names.return_value = ["Test In Port"]
        mock_output_port = Mock()
        mock_input_port = Mock()
        mock_open_output.return_value = mock_output_port
        mock_open_input.return_value = mock_input_port

        interface = MIDIInterface("Test Out Port", "Test In Port")

        assert interface.port_name == "Test Out Port"
        assert interface.input_port_name == "Test In Port"
        assert interface.input_port is not None
        mock_open_output.assert_called_once_with("Test Out Port")
        mock_open_input.assert_called_once_with("Test In Port")

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    def test_real_midi_interface_invalid_output_port(self, mock_output_names, mock_input_names):
        """Test real MIDI interface with invalid output port."""
        mock_output_names.return_value = ["Other Port"]
        mock_input_names.return_value = []

        with pytest.raises(ValueError, match="MIDI output port 'Invalid' not found"):
            MIDIInterface("Invalid")

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    @patch("mido.open_output")
    def test_real_midi_interface_invalid_input_port(self, mock_open_output, mock_output_names, mock_input_names):
        """Test real MIDI interface with invalid input port."""
        mock_output_names.return_value = ["Test Port"]
        mock_input_names.return_value = ["Other Port"]
        mock_port = Mock()
        mock_open_output.return_value = mock_port

        with pytest.raises(ValueError, match="MIDI input port 'Invalid Input' not found"):
            MIDIInterface("Test Port", "Invalid Input")

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    @patch("mido.open_output")
    def test_send_sysex(self, mock_open_output, mock_output_names, mock_input_names):
        """Test sending SysEx message."""
        mock_output_names.return_value = ["Test Port"]
        mock_input_names.return_value = []
        mock_port = Mock()
        mock_open_output.return_value = mock_port

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
