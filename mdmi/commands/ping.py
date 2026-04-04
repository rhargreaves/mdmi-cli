"""Ping command for MDMI CLI."""

import time
import random
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
    "-n",
    "--count",
    type=click.IntRange(min=1),
    default=None,
    help="Stop after sending this many pings (default: run until Ctrl+C)",
)
@click.option(
    "--size",
    type=click.IntRange(min=0),
    default=0,
    help="Additional data bytes to include after ping ID (default: 0)",
)
@click.option(
    "--no-response",
    is_flag=True,
    hidden=True,
    help="For testing: disable fake interface pong simulation",
)
def ping(midi_out, midi_in, dry_run, timeout, count, size, no_response):
    """Send a ping to MDMI and measure round-trip latency.

    This command sends a ping SysEx message (00 22 77 01) to the MDMI
    and waits for a pong response (00 22 77 02) to measure MIDI round-trip latency.
    """
    try:
        interface = get_midi_interface(midi_out, midi_in, dry_run)

        if no_response and dry_run:
            interface.simulate_pong = False

        transmitted = 0
        received = 0
        latencies_ms = []
        sequence = 0
        target_name = interface.port_name
        input_port_name = getattr(interface, "input_port_name", None)
        if not isinstance(input_port_name, str) or not input_port_name:
            input_port_name = target_name
        source_name = input_port_name

        click.echo(f"PING {target_name} timeout: {timeout}s")
        if source_name != target_name:
            click.echo(f"Listening for pong on {source_name}...")
        click.echo("Press Ctrl+C to stop")

        try:
            while count is None or transmitted < count:
                ping_id = random.randint(0, 0x7F)
                payload = b""
                if size > 0:
                    payload = bytes([0x00] + [random.randint(0, 0x7F) for _ in range(size - 1)])
                ping_message = bytes([0xF0, 0x00, 0x22, 0x77, 0x01, ping_id]) + payload + bytes([0xF7])
                expected_pong = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, ping_id, 0xF7])

                transmitted += 1
                sequence += 1
                start_time = time.time()
                interface.send_sysex(ping_message)
                pong_response = interface.wait_for_sysex(timeout)
                end_time = time.time()

                if pong_response == expected_pong:
                    round_trip_ms = (end_time - start_time) * 1000
                    received += 1
                    latencies_ms.append(round_trip_ms)
                    click.echo(
                        f"{len(pong_response)} bytes from {source_name}: seq={sequence} id={ping_id} "
                        + f"time={round_trip_ms:.2f} ms"
                    )
                elif pong_response is None:
                    click.echo(f"Request timeout for ping seq={sequence} id={ping_id}")
                else:
                    hex_response = " ".join(f"{b:02X}" for b in pong_response)
                    click.echo(f"Unexpected response: {hex_response}")
        except KeyboardInterrupt:
            pass

        click.echo()
        click.echo(f"--- {target_name} ping statistics ---")
        loss_percent = ((transmitted - received) / transmitted) * 100 if transmitted else 0.0
        click.echo(f"{transmitted} packets transmitted, {received} received, {loss_percent:.1f}% packet loss")

        if latencies_ms:
            min_latency = min(latencies_ms)
            avg_latency = sum(latencies_ms) / len(latencies_ms)
            max_latency = max(latencies_ms)
            click.echo(f"round-trip min/avg/max = {min_latency:.2f}/{avg_latency:.2f}/{max_latency:.2f} ms")

        if received < transmitted:
            raise click.Abort()

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error during ping: {e}")
        raise click.Abort()
    finally:
        if "interface" in locals():
            interface.close()
