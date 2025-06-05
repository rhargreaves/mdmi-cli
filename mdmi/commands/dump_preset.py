"""Dump preset command for MDMI CLI."""

import click
from pathlib import Path

from mdmi.preset_parsers import parse_dump_response, write_dmp_preset, write_tfi_preset
from mdmi.sysex_generator import SysExGenerator
from .common import ping_options, get_ping_interface


@click.command()
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to dump",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["dmp", "tfi"]),
    default="dmp",
    help="Output format (default: dmp)",
)
@click.option(
    "--filename",
    type=click.Path(),
    help="Output filename (default: preset_<program>.<format>)",
)
@ping_options
@click.option(
    "--timeout",
    type=float,
    default=5.0,
    help="Timeout in seconds to wait for dump response (default: 5.0)",
)
def dump_preset(program, output_format, filename, midi_out, midi_in, dry_run, timeout):
    """Dump a preset from MDMI to a file.

    This command sends a dump request to MDMI for the specified program number
    and saves the response as either a DMP or TFI file.
    """
    try:
        # Get MIDI interface
        interface = get_ping_interface(midi_out, midi_in, dry_run)

        # Generate output filename if not specified
        if not filename:
            filename = f"preset_{program:03d}.{output_format}"

        # Ensure output path has correct extension
        output_path = Path(filename)
        if output_path.suffix.lower() != f".{output_format}":
            output_path = output_path.with_suffix(f".{output_format}")

        # Generate dump request SysEx
        generator = SysExGenerator()
        dump_request = generator.generate_dump_preset_request(program)

        click.echo(f"Requesting dump of program {program} from {interface.port_name}...")
        if hasattr(interface, "input_port_name") and interface.input_port_name != interface.port_name:
            click.echo(f"Listening for response on {interface.input_port_name}...")

        # Send dump request
        interface.send_sysex(dump_request)

        # Wait for dump response
        click.echo(f"Waiting for dump response (timeout: {timeout}s)...")
        dump_response = interface.wait_for_sysex(timeout)

        if dump_response is None:
            click.echo(f"❌ No dump response received within {timeout} seconds")
            click.echo("This could mean:")
            click.echo("  - MDMI is not connected or powered")
            click.echo("  - MIDI cables are not properly connected")
            click.echo("  - MIDI interface doesn't support input")
            click.echo("  - The requested program slot is empty")
            raise click.Abort()

        # Parse the dump response
        try:
            preset = parse_dump_response(dump_response)
        except Exception as e:
            hex_response = " ".join(f"{b:02X}" for b in dump_response)
            click.echo(f"❌ Failed to parse dump response: {e}")
            click.echo(f"Raw response: {hex_response}")
            raise click.Abort()

        # Write the preset file
        try:
            if output_format == "dmp":
                write_dmp_preset(preset, str(output_path))
            elif output_format == "tfi":
                write_tfi_preset(preset, str(output_path))
            else:
                click.echo(f"❌ Unsupported output format: {output_format}")
                raise click.Abort()
        except Exception as e:
            click.echo(f"❌ Failed to write {output_format.upper()} file: {e}")
            raise click.Abort()

        # Success!
        click.echo(f"✅ Successfully dumped program {program} to {output_path}")
        click.echo(f"Format: {output_format.upper()}")
        click.echo(f"Algorithm: {preset.algorithm}, Feedback: {preset.feedback}")
        click.echo(f"LFO AMS: {preset.lfo_ams}, LFO FMS: {preset.lfo_fms}")

    except Exception as e:
        click.echo(f"Error during dump: {e}")
        raise click.Abort()
    finally:
        if "interface" in locals():
            interface.close()
