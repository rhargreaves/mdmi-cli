"""Dump preset command for MDMI CLI."""

import click

from mdmi.preset_parsers import parse_dump_response
from .dump_common import execute_dump_command, dump_options


@click.command()
@click.option(
    "--program",
    type=click.IntRange(0, 127),
    required=True,
    help="MIDI program number to dump",
)
@dump_options
def dump_preset(program, output_format, filename, midi_out, midi_in, dry_run, timeout):
    """Dump a preset from MDMI to a file.

    This command sends a dump request to MDMI for the specified program number
    and saves the response as either a DMP or TFI file.
    """

    def generate_request(generator, program):
        return generator.generate_dump_preset_request(program)

    execute_dump_command(
        param_value=program,
        param_name="program",
        output_format=output_format,
        filename=filename,
        midi_out=midi_out,
        midi_in=midi_in,
        dry_run=dry_run,
        timeout=timeout,
        generate_request_func=generate_request,
        parse_response_func=parse_dump_response,
        default_filename_pattern="preset_{:03d}.{}",
    )
