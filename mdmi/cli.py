"""CLI for Mega Drive MIDI Interface."""

import click

from mdmi.commands import (
    load_preset,
    list_ports,
    list_wopn,
    clear_preset,
    clear_all_presets,
)


@click.group()
def main():
    """Mega Drive MIDI Interface CLI."""
    pass


main.add_command(load_preset)
main.add_command(list_ports)
main.add_command(list_wopn)
main.add_command(clear_preset)
main.add_command(clear_all_presets)


if __name__ == "__main__":
    main()
