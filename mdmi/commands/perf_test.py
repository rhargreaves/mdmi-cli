"""Performance test command for MDMI CLI."""

import time
import signal
import statistics
from datetime import datetime
import click
import matplotlib.pyplot as plt
import numpy as np
from .common import dual_midi_options, get_midi_interface


def get_default_histogram_filename():
    """Generate default histogram filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"perf_hist_{timestamp}.png"


class PerformanceTest:
    """Class to manage the performance test state and statistics."""

    def __init__(self):
        self.latencies = []
        self.start_time = None
        self.running = True

    def add_latency(self, latency_ms):
        """Add a latency measurement to the results."""
        self.latencies.append(latency_ms)

    def get_stats(self):
        """Get current statistics."""
        if not self.latencies:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "median": 0}

        return {
            "count": len(self.latencies),
            "min": min(self.latencies),
            "max": max(self.latencies),
            "avg": statistics.mean(self.latencies),
            "median": statistics.median(self.latencies),
        }

    def stop(self):
        """Stop the test."""
        self.running = False


@click.command()
@dual_midi_options
@click.option(
    "--duration",
    type=float,
    help="Test duration in seconds (default: run until Ctrl+C)",
)
@click.option(
    "--interval",
    type=float,
    default=0.05,
    help="Interval between pings in seconds (default: 0.05)",
)
@click.option(
    "--hist-filename",
    type=click.Path(),
    default=None,
    help="Output PNG file for histogram (default: perf_hist_YYYYMMDD_HHMMSS.png)",
)
@click.option(
    "--timeout",
    type=float,
    default=2.0,
    help="Timeout for individual ping responses (default: 2.0)",
)
def perf_test(midi_out, midi_in, dry_run, duration, interval, hist_filename, timeout):
    """Continuously test MDMI ping/pong latency and generate performance histogram.

    This command sends continuous ping requests to MDMI and measures round-trip
    latency. Real-time statistics are displayed and a histogram is generated
    at the end showing the latency distribution.

    Press Ctrl+C to stop the test early.
    """
    perf = PerformanceTest()

    def signal_handler(signum, frame):
        """Handle Ctrl+C gracefully."""
        perf.stop()

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Set default histogram filename if not provided
        if hist_filename is None:
            hist_filename = get_default_histogram_filename()

        # Get MIDI interface
        interface = get_midi_interface(midi_out, midi_in, dry_run)

        # Create ping SysEx message
        ping_message = bytes([0xF0, 0x00, 0x22, 0x77, 0x01, 0xF7])
        expected_pong = bytes([0xF0, 0x00, 0x22, 0x77, 0x02, 0xF7])

        click.echo(f"Starting performance test on {interface.port_name}...")
        if hasattr(interface, "input_port_name") and interface.input_port_name != interface.port_name:
            click.echo(f"Listening for responses on {interface.input_port_name}...")

        if duration:
            click.echo(f"Test duration: {duration} seconds")
        else:
            click.echo("Test duration: until Ctrl+C")

        click.echo(f"Ping interval: {interval} seconds")
        click.echo(f"Individual timeout: {timeout} seconds")
        click.echo("\nStarting test... (Press Ctrl+C to stop)")
        click.echo()

        perf.start_time = time.time()
        failed_pings = 0
        last_update = 0

        while perf.running:
            # Check if duration limit reached
            if duration and (time.time() - perf.start_time) >= duration:
                break

            # Send ping
            ping_start = time.time()
            interface.send_sysex(ping_message)

            # Wait for pong
            pong_response = interface.wait_for_sysex(timeout)
            ping_end = time.time()

            if pong_response == expected_pong:
                # Successful ping - record latency
                latency_ms = (ping_end - ping_start) * 1000
                perf.add_latency(latency_ms)
            else:
                # Failed ping
                failed_pings += 1

            # Update statistics display (but not too frequently)
            current_time = time.time()
            if current_time - last_update >= 0.5:  # Update every 0.5 seconds
                stats = perf.get_stats()
                elapsed = current_time - perf.start_time

                # Clear line and show stats
                print(
                    f"\r\033[K"
                    f"Elapsed: {elapsed:.1f}s | "
                    f"Pings: {stats['count']} | "
                    f"Failed: {failed_pings} | "
                    f"Min: {stats['min']:.1f}ms | "
                    f"Max: {stats['max']:.1f}ms | "
                    f"Avg: {stats['avg']:.1f}ms | "
                    f"Median: {stats['median']:.1f}ms",
                    end="",
                    flush=True,
                )

                last_update = current_time

            # Wait for next ping
            time.sleep(interval)

        # Final newline after stats
        print()

        # Generate final report
        stats = perf.get_stats()
        total_time = time.time() - perf.start_time

        click.echo("\n📊 Performance Test Complete")
        click.echo(f"Total duration: {total_time:.1f} seconds")
        click.echo(f"Total pings sent: {stats['count'] + failed_pings}")
        click.echo(f"Successful pings: {stats['count']}")
        click.echo(f"Failed pings: {failed_pings}")

        if stats["count"] > 0:
            success_rate = (stats["count"] / (stats["count"] + failed_pings)) * 100
            click.echo(f"Success rate: {success_rate:.1f}%")
            click.echo("\n📈 Latency Statistics:")
            click.echo(f"  Minimum:  {stats['min']:.2f} ms")
            click.echo(f"  Maximum:  {stats['max']:.2f} ms")
            click.echo(f"  Average:  {stats['avg']:.2f} ms")
            click.echo(f"  Median:   {stats['median']:.2f} ms")

            if len(perf.latencies) > 1:
                std_dev = statistics.stdev(perf.latencies)
                click.echo(f"  Std Dev:  {std_dev:.2f} ms")

                # Calculate percentiles
                sorted_latencies = sorted(perf.latencies)
                p95 = np.percentile(sorted_latencies, 95)
                p99 = np.percentile(sorted_latencies, 99)
                click.echo(f"  95th %ile: {p95:.2f} ms")
                click.echo(f"  99th %ile: {p99:.2f} ms")

            # Generate histogram
            generate_histogram(perf.latencies, hist_filename, stats, interval)
            click.echo(f"\n📊 Histogram saved to: {hist_filename}")
        else:
            click.echo("❌ No successful pings recorded - cannot generate histogram")

    except Exception as e:
        click.echo(f"\nError during performance test: {e}")
        raise click.Abort()
    finally:
        if "interface" in locals():
            interface.close()


def generate_histogram(latencies, output_path, stats, interval):
    """Generate and save a latency histogram."""
    plt.figure(figsize=(12, 8))

    # Create histogram
    n_bins = min(100, max(10, len(latencies) // 10))  # Adaptive bin count
    counts, bins, patches = plt.hist(latencies, bins=n_bins, alpha=0.7, color="skyblue", edgecolor="black")

    # Add statistics text box
    stats_text = (
        f"Count: {stats['count']}\n"
        f"Interval: {interval * 1000:.1f} ms\n"
        f"Min: {stats['min']:.2f} ms\n"
        f"Max: {stats['max']:.2f} ms\n"
        f"Avg: {stats['avg']:.2f} ms\n"
        f"Median: {stats['median']:.2f} ms"
    )

    if len(latencies) > 1:
        std_dev = statistics.stdev(latencies)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        stats_text += f"\nStd Dev: {std_dev:.2f} ms\n95th %: {p95:.2f} ms\n99th %: {p99:.2f} ms"

    plt.text(
        0.70,
        0.95,
        stats_text,
        transform=plt.gca().transAxes,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        verticalalignment="top",
        fontfamily="monospace",
    )

    # Add vertical lines for key statistics
    plt.axvline(stats["avg"], color="red", linestyle="--", alpha=0.8, label=f"Average ({stats['avg']:.1f} ms)")
    plt.axvline(stats["median"], color="green", linestyle="--", alpha=0.8, label=f"Median ({stats['median']:.1f} ms)")

    # Labels and title
    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.title("MDMI Ping/Pong Latency Distribution")

    # Only add legend if there are labeled artists
    handles, labels = plt.gca().get_legend_handles_labels()
    if handles:
        plt.legend()

    plt.grid(True, alpha=0.3)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()  # Close to free memory
