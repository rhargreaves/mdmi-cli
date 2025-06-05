"""Ping command for MDMI CLI."""

import time
import click
from .common import dual_midi_options, get_midi_interface


@click.command()
@dual_midi_options
@click.option(
    "--timeout",
    type=float,
    default=5.0,
    help="Timeout in seconds to wait for pong response (default: 5.0)",
)
@click.option(
    "--no-response",
    is_flag=True,
    hidden=True,
    help="For testing: disable fake interface pong simulation",
)
def ping(midi_out, midi_in, dry_run, timeout, no_response):
    """Send a ping to MDMI and measure round-trip latency.

    This command sends a ping SysEx message (00 22 77 01) to the MDMI
    and waits for a pong response (00 22 77 02) to measure MIDI round-trip latency.
    """
    try:
        # Get MIDI interface
        interface = get_midi_interface(midi_out, midi_in, dry_run)

        # If testing with no response, disable pong simulation
        if no_response and dry_run:
            interface.simulate_pong = False

        # Create ping SysEx message (F0 00 22 77 01 F7)
        ping_message = bytes([0xF0, 0x00, 0x22, 0x77, 0x01, 0xF7])

        click.echo(f"Sending ping to {interface.port_name}...")
        if hasattr(interface, "input_port_name") and interface.input_port_name != interface.port_name:
            click.echo(f"Listening for pong on {interface.input_port_name}...")

        # Record start time and send ping
        start_time = time.time()
        interface.send_sysex(ping_message)

        # Wait for pong response
        click.echo(f"Waiting for pong response (timeout: {timeout}s)...")
        pong_response = interface.wait_for_sysex(timeout)
        end_time = time.time()

        if pong_response is None:
            click.echo(f"❌ No pong response received within {timeout} seconds")
            click.echo("This could mean:")
            click.echo("  - MDMI is not connected or powered")
            click.echo("  - MIDI cables are not properly connected")
            click.echo("  - MIDI interface doesn't support input")
            raise click.Abort()

        # Verify it's a valid pong response
        expected_pong = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])
        if pong_response != expected_pong:
            hex_response = " ".join(f"{b:02X}" for b in pong_response)
            click.echo(f"❌ Unexpected response: {hex_response}")
            click.echo("Expected pong: F0 00 22 77 02 F7")
            raise click.Abort()

        # Calculate round-trip time
        round_trip_ms = (end_time - start_time) * 1000

        # Success!
        click.echo("✅ Pong received!")
        click.echo(f"Round-trip latency: {round_trip_ms:.2f} ms")

        # Provide interpretation of the latency
        if round_trip_ms < 5:
            click.echo("🟢 Excellent latency")
        elif round_trip_ms < 10:
            click.echo("🟡 Good latency")
        elif round_trip_ms < 20:
            click.echo("🟠 Acceptable latency")
        else:
            click.echo("🔴 High latency - check connections")

    except Exception as e:
        click.echo(f"Error during ping: {e}")
        raise click.Abort()
    finally:
        if "interface" in locals():
            interface.close()
