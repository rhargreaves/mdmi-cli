"""CLI for Mega Drive MIDI Interface."""

import click
from pathlib import Path
from typing import Optional

from .preset_parsers import WOPNParser, DMPParser, TFIParser, PresetParseError
from .sysex_generator import SysExGenerator
from .midi_interface import MIDIInterface, FakeMIDIInterface


def detect_preset_format(filename: str) -> str:
    """Detect preset format from file extension."""
    suffix = Path(filename).suffix.lower()

    if suffix == ".tfi":
        return "TFI"
    elif suffix == ".dmp":
        return "DMP"
    elif suffix == ".wopn":
        return "WOPN"
    else:
        return "UNKNOWN"


def get_parser(format_type: str):
    """Get appropriate parser for format type."""
    if format_type == "TFI":
        return TFIParser()
    elif format_type == "DMP":
        return DMPParser()
    elif format_type == "WOPN":
        return WOPNParser()
    else:
        raise ValueError(f"Unsupported format: {format_type}")


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Mega Drive MIDI Interface CLI tool.

    Control your Mega Drive MIDI Interface via SysEx commands.
    Supports loading WOPN, DMP, and TFI preset formats.
    """
    pass


@main.command("load-preset")
@click.argument("preset_file", type=click.Path())
@click.option(
    "--channel",
    "-c",
    type=click.IntRange(0, 5),
    required=True,
    help="Target FM channel (0-5)",
)
@click.option(
    "--port", "-p", type=str, help="MIDI port name (use --list-ports to see available)"
)
@click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")
@click.option("--list-ports", is_flag=True, help="List available MIDI ports and exit")
def load_preset(
    preset_file: str, channel: int, port: Optional[str], fake: bool, list_ports: bool
):
    """Load a preset file to MDMI.

    Supports TFI, DMP, and WOPN preset formats.
    Use --fake for testing without real MIDI hardware.
    """
    import mido

    if list_ports:
        click.echo("Available MIDI ports:")
        for port_name in mido.get_output_names():
            click.echo(f"  {port_name}")
        return

    # Validate file
    preset_path = Path(preset_file)
    if not preset_path.exists():
        click.echo(f"Error: File '{preset_file}' does not exist.")
        raise click.Abort()

    # Detect format
    format_type = detect_preset_format(preset_file)
    if format_type == "UNKNOWN":
        click.echo(f"Error: Unsupported file format for '{preset_file}'.")
        click.echo("Supported formats: .tfi, .dmp, .wopn")
        raise click.Abort()

    # Parse preset
    try:
        data = preset_path.read_bytes()
        parser = get_parser(format_type)
        preset = parser.parse(data)
    except PresetParseError as e:
        click.echo(f"Error parsing preset: {e}")
        raise click.Abort()

    # Generate SysEx
    try:
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, channel)
    except ValueError as e:
        click.echo(f"Error generating SysEx: {e}")
        raise click.Abort()

    # Send via MIDI
    try:
        if fake:
            interface = FakeMIDIInterface()
            interface.send_sysex(sysex_data)
            click.echo(
                f"Successfully loaded {format_type} preset "
                f"'{preset_path.name}' to channel {channel} "
                f"(fake interface)"
            )
        else:
            if not port:
                available_ports = mido.get_output_names()
                if not available_ports:
                    click.echo("Error: No MIDI ports available.")
                    raise click.Abort()
                elif len(available_ports) == 1:
                    port = available_ports[0]
                    click.echo(f"Using MIDI port: {port}")
                else:
                    click.echo(
                        "Error: Multiple MIDI ports available. "
                        "Please specify with --port:"
                    )
                    for port_name in available_ports:
                        click.echo(f"  {port_name}")
                    raise click.Abort()

            interface = MIDIInterface(port)
            interface.send_sysex(sysex_data)
            interface.close()
            click.echo(
                f"Successfully loaded {format_type} preset "
                f"'{preset_path.name}' to channel {channel}"
            )

    except Exception as e:
        click.echo(f"Error sending MIDI: {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
