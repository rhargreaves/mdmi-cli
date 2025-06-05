"""Tests for CLI - Reorganized into focused modules.

This file has been split into more focused test modules:
- test_cli_basic.py: Basic CLI functionality (help, list-ports, etc.)
- test_cli_presets.py: Preset-related commands (load, clear, list-wopn)
- test_cli_performance.py: Performance commands (ping, perf-test)
- test_perf_test.py: Unit tests for perf_test module
"""


def setup_virtual_clock():
    """Set up a virtual clock for performance tests that don't rely on real time.

    This helper creates mock functions for time.time() and time.sleep() that
    simulate time passage without actually waiting, making tests run much faster.

    Returns:
        tuple: (time_side_effect, sleep_side_effect) functions for mocking
    """
    virtual_time = [0.0]

    def time_side_effect():
        return virtual_time[0]

    def sleep_side_effect(duration):
        virtual_time[0] += duration

    return time_side_effect, sleep_side_effect


class TestCLILegacy:
    """Legacy tests that haven't been moved to focused modules yet."""

    # Any future CLI tests that don't fit into the focused modules can go here
    pass
