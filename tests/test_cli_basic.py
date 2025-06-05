"""Tests for basic CLI functionality."""

from unittest.mock import patch
from click.testing import CliRunner
import io
from contextlib import redirect_stdout

from mdmi.cli import main


class TestCLIBasic:
    """Tests for basic CLI commands."""

    def test_main_help(self):
        """Test main command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Mega Drive MIDI Interface CLI" in result.output

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    def test_list_ports_without_preset_file(self, mock_get_output_ports, mock_get_input_ports):
        """Test list-ports command works properly."""
        mock_get_output_ports.return_value = ["Test Port 1", "Test Port 2"]
        mock_get_input_ports.return_value = ["Input Port 1", "Input Port 2"]

        runner = CliRunner()
        result = runner.invoke(main, ["list-ports"])

        assert result.exit_code == 0
        assert "📤 Output ports (for sending to MDMI):" in result.output
        assert "📥 Input ports (for receiving from MDMI):" in result.output
        assert "Test Port 1" in result.output
        assert "Test Port 2" in result.output
        assert "Input Port 1" in result.output
        assert "Input Port 2" in result.output
        mock_get_output_ports.assert_called_once()
        mock_get_input_ports.assert_called_once()

    @patch("mido.get_input_names")
    @patch("mido.get_output_names")
    def test_list_ports_no_ports_available(self, mock_get_output_ports, mock_get_input_ports):
        """Test list-ports command when no ports are available."""
        mock_get_output_ports.return_value = []
        mock_get_input_ports.return_value = []

        runner = CliRunner()
        result = runner.invoke(main, ["list-ports"])

        assert result.exit_code == 0
        assert "(No MIDI output ports found)" in result.output
        assert "(No MIDI input ports found)" in result.output
        mock_get_output_ports.assert_called_once()
        mock_get_input_ports.assert_called_once()

    def test_list_ports_updated_format(self):
        """Test that list-ports shows the new format with input and output ports."""
        runner = CliRunner()
        with patch("mido.get_output_names") as mock_output, patch("mido.get_input_names") as mock_input:
            mock_output.return_value = ["Output Port 1", "Output Port 2"]
            mock_input.return_value = ["Input Port 1", "Input Port 2"]

            result = runner.invoke(main, ["list-ports"])

        assert result.exit_code == 0
        assert "📤 Output ports (for sending to MDMI):" in result.output
        assert "📥 Input ports (for receiving from MDMI):" in result.output
        assert "Output Port 1" in result.output
        assert "Input Port 1" in result.output
        assert "MDMI_MIDI_OUT" in result.output
        assert "MDMI_MIDI_IN" in result.output
        assert "MDMI_MIDI_PORT" in result.output

    def test_fake_interface_debug_output(self):
        """Test that FakeMidiInterface prints SysEx debug information."""
        from mdmi.fake_midi_interface import FakeMidiInterface

        # Create a fake interface
        fake_interface = FakeMidiInterface()

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # Send a test SysEx message
            test_sysex = bytes([0xF0, 0x00, 0x22, 0x77, 0x0A, 0x00, 0x2A, 0xF7])  # Program 42 (0x2A)
            fake_interface.send_sysex(test_sysex)

        # Get the captured output
        output = captured_output.getvalue()

        # Verify debug output format
        assert "FakeMidiInterface: Sending SysEx" in output
        assert "8 bytes" in output  # Our test message is 8 bytes
        assert "F0 00 22 77 0A 00 2A F7" in output

        # Verify the message was also stored
        assert fake_interface.get_last_sysex() == test_sysex
