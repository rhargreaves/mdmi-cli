"""CLI for Mega Drive MIDI Interface."""

import click
from pathlib import Path
import mido

from mdmi.preset_parsers import detect_preset_format, parse_preset
from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


@click.group()
def main():
    """Mega Drive MIDI Interface CLI."""
    pass


@main.command()
@click.argument("preset_file", required=False)
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    help="MIDI program number to store preset under (0-127)",
)
@click.option("--port", help="MIDI output port name")
@click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")
@click.option("--list-ports", is_flag=True, help="List available MIDI ports")
def load_preset(preset_file, program, port, fake, list_ports):
    """Load a preset file to MDMI."""
    if list_ports:
        ports = mido.get_output_names()
        click.echo("Available MIDI ports:")
        for port_name in ports:
            click.echo(f"  {port_name}")
        return

    if not preset_file:
        click.echo("Error: PRESET_FILE is required")
        raise click.Abort()

    if program is None:
        click.echo("Error: --program is required")
        raise click.Abort()

    preset_path = Path(preset_file)
    if not preset_path.exists():
        click.echo(f"Error: File {preset_file} does not exist")
        raise click.Abort()

    try:
        data = preset_path.read_bytes()
        format_type = detect_preset_format(data)

        if format_type == "UNKNOWN":
            click.echo("Error: Unsupported preset format")
            raise click.Abort()

        preset = parse_preset(data, format_type)
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program)

        if fake:
            interface = FakeMIDIInterface()
        else:
            interface = MIDIInterface(port)

        interface.send_sysex(sysex_data)

        msg = f"Successfully loaded {format_type} preset to program {program}"
        click.echo(msg)

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()


@main.command()
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to clear (0-127)",
)
@click.option("--port", help="MIDI output port name")
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


@main.command()
@click.option("--port", help="MIDI output port name")
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


if __name__ == "__main__":
    main()
