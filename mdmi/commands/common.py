"""Common CLI utilities for MDMI commands."""

import click
import os
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


def get_default_output_port():
    """Get default output port from environment variables."""
    # MDMI_MIDI_OUT takes precedence, fall back to MDMI_MIDI_PORT for backwards compatibility
    return os.environ.get("MDMI_MIDI_OUT") or os.environ.get("MDMI_MIDI_PORT")


def get_default_input_port():
    """Get default input port from environment variables."""
    return os.environ.get("MDMI_MIDI_IN")


# Shared option definitions
midi_out_option = click.option(
    "--midi-out",
    default=get_default_output_port,
    help="MIDI output port name (default: MDMI_MIDI_OUT or MDMI_MIDI_PORT env var)",
)

midi_in_option = click.option(
    "--midi-in",
    default=get_default_input_port,
    help="MIDI input port name (default: MDMI_MIDI_IN env var)",
)

fake_option = click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")


def midi_options(func):
    """Decorator that adds common MIDI options (--midi-out and --fake)."""
    func = fake_option(func)
    func = midi_out_option(func)
    return func


def ping_options(func):
    """Decorator that adds MIDI options for ping command (includes input port)."""
    func = fake_option(func)
    func = midi_in_option(func)
    func = midi_out_option(func)
    return func


def get_midi_interface(midi_out, fake):
    """Get the appropriate MIDI interface based on options.

    Args:
        midi_out: Output port name
        fake: Whether to use fake interface

    Returns:
        MIDIInterface or FakeMIDIInterface instance
    """
    if fake:
        return FakeMIDIInterface()
    else:
        return MIDIInterface(midi_out)


def get_ping_interface(midi_out, midi_in, fake):
    """Get MIDI interface for ping command with separate input/output ports.

    Args:
        midi_out: Output port name
        midi_in: Input port name (can be None)
        fake: Whether to use fake interface

    Returns:
        MIDIInterface or FakeMIDIInterface instance
    """
    if fake:
        return FakeMIDIInterface()
    else:
        return MIDIInterface(midi_out, midi_in)
