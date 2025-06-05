"""Dump FM channel parameters command for MDMI CLI."""

import click

from mdmi.preset_parsers import parse_channel_dump_response
from .dump_common import execute_dump_command, dump_options


@click.command()
@click.option(
    "--channel",
    type=click.IntRange(0, 15),
    required=True,
    help="MIDI channel to dump",
)
@dump_options
def dump_channel(channel, output_format, filename, midi_out, midi_in, dry_run, timeout):
    """Dump FM channel parameters from MDMI to a file.

    This command sends a channel dump request to MDMI for the specified MIDI channel
    and saves the response as either a DMP or TFI file.
    """

    def generate_request(generator, channel):
        return generator.generate_dump_channel_request(channel)

    execute_dump_command(
        param_value=channel,
        param_name="FM channel",
        output_format=output_format,
        filename=filename,
        midi_out=midi_out,
        midi_in=midi_in,
        dry_run=dry_run,
        timeout=timeout,
        generate_request_func=generate_request,
        parse_response_func=parse_channel_dump_response,
        default_filename_pattern="channel_{:02d}.{}",
    )
