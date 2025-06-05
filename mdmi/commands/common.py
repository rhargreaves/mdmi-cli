"""Common CLI utilities for MDMI commands."""

import click
import os
from mdmi.mido_midi_interface import MidoMidiInterface
from mdmi.fake_midi_interface import FakeMidiInterface
from mdmi.midi_interface import MidiInterface


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

dry_run_option = click.option("--dry-run", is_flag=True, help="Use fake MIDI interface and display MIDI messages")


def midi_options(func):
    """Decorator that adds common MIDI options (--midi-out and --dry-run)."""
    func = dry_run_option(func)
    func = midi_out_option(func)
    return func


def dual_midi_options(func):
    """Decorator that adds MIDI options for commands that need both input and output ports."""
    func = dry_run_option(func)
    func = midi_in_option(func)
    func = midi_out_option(func)
    return func


def get_midi_interface(midi_out, midi_in, dry_run) -> MidiInterface:
    """Get the appropriate MIDI interface based on options.

    Args:
        midi_out: Output port name
        midi_in: Input port name (can be None)
        dry_run: Whether to use fake interface

    Returns:
        MIDI interface instance conforming to MIDIInterface
    """
    if dry_run:
        return FakeMidiInterface()
    else:
        return MidoMidiInterface(midi_out, midi_in)
