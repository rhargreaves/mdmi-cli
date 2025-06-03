"""Tests for CLI."""

from unittest.mock import Mock, patch
from click.testing import CliRunner

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

    @patch("mido.get_output_names")
    def test_list_ports_without_preset_file(self, mock_get_ports):
        """Test list-ports command works properly."""
        mock_get_ports.return_value = ["Test Port 1", "Test Port 2"]

        runner = CliRunner()
        result = runner.invoke(main, ["list-ports"])

        assert result.exit_code == 0
        assert "Available MIDI output ports:" in result.output
        assert "Test Port 1" in result.output
        assert "Test Port 2" in result.output
        mock_get_ports.assert_called_once()

    @patch("mido.get_output_names")
    def test_list_ports_no_ports_available(self, mock_get_ports):
        """Test list-ports command when no ports are available."""
        mock_get_ports.return_value = []

        runner = CliRunner()
        result = runner.invoke(main, ["list-ports"])

        assert result.exit_code == 0
        assert "No MIDI output ports found" in result.output
        mock_get_ports.assert_called_once()

    def test_load_preset_without_arguments_shows_error(self):
        """Test that load-preset without arguments shows proper error."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset"])

        assert result.exit_code != 0
        assert "PRESET_FILE is required" in result.output

    def test_load_preset_without_program_shows_error(self):
        """Test that load-preset without program shows proper error."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "test.tfi"])

        assert result.exit_code != 0
        assert "--program is required" in result.output

    @patch("mdmi.cli.Path.exists")
    def test_load_preset_file_not_found(self, mock_exists):
        """Test load-preset with non-existent file."""
        mock_exists.return_value = False

        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "nonexistent.tfi", "--program", "0"])

        assert result.exit_code != 0
        assert "does not exist" in result.output

    @patch("mdmi.cli.Path.exists")
    @patch("mdmi.cli.Path.read_bytes")
    @patch("mdmi.cli.detect_preset_format")
    @patch("mdmi.cli.FakeMIDIInterface")
    def test_load_preset_tfi_fake_interface(self, mock_fake_midi, mock_detect, mock_read, mock_exists):
        """Test loading TFI preset with fake interface."""
        # Setup mocks
        mock_exists.return_value = True
        mock_read.return_value = b"\x00" * 42  # Valid TFI data
        mock_detect.return_value = "TFI"
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "test.tfi", "--program", "0", "--fake"])

        assert result.exit_code == 0
        assert "Successfully loaded" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.cli.Path.exists")
    @patch("mdmi.cli.Path.read_bytes")
    @patch("mdmi.cli.detect_preset_format")
    @patch("mido.get_output_names")
    @patch("mdmi.cli.MIDIInterface")
    def test_load_preset_real_interface(self, mock_midi, mock_ports, mock_detect, mock_read, mock_exists):
        """Test loading preset with real MIDI interface."""
        # Setup mocks
        mock_exists.return_value = True
        mock_read.return_value = b"\x00" * 42
        mock_detect.return_value = "TFI"
        mock_ports.return_value = ["Test Port"]
        mock_interface = Mock()
        mock_midi.return_value = mock_interface

        runner = CliRunner()
        args = ["load-preset", "test.tfi", "--program", "0", "--port", "Test Port"]
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

    @patch("mdmi.cli.Path.exists")
    @patch("mdmi.cli.Path.read_bytes")
    @patch("mdmi.cli.detect_preset_format")
    def test_load_preset_unsupported_format(self, mock_detect, mock_read, mock_exists):
        """Test load-preset with unsupported format."""
        mock_exists.return_value = True
        mock_read.return_value = b"invalid"
        mock_detect.return_value = "UNKNOWN"

        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "test.unknown", "--program", "0", "--fake"])

        assert result.exit_code != 0
        assert "Unsupported" in result.output

    def test_clear_preset_help(self):
        """Test clear-preset command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset", "--help"])

        assert result.exit_code == 0
        assert "Clear a specific user preset" in result.output

    @patch("mdmi.cli.FakeMIDIInterface")
    def test_clear_preset_fake_interface(self, mock_fake_midi):
        """Test clearing preset with fake interface."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset", "--program", "5", "--fake"])

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

    @patch("mdmi.cli.FakeMIDIInterface")
    def test_clear_all_presets_with_confirm(self, mock_fake_midi):
        """Test clearing all presets with --confirm flag."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--fake", "--confirm"])

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.cli.FakeMIDIInterface")
    def test_clear_all_presets_with_user_confirmation(self, mock_fake_midi):
        """Test clearing all presets with user confirmation."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--fake"], input="y\n")

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.cli.FakeMIDIInterface")
    def test_clear_all_presets_user_aborts(self, mock_fake_midi):
        """Test clearing all presets when user aborts."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--fake"], input="n\n")

        assert result.exit_code != 0
        mock_interface.send_sysex.assert_not_called()
