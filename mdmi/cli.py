"""CLI for Mega Drive MIDI Interface."""

import click
import os
from pathlib import Path
import mido

from mdmi.preset_parsers import detect_preset_format, parse_preset, list_wopn_contents
from mdmi.sysex_generator import SysExGenerator
from mdmi.midi_interface import MIDIInterface, FakeMIDIInterface


@click.group()
def main():
    """Mega Drive MIDI Interface CLI."""
    pass


@main.command()
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


@main.command()
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


@main.command()
@click.argument("wopn_file", type=click.Path(exists=True))
def list_wopn(wopn_file):
    """List contents of a WOPN file."""
    try:
        data = Path(wopn_file).read_bytes()
        if detect_preset_format(data) != "WOPN":
            click.echo("Error: File is not a valid WOPN file")
            raise click.Abort()

        contents = list_wopn_contents(data)

        click.echo(f"WOPN File: {wopn_file}")
        click.echo("=" * 50)

        # Show melody banks
        if contents["melody_banks"]:
            click.echo("\nMelody Banks:")
            for bank in contents["melody_banks"]:
                click.echo(f"  Bank {bank['index']}: {bank['name']}")
                for inst in bank["instruments"][:10]:  # Show first 10
                    click.echo(f"    {inst['index']:3d}: {inst['name']}")
                if len(bank["instruments"]) > 10:
                    click.echo(f"    ... and {len(bank['instruments']) - 10} more")

        # Show percussion banks
        if contents["percussion_banks"]:
            click.echo("\nPercussion Banks:")
            for bank in contents["percussion_banks"]:
                click.echo(f"  Bank {bank['index']}: {bank['name']}")
                for inst in bank["instruments"][:10]:  # Show first 10
                    click.echo(f"    {inst['index']:3d}: {inst['name']}")
                if len(bank["instruments"]) > 10:
                    click.echo(f"    ... and {len(bank['instruments']) - 10} more")

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


@main.command()
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


if __name__ == "__main__":
    main()
