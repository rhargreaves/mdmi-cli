"""Clear all presets command for MDMI CLI."""

import click
import os

from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


@click.command()
@click.option(
    "--port",
    default=lambda: os.environ.get("MDMI_MIDI_PORT"),
    help="MIDI output port name (default: MDMI_MIDI_PORT env var)",
)
@click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def clear_all_presets(port, fake, confirm):
    """Clear all user presets."""
    if not confirm:
        prompt = "This will clear ALL user presets. Continue?"
        click.confirm(prompt, abort=True)

    try:
        generator = SysExGenerator()
        sysex_data = generator.generate_clear_all_presets()

        if fake:
            interface = FakeMIDIInterface()
        else:
            interface = MIDIInterface(port)

        interface.send_sysex(sysex_data)
        click.echo("Successfully cleared all presets")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
