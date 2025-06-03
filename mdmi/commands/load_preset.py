"""Load preset command for MDMI CLI."""

import click
import os
from pathlib import Path

from mdmi.preset_parsers import detect_preset_format, parse_preset
from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


@click.command()
@click.argument("preset_file", type=click.Path(exists=True))
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to store preset under (0-127)",
)
@click.option(
    "--port",
    default=lambda: os.environ.get("MDMI_MIDI_PORT"),
    help="MIDI output port name (default: MDMI_MIDI_PORT env var)",
)
@click.option("--fake", is_flag=True, help="Use fake MIDI interface for testing")
@click.option("--bank", type=int, default=0, help="WOPN bank index (default: 0)")
@click.option("--instrument", type=int, default=0, help="WOPN instrument index (default: 0)")
@click.option(
    "--bank-type",
    type=click.Choice(["melody", "percussion"]),
    default="melody",
    help="WOPN bank type (default: melody)",
)
def load_preset(preset_file, program, port, fake, bank, instrument, bank_type):
    """Load a preset file to MDMI."""
    try:
        preset_path = Path(preset_file)
        data = preset_path.read_bytes()
        format_type = detect_preset_format(data)

        if format_type == "UNKNOWN":
            click.echo("Error: Unsupported preset format")
            raise click.Abort()

        # Parse with format-specific options
        kwargs = {}
        if format_type == "WOPN":
            kwargs = {"bank": bank, "instrument": instrument, "bank_type": bank_type}

        preset = parse_preset(data, format_type, **kwargs)
        generator = SysExGenerator()
        sysex_data = generator.generate_preset_load(preset, program)

        if fake:
            interface = FakeMIDIInterface()
        else:
            interface = MIDIInterface(port)

        interface.send_sysex(sysex_data)

        if format_type == "WOPN":
            msg = f"Successfully loaded {format_type} preset '{preset.name}' "
            msg += f"(bank {bank}, instrument {instrument}) to program {program}"
        else:
            msg = f"Successfully loaded {format_type} preset to program {program}"
        click.echo(msg)

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
