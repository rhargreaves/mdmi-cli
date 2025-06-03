"""List WOPN command for MDMI CLI."""

import click
from pathlib import Path

from mdmi.preset_parsers import detect_preset_format, list_wopn_contents


@click.command()
@click.argument("wopn_file", type=click.Path(exists=True))
@click.option("--full", is_flag=True, help="Show all instruments (default: first 10 per bank)")
def list_wopn(wopn_file, full):
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
                instruments = bank["instruments"]

                if full:
                    # Show all instruments
                    for inst in instruments:
                        click.echo(f"    {inst['index']:3d}: {inst['name']}")
                else:
                    # Show first 10 instruments
                    for inst in instruments[:10]:
                        click.echo(f"    {inst['index']:3d}: {inst['name']}")
                    if len(instruments) > 10:
                        click.echo(f"    ... and {len(instruments) - 10} more (use --full to see all)")

        # Show percussion banks
        if contents["percussion_banks"]:
            click.echo("\nPercussion Banks:")
            for bank in contents["percussion_banks"]:
                click.echo(f"  Bank {bank['index']}: {bank['name']}")
                instruments = bank["instruments"]

                if full:
                    # Show all instruments
                    for inst in instruments:
                        click.echo(f"    {inst['index']:3d}: {inst['name']}")
                else:
                    # Show first 10 instruments
                    for inst in instruments[:10]:
                        click.echo(f"    {inst['index']:3d}: {inst['name']}")
                    if len(instruments) > 10:
                        click.echo(f"    ... and {len(instruments) - 10} more (use --full to see all)")

    except Exception as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
