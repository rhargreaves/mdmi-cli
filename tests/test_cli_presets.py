"""Tests for preset-related CLI functionality."""

from unittest.mock import Mock, patch
from click.testing import CliRunner

from mdmi.cli import main


class TestCLIPresets:
    """Tests for preset-related CLI commands."""

    def test_load_preset_help(self):
        """Test load-preset command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "--help"])

        assert result.exit_code == 0
        assert "Load a preset file to MDMI" in result.output
        assert "MDMI_MIDI_OUT" in result.output

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
    @patch("mdmi.commands.common.FakeMidiInterface")
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
    @patch("mdmi.commands.common.FakeMidiInterface")
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
    @patch("mdmi.commands.common.MidoMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
    def test_clear_preset_fake_interface(self, mock_fake_midi):
        """Test clearing preset with fake interface."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-preset", "--program", "5", "--dry-run"])

        assert result.exit_code == 0
        assert "Successfully cleared preset 5" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
    def test_clear_all_presets_with_confirm(self, mock_fake_midi):
        """Test clearing all presets with --confirm flag."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--dry-run", "--confirm"])

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
    def test_clear_all_presets_with_user_confirmation(self, mock_fake_midi):
        """Test clearing all presets with user confirmation."""
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["clear-all-presets", "--dry-run"], input="y\n")

        assert result.exit_code == 0
        assert "Successfully cleared all presets" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.commands.common.FakeMidiInterface")
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
