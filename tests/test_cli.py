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

    @patch("mdmi.cli.Path.exists")
    def test_load_preset_file_not_found(self, mock_exists):
        """Test load-preset with non-existent file."""
        mock_exists.return_value = False

        runner = CliRunner()
        result = runner.invoke(
            main, ["load-preset", "nonexistent.tfi", "--channel", "0"]
        )

        assert result.exit_code != 0
        assert "does not exist" in result.output

    @patch("mdmi.cli.Path.exists")
    @patch("mdmi.cli.Path.read_bytes")
    @patch("mdmi.cli.detect_preset_format")
    @patch("mdmi.cli.FakeMIDIInterface")
    def test_load_preset_tfi_fake_interface(
        self, mock_fake_midi, mock_detect, mock_read, mock_exists
    ):
        """Test loading TFI preset with fake interface."""
        # Setup mocks
        mock_exists.return_value = True
        mock_read.return_value = b"\x00" * 42  # Valid TFI data
        mock_detect.return_value = "TFI"
        mock_interface = Mock()
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(
            main, ["load-preset", "test.tfi", "--channel", "0", "--fake"]
        )

        assert result.exit_code == 0
        assert "Successfully loaded" in result.output
        mock_interface.send_sysex.assert_called_once()

    @patch("mdmi.cli.Path.exists")
    @patch("mdmi.cli.Path.read_bytes")
    @patch("mdmi.cli.detect_preset_format")
    @patch("mido.get_output_names")
    @patch("mdmi.cli.MIDIInterface")
    def test_load_preset_real_interface(
        self, mock_midi, mock_ports, mock_detect, mock_read, mock_exists
    ):
        """Test loading preset with real MIDI interface."""
        # Setup mocks
        mock_exists.return_value = True
        mock_read.return_value = b"\x00" * 42
        mock_detect.return_value = "TFI"
        mock_ports.return_value = ["Test Port"]
        mock_interface = Mock()
        mock_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(
            main, ["load-preset", "test.tfi", "--channel", "0", "--port", "Test Port"]
        )

        assert result.exit_code == 0
        mock_interface.send_sysex.assert_called_once()

    def test_load_preset_invalid_channel(self):
        """Test load-preset with invalid channel."""
        runner = CliRunner()
        result = runner.invoke(main, ["load-preset", "test.tfi", "--channel", "10"])

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
        result = runner.invoke(
            main, ["load-preset", "test.unknown", "--channel", "0", "--fake"]
        )

        assert result.exit_code != 0
        assert "Unsupported" in result.output
