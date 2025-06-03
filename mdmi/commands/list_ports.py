"""List MIDI ports command for MDMI CLI."""

import click
import mido


@click.command()
def list_ports():
    """List available MIDI input and output ports."""
    click.echo("Available MIDI ports:")
    click.echo()

    # List output ports
    output_ports = mido.get_output_names()
    click.echo("📤 Output ports (for sending to MDMI):")
    if output_ports:
        for port in output_ports:
            click.echo(f"  • {port}")
    else:
        click.echo("  (No MIDI output ports found)")

    click.echo()

    # List input ports
    input_ports = mido.get_input_names()
    click.echo("📥 Input ports (for receiving from MDMI):")
    if input_ports:
        for port in input_ports:
            click.echo(f"  • {port}")
    else:
        click.echo("  (No MIDI input ports found)")

    click.echo()
    click.echo("Environment variables:")
    click.echo("  MDMI_MIDI_OUT  - Default output port")
    click.echo("  MDMI_MIDI_IN   - Default input port")
    click.echo("  MDMI_MIDI_PORT - Default output port (legacy)")
