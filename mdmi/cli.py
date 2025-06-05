"""Main CLI module for MDMI."""

import click

from mdmi.commands import (
    load_preset,
    list_ports,
    list_wopn,
    clear_preset,
    clear_all_presets,
    ping,
    dump_preset,
    dump_channel,
)


@click.group()
def main():
    """Mega Drive MIDI Interface CLI

    A command-line tool for working with the Mega Drive MIDI Interface (MDMI).
    Use MDMI_MIDI_PORT environment variable to set a default MIDI port.
    """
    pass


main.add_command(load_preset)
main.add_command(list_ports)
main.add_command(list_wopn)
main.add_command(clear_preset)
main.add_command(clear_all_presets)
main.add_command(ping)
main.add_command(dump_preset)
main.add_command(dump_channel)


if __name__ == "__main__":
    main()
