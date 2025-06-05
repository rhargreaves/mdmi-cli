"""Common functionality for dump commands."""

from pathlib import Path
from mdmi.preset_parsers import write_dmp_preset, write_tfi_preset
from mdmi.sysex_generator import SysExGenerator
from .common import get_midi_interface, dual_midi_options
import click


def dump_options(func):
    """Decorator that adds common dump options (format, filename, dual MIDI options, timeout)."""

    func = click.option(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds to wait for dump response (default: 5.0)",
    )(func)
    func = dual_midi_options(func)
    func = click.option(
        "--filename",
        type=click.Path(),
        help="Output filename (auto-generated if not specified)",
    )(func)
    func = click.option(
        "--format",
        "output_format",
        type=click.Choice(["dmp", "tfi"]),
        default="dmp",
        help="Output format (default: dmp)",
    )(func)

    return func


def execute_dump_command(
    param_value,
    param_name,
    output_format,
    filename,
    midi_out,
    midi_in,
    dry_run,
    timeout,
    generate_request_func,
    parse_response_func,
    default_filename_pattern,
):
    """Common logic for dump commands.

    Args:
        param_value: The parameter value (channel or program number)
        param_name: Name of the parameter for display purposes
        output_format: Output format ("dmp" or "tfi")
        filename: User-specified filename or None
        midi_out, midi_in, dry_run: MIDI interface options
        timeout: Response timeout in seconds
        generate_request_func: Function to generate the SysEx request
        parse_response_func: Function to parse the response
        default_filename_pattern: Format string for default filename
    """
    try:
        # Get MIDI interface
        interface = get_midi_interface(midi_out, midi_in, dry_run)

        # Generate output filename if not specified
        if not filename:
            filename = default_filename_pattern.format(param_value, output_format)

        # Ensure output path has correct extension
        output_path = Path(filename)
        if output_path.suffix.lower() != f".{output_format}":
            output_path = output_path.with_suffix(f".{output_format}")

        # Generate dump request SysEx
        generator = SysExGenerator()
        dump_request = generate_request_func(generator, param_value)

        click.echo(f"Requesting dump of {param_name} {param_value} from {interface.port_name}...")
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
            if param_name == "FM channel":
                click.echo("  - The requested MIDI channel is not assigned to an FM channel")
            else:
                click.echo("  - The requested program slot is empty")
            raise click.Abort()

        # Parse the dump response
        try:
            preset = parse_response_func(dump_response)
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
        click.echo(f"✅ Successfully dumped {param_name} {param_value} to {output_path}")
        click.echo(f"Format: {output_format.upper()}")
        click.echo(f"Algorithm: {preset.algorithm}, Feedback: {preset.feedback}")
        click.echo(f"LFO AMS: {preset.lfo_ams}, LFO FMS: {preset.lfo_fms}")

    except Exception as e:
        click.echo(f"Error during dump: {e}")
        raise click.Abort()
    finally:
        if "interface" in locals():
            interface.close()
