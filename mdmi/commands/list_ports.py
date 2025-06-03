"""List ports command for MDMI CLI."""

import click
import mido


@click.command()
def list_ports():
    """List available MIDI output ports."""
    try:
        ports = mido.get_output_names()
        if not ports:
            click.echo("No MIDI output ports found")
        else:
            click.echo("Available MIDI output ports:")
            for port_name in ports:
                click.echo(f"  {port_name}")
    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
