"""Tests for CLI."""

from unittest.mock import Mock, patch
from click.testing import CliRunner
import io
from contextlib import redirect_stdout

from mdmi.cli import main


class TestCLI:
    """Tests for CLI commands."""

    def test_main_help(self):
        """Test main command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Mega Drive MIDI Interface CLI" in result.output

    def test_load_preset_help(self):
        """Test load-preset command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "--help"])

        assert result.exit_code == 0
        assert "Load a preset file to MDMI" in result.output
        assert "MDMI_MIDI_OUT" in result.output

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

    def test_load_preset_without_arguments_shows_error(self):
        """Test that load-preset without arguments shows proper error."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_load_preset_without_program_shows_error(self):
        """Test that load-preset without program shows proper error."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "tests/data/sample.tfi"])

        assert result.exit_code != 0
        assert "Missing option" in result.output

    def test_load_preset_file_not_found(self):
        """Test load-preset with non-existent file."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "nonexistent.tfi", "--program", "0"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    @patch("pathlib.Path.read_bytes")
    @patch("mdmi.preset_parsers.detect_preset_format")
    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_load_preset_tfi_fake_interface(self, mock_fake_midi, mock_detect, mock_read):
        """Test loading TFI preset with fake interface."""
        # Setup mocks
        mock_read.return_value = b"\x00" * 42  # Valid TFI data
        mock_detect.return_value = "TFI"
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "tests/data/sample.tfi", "--program", "0", "--dry-run"])

        assert result.exit_code == 0
        assert "Successfully loaded" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("pathlib.Path.read_bytes")
    @patch("mdmi.preset_parsers.detect_preset_format")
    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_load_preset_with_env_port(self, mock_fake_midi, mock_detect, mock_read):
        """Test loading preset using MDMI_MIDI_PORT environment variable."""
        # Setup mocks
        mock_read.return_value = b"\x00" * 42  # Valid TFI data
        mock_detect.return_value = "TFI"
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        # Set environment variable
        env = {"MDMI_MIDI_PORT": "Env Test Port"}
        runner = CliRunner(env=env)

        # Don't specify --port, should use environment variable
        result = runner.invoke(main, ["load-preset", "tests/data/sample.tfi", "--program", "0", "--dry-run"])

        assert result.exit_code == 0
        assert "Successfully loaded" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("pathlib.Path.read_bytes")
    @patch("mdmi.preset_parsers.detect_preset_format")
    @patch("mido.get_output_names")
    @patch("mdmi.commands.common.MIDIInterface")
    def test_load_preset_real_interface(self, mock_midi, mock_ports, mock_detect, mock_read):
        """Test loading preset with real MIDI interface."""
        # Setup mocks
        mock_read.return_value = b"\x00" * 42
        mock_detect.return_value = "TFI"
        mock_ports.return_value = ["Test Port"]
        mock_interface = Mock()
        mock_midi.return_value = mock_interface

        runner = CliRunner()
        args = ["load-preset", "tests/data/sample.tfi", "--program", "0", "--midi-out", "Test Port"]
        result = runner.invoke(main, args)

        assert result.exit_code == 0
        mock_interface.send_sysex.assert_called_once()

    def test_load_preset_invalid_program(self):
        """Test load-preset with invalid program."""
        runner = CliRunner()
        args = ["load-preset", "test.tfi", "--program", "128"]
        result = runner.invoke(main, args)

        assert result.exit_code != 0
        assert "Invalid value for" in result.output

    @patch("pathlib.Path.read_bytes")
    @patch("mdmi.preset_parsers.detect_preset_format")
    def test_load_preset_unsupported_format(self, mock_detect, mock_read):
        """Test load-preset with unsupported format."""
        mock_read.return_value = b"invalid"
        mock_detect.return_value = "UNKNOWN"

        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "tests/data/sample.tfi", "--program", "0", "--dry-run"])

        assert result.exit_code != 0
        assert "Unsupported" in result.output

    def test_clear_preset_help(self):
        """Test clear-preset command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset", "--help"])

        assert result.exit_code == 0
        assert "Clear a specific user preset" in result.output
        assert "MDMI_MIDI_OUT" in result.output

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_preset_fake_interface(self, mock_fake_midi):
        """Test clearing preset with fake interface."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset", "--program", "5", "--dry-run"])

        assert result.exit_code == 0
        assert "Successfully cleared preset 5" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_preset_with_env_port(self, mock_fake_midi):
        """Test clearing preset using MDMI_MIDI_PORT environment variable."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        # Set environment variable
        env = {"MDMI_MIDI_PORT": "Env Test Port"}
        runner = CliRunner(env=env)

        result = runner.invoke(main, ["clear-preset", "--program", "5", "--dry-run"])

        assert result.exit_code == 0
        assert "Successfully cleared preset 5" in result.output
        mock_interface.send_sysex.assert_called_once()

    def test_clear_preset_without_program_shows_error(self):
        """Test that clear-preset without program shows proper error."""
        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset"])

        assert result.exit_code != 0
        assert "--program" in result.output

    def test_clear_all_presets_help(self):
        """Test clear-all-presets command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--help"])

        assert result.exit_code == 0
        assert "Clear all user presets" in result.output
        assert "MDMI_MIDI_OUT" in result.output

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_all_presets_with_confirm(self, mock_fake_midi):
        """Test clearing all presets with --confirm flag."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--dry-run", "--confirm"])

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_all_presets_with_env_port(self, mock_fake_midi):
        """Test clearing all presets using MDMI_MIDI_PORT environment variable."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        # Set environment variable
        env = {"MDMI_MIDI_PORT": "Env Test Port"}
        runner = CliRunner(env=env)

        result = runner.invoke(main, ["clear-all-presets", "--dry-run", "--confirm"])

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_all_presets_with_user_confirmation(self, mock_fake_midi):
        """Test clearing all presets with user confirmation."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--dry-run"], input="y\n")

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_clear_all_presets_user_aborts(self, mock_fake_midi):
        """Test clearing all presets when user aborts."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--dry-run"], input="n\n")

        assert result.exit_code != 0
        mock_interface.send_sysex.assert_not_called()

    def test_list_wopn_command(self):
        """Test list-wopn command with limited display (default)."""
        runner = CliRunner()
        result = runner.invoke(main, ["list-wopn", "tests/data/sample.wopn"])

        assert result.exit_code == 0
        assert "WOPN File: tests/data/sample.wopn" in result.output
        assert "Melody Banks:" in result.output
        assert "Standard :3" in result.output
        assert "GrandPiano" in result.output
        # Should show truncation message for banks with >10 instruments
        assert "... and" in result.output
        assert "more (use --full to see all)" in result.output

    def test_list_wopn_command_full(self):
        """Test list-wopn command with --full option."""
        runner = CliRunner()
        result_default = runner.invoke(main, ["list-wopn", "tests/data/sample.wopn"])
        result_full = runner.invoke(main, ["list-wopn", "tests/data/sample.wopn", "--full"])

        assert result_full.exit_code == 0
        assert "WOPN File: tests/data/sample.wopn" in result_full.output
        assert "Melody Banks:" in result_full.output
        assert "Standard :3" in result_full.output
        assert "GrandPiano" in result_full.output

        # Full output should be longer than default output
        assert len(result_full.output) > len(result_default.output)

        # Full output should not have truncation message
        assert "... and" not in result_full.output or "more (use --full to see all)" not in result_full.output

    def test_list_wopn_help(self):
        """Test list-wopn command help includes --full option."""
        runner = CliRunner()
        result = runner.invoke(main, ["list-wopn", "--help"])

        assert result.exit_code == 0
        assert "List contents of a WOPN file" in result.output
        assert "--full" in result.output
        assert "Show all instruments" in result.output

    def test_fake_interface_debug_output(self):
        """Test that FakeMIDIInterface prints SysEx debug information."""
        from mdmi.midi_interface import FakeMIDIInterface

        # Create a fake interface
        fake_interface = FakeMIDIInterface()

        # Capture stdout
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # Send a test SysEx message
            test_sysex = bytes([0xF0, 0x00, 0x22, 0x77, 0x0A, 0x00, 0x2A, 0xF7])  # Program 42 (0x2A)
            fake_interface.send_sysex(test_sysex)

        # Get the captured output
        output = captured_output.getvalue()

        # Verify debug output format
        assert "FakeMIDIInterface: Sending SysEx" in output
        assert "8 bytes" in output  # Our test message is 8 bytes
        assert "F0 00 22 77 0A 00 2A F7" in output

        # Verify the message was also stored
        assert fake_interface.get_last_sysex() == test_sysex

    def test_ping_help(self):
        """Test ping command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["ping", "--help"])

        assert result.exit_code == 0
        assert "Send a ping to MDMI and measure round-trip latency" in result.output
        assert "--timeout" in result.output
        assert "--midi-in" in result.output
        assert "MDMI_MIDI_OUT" in result.output
        assert "MDMI_MIDI_IN" in result.output

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_ping_fake_interface_success(self, mock_fake_midi):
        """Test ping command with successful fake interface response."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["ping", "--dry-run"])

        assert result.exit_code == 0
        assert "Sending ping to Fake MIDI Interface" in result.output
        assert "✅ Pong received!" in result.output
        assert "Round-trip latency:" in result.output
        assert "ms" in result.output

        # Verify ping SysEx was sent
        mock_interface.send_sysex.assert_called_once()
        sent_ping = mock_interface.send_sysex.call_args[0][0]
        expected_ping = bytes([0xF0, 0x00, 0x22, 0x77, 0x01, 0xF7])
        assert sent_ping == expected_ping

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_ping_fake_interface_timeout(self, mock_fake_midi):
        """Test ping command with timeout (no pong response)."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = None  # Timeout
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["ping", "--dry-run", "--timeout", "0.1"])

        assert result.exit_code != 0
        assert "❌ No pong response received" in result.output
        assert "MDMI is not connected" in result.output

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_ping_fake_interface_wrong_response(self, mock_fake_midi):
        """Test ping command with unexpected response."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        # Return unexpected response
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x99, 0xF7])
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["ping", "--dry-run"])

        assert result.exit_code != 0
        assert "❌ Unexpected response:" in result.output
        assert "F0 00 22 77 99 F7" in result.output
        assert "Expected pong: F0 00 22 77 02 F7" in result.output

    @patch("mdmi.commands.common.FakeMIDIInterface")
    def test_ping_with_custom_timeout(self, mock_fake_midi):
        """Test ping command with custom timeout value."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["ping", "--dry-run", "--timeout", "2.5"])

        assert result.exit_code == 0
        assert "timeout: 2.5s" in result.output
        # Verify the timeout was passed to wait_for_sysex
        mock_interface.wait_for_sysex.assert_called_once_with(2.5)

    def test_ping_with_environment_variables(self):
        """Test ping command with environment variables."""
        runner = CliRunner()
        env = {"MDMI_MIDI_OUT": "Test Out Port", "MDMI_MIDI_IN": "Test In Port"}
        result = runner.invoke(main, ["ping", "--dry-run"], env=env)

        assert result.exit_code == 0
        assert "✅ Pong received!" in result.output

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
