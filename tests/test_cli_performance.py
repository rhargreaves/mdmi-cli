"""Tests for performance-related CLI functionality."""

from unittest.mock import Mock, patch
from click.testing import CliRunner

from mdmi.cli import main


def setup_virtual_clock():
    """Set up a virtual clock for performance tests that don't rely on real time."""
    virtual_time = [0.0]

    def time_side_effect():
        return virtual_time[0]

    def sleep_side_effect(duration):
        virtual_time[0] += duration

    return time_side_effect, sleep_side_effect


class TestCLIPing:
    """Tests for ping command."""

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

    @patch("mdmi.commands.common.FakeMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
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

    @patch("mdmi.commands.common.FakeMidiInterface")
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


class TestCLIPerfTest:
    """Tests for perf-test command."""

    def test_perf_test_help(self):
        """Test perf-test command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--help"])

        assert result.exit_code == 0
        assert "Continuously test MDMI ping/pong latency" in result.output
        assert "--duration" in result.output
        assert "--interval" in result.output
        assert "--hist-filename" in result.output
        assert "--timeout" in result.output
        assert "Press Ctrl+C to stop" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("time.sleep")  # Mock sleep to avoid delays
    @patch("time.time")  # Mock time for virtual clock
    def test_perf_test_with_duration(self, mock_time, mock_sleep, mock_close, mock_savefig, mock_fake_midi):
        """Test perf-test command with duration limit."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Set up virtual clock for fast testing
        time_side_effect, sleep_side_effect = setup_virtual_clock()
        mock_time.side_effect = time_side_effect
        mock_sleep.side_effect = sleep_side_effect

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.5", "--interval", "0.1"])

        assert result.exit_code == 0
        assert "Starting performance test" in result.output
        assert "Test duration: 0.5 seconds" in result.output
        assert "📊 Performance Test Complete" in result.output
        assert "Success rate: 100.0%" in result.output
        assert "Minimum:" in result.output
        assert "Maximum:" in result.output
        assert "Average:" in result.output
        assert "Median:" in result.output
        assert "📊 Histogram saved to:" in result.output

        # Verify histogram was generated
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

        # Should have sent 5 pings (0.5 seconds / 0.1 interval = 5)
        assert mock_interface.send_sysex.call_count == 5

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_custom_options(self, mock_time, mock_sleep, mock_close, mock_savefig, mock_fake_midi):
        """Test perf-test command with custom options."""
        mock_interface = Mock()
        mock_interface.port_name = "Test Port"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "perf-test",
                "--dry-run",
                "--duration",
                "0.3",
                "--interval",
                "0.05",
                "--timeout",
                "1.5",
                "--hist-filename",
                "custom_test.png",
            ],
        )

        assert result.exit_code == 0
        assert "Test duration: 0.3 seconds" in result.output
        assert "Ping interval: 0.05 seconds" in result.output
        assert "Individual timeout: 1.5 seconds" in result.output
        assert "custom_test.png" in result.output

        # Verify timeout was passed correctly
        for call in mock_interface.wait_for_sysex.call_args_list:
            assert call[0][0] == 1.5

        # Should have sent 6 pings (0.3 seconds / 0.05 interval = 6)
        assert mock_interface.send_sysex.call_count == 6

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_with_failed_pings(self, mock_time, mock_sleep, mock_fake_midi):
        """Test perf-test command with some failed pings."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        # Create alternating success/failure responses (6 pings total)
        success_response = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        responses = [
            success_response,  # Success
            None,  # Failure
            success_response,  # Success
            None,  # Failure
            success_response,  # Success
            None,  # Failure
        ]
        mock_interface.wait_for_sysex.side_effect = responses
        mock_fake_midi.return_value = mock_interface

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.3", "--interval", "0.05"])

        assert result.exit_code == 0
        assert "Failed pings: 3" in result.output
        assert "Successful pings: 3" in result.output
        assert "Success rate: 50.0%" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_all_failed_pings(self, mock_time, mock_sleep, mock_fake_midi):
        """Test perf-test command when all pings fail."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = None  # All timeouts
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.2", "--interval", "0.05"])

        assert result.exit_code == 0
        assert "Failed pings: 4" in result.output  # 0.2 / 0.05 = 4 pings
        assert "Successful pings: 0" in result.output
        assert "❌ No successful pings recorded - cannot generate histogram" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_with_separate_input_port(self, mock_time, mock_sleep, mock_close, mock_savefig, mock_fake_midi):
        """Test perf-test command with separate input port."""
        mock_interface = Mock()
        mock_interface.port_name = "Test Output Port"
        mock_interface.input_port_name = "Test Input Port"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "perf-test",
                "--dry-run",
                "--duration",
                "0.2",
                "--midi-out",
                "Test Output Port",
                "--midi-in",
                "Test Input Port",
            ],
        )

        assert result.exit_code == 0
        assert "Starting performance test on Test Output Port" in result.output
        assert "Listening for responses on Test Input Port" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_statistics_calculation(self, mock_time, mock_sleep, mock_close, mock_savefig, mock_fake_midi):
        """Test that performance statistics are calculated correctly."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.5", "--interval", "0.05"])

        assert result.exit_code == 0

        # Check that all required statistics are present
        assert "📈 Latency Statistics:" in result.output
        assert "Minimum:" in result.output
        assert "Maximum:" in result.output
        assert "Average:" in result.output
        assert "Median:" in result.output
        assert "Std Dev:" in result.output
        assert "95th %ile:" in result.output
        assert "99th %ile:" in result.output

        # Check that all values have units
        assert "ms" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_with_environment_variables(self, mock_time, mock_sleep, mock_fake_midi):
        """Test perf-test command with environment variables."""
        mock_interface = Mock()
        mock_interface.port_name = "Env Test Port"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        env = {"MDMI_MIDI_OUT": "Env Test Port", "MDMI_MIDI_IN": "Env Input Port"}
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.2"], env=env)

        assert result.exit_code == 0
        assert "📊 Performance Test Complete" in result.output

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_real_time_updates(self, mock_time, mock_sleep, mock_close, mock_savefig, mock_fake_midi):
        """Test that real-time statistics updates are working."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.6", "--interval", "0.1"])

        assert result.exit_code == 0

        # Should have sent exactly 6 pings (0.6 seconds / 0.1 interval = 6)
        ping_calls = mock_interface.send_sysex.call_count
        assert ping_calls == 6

        # Verify all pings were correct format
        expected_ping = bytes([0xF0, 0x00, 0x22, 0x77, 0x01, 0xF7])
        for call in mock_interface.send_sysex.call_args_list:
            assert call[0][0] == expected_ping

    @patch("mdmi.commands.common.FakeMidiInterface")
    @patch("matplotlib.pyplot.savefig", side_effect=Exception("Histogram error"))
    @patch("time.sleep")
    @patch("time.time")
    def test_perf_test_histogram_generation_error(self, mock_time, mock_sleep, mock_savefig, mock_fake_midi):
        """Test perf-test command when histogram generation fails."""
        mock_interface = Mock()
        mock_interface.port_name = "Fake MIDI Interface"
        mock_interface.wait_for_sysex.return_value = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        mock_fake_midi.return_value = mock_interface

        # Virtual clock
        virtual_time = [0.0]
        mock_time.side_effect = lambda: virtual_time[0]
        mock_sleep.side_effect = lambda duration: virtual_time.__setitem__(0, virtual_time[0] + duration)

        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--dry-run", "--duration", "0.2"])

        # Should fail due to histogram generation error
        assert result.exit_code != 0
        assert "Error during performance test" in result.output

    def test_perf_test_invalid_duration(self):
        """Test perf-test command with invalid duration."""
        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--duration", "-1"])

        assert result.exit_code != 0

    def test_perf_test_invalid_interval(self):
        """Test perf-test command with invalid interval."""
        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--interval", "-0.1"])

        assert result.exit_code != 0

    def test_perf_test_invalid_timeout(self):
        """Test perf-test command with invalid timeout."""
        runner = CliRunner()
        result = runner.invoke(main, ["perf-test", "--timeout", "-1"])

        assert result.exit_code != 0
