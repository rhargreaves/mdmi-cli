"""Clear all presets command for MDMI CLI."""

import click

from mdmi.sysex_generator import SysExGenerator
from .common import midi_options, get_midi_interface


@click.command()
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@midi_options
def clear_all_presets(confirm, midi_out, dry_run):
    """Clear all user presets.

    This will reset ALL user presets to their default state. Use with caution!
    """
    try:
        # Confirmation check
        if not confirm:
            if not click.confirm("This will clear ALL presets. Are you sure?"):
                click.echo("Operation cancelled.")
                raise click.Abort()

        generator = SysExGenerator()
        sysex_data = generator.generate_clear_all_presets()

        interface = get_midi_interface(midi_out, None, dry_run)
        interface.send_sysex(sysex_data)

        click.echo("Successfully cleared all presets")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
