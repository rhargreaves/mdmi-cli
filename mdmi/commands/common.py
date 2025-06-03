"""Common CLI utilities for MDMI commands."""

import click
import os
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


# Shared option definitions
port_option = click.option(
    "--port",
    default=lambda: os.environ.get("MDMI_MIDI_PORT"),
    help="MIDI output port name (default: MDMI_MIDI_PORT env var)",
)

fake_option = click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")


def midi_options(func):
    """Decorator that adds common MIDI options (--port and --fake)."""
    func = fake_option(func)
    func = port_option(func)
    return func


def get_midi_interface(port, fake):
    """Get the appropriate MIDI interface based on options."""
    if fake:
        return FakeMIDIInterface()
    else:
        return MIDIInterface(port)
