"""Clear preset command for MDMI CLI."""

import click

from mdmi.sysex_generator import SysExGenerator
from .common import midi_options, get_midi_interface


@click.command()
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to clear (0-127)",
)
@midi_options
def clear_preset(program, port, fake):
    """Clear a specific user preset."""
    try:
        generator = SysExGenerator()
        sysex_data = generator.generate_clear_preset(program)

        interface = get_midi_interface(port, fake)
        interface.send_sysex(sysex_data)
        click.echo(f"Successfully cleared preset {program}")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
