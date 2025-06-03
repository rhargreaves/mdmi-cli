"""Clear preset command for MDMI CLI."""

import click
import os

from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


@click.command()
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to clear (0-127)",
)
@click.option(
    "--port",
    default=lambda: os.environ.get("MDMI_MIDI_PORT"),
    help="MIDI output port name (default: MDMI_MIDI_PORT env var)",
)
@click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")
def clear_preset(program, port, fake):
    """Clear a specific user preset."""
    try:
        generator = SysExGenerator()
        sysex_data = generator.generate_clear_preset(program)

        if fake:
            interface = FakeMIDIInterface()
        else:
            interface = MIDIInterface(port)

        interface.send_sysex(sysex_data)
        click.echo(f"Successfully cleared preset {program}")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
