"""Clear all presets command for MDMI CLI."""

import click

from mdmi.sysex_generator import SysExGenerator
from .common import midi_options, get_midi_interface


@click.command()
@midi_options
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def clear_all_presets(port, fake, confirm):
    """Clear all user presets."""
    if not confirm:
        prompt = "This will clear ALL user presets. Continue?"
        click.confirm(prompt, abort=True)

    try:
        generator = SysExGenerator()
        sysex_data = generator.generate_clear_all_presets()

        interface = get_midi_interface(port, fake)
        interface.send_sysex(sysex_data)
        click.echo("Successfully cleared all presets")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
