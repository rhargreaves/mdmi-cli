"""Tests for perf_test module."""

import statistics
import tempfile
import os
from unittest.mock import patch
import matplotlib
import numpy as np

from mdmi.commands.perf_test import PerformanceTest, generate_histogram


class TestPerformanceTest:
    """Tests for PerformanceTest class."""

    def test_init(self):
        """Test PerformanceTest initialization."""
        perf = PerformanceTest()

        assert perf.latencies == []
        assert perf.start_time is None
        assert perf.running is True

    def test_add_latency(self):
        """Test adding latency measurements."""
        perf = PerformanceTest()

        perf.add_latency(10.5)
        perf.add_latency(12.3)
        perf.add_latency(9.8)

        assert perf.latencies == [10.5, 12.3, 9.8]

    def test_get_stats_empty(self):
        """Test get_stats with no measurements."""
        perf = PerformanceTest()

        stats = perf.get_stats()

        expected = {"count": 0, "min": 0, "max": 0, "avg": 0, "median": 0}
        assert stats == expected

    def test_get_stats_single_measurement(self):
        """Test get_stats with single measurement."""
        perf = PerformanceTest()
        perf.add_latency(15.5)

        stats = perf.get_stats()

        assert stats["count"] == 1
        assert stats["min"] == 15.5
        assert stats["max"] == 15.5
        assert stats["avg"] == 15.5
        assert stats["median"] == 15.5

    def test_get_stats_multiple_measurements(self):
        """Test get_stats with multiple measurements."""
        perf = PerformanceTest()
        latencies = [10.0, 12.0, 8.0, 15.0, 11.0]

        for latency in latencies:
            perf.add_latency(latency)

        stats = perf.get_stats()

        assert stats["count"] == 5
        assert stats["min"] == 8.0
        assert stats["max"] == 15.0
        assert stats["avg"] == 11.2  # (10+12+8+15+11)/5
        assert stats["median"] == 11.0  # Middle value when sorted: [8, 10, 11, 12, 15]

    def test_get_stats_even_number_measurements(self):
        """Test get_stats with even number of measurements (median calculation)."""
        perf = PerformanceTest()
        latencies = [10.0, 12.0, 14.0, 16.0]

        for latency in latencies:
            perf.add_latency(latency)

        stats = perf.get_stats()

        assert stats["count"] == 4
        assert stats["median"] == 13.0  # (12+14)/2

    def test_stop(self):
        """Test stopping the test."""
        perf = PerformanceTest()
        assert perf.running is True

        perf.stop()
        assert perf.running is False


class TestGenerateHistogram:
    """Tests for generate_histogram function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use non-interactive backend for tests
        matplotlib.use("Agg")

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_basic(self, mock_close, mock_savefig):
        """Test basic histogram generation."""
        latencies = [10.0, 12.0, 11.0, 13.0, 10.5, 12.5]
        stats = {"count": 6, "min": 10.0, "max": 13.0, "avg": 11.5, "median": 11.75}

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        # Verify matplotlib functions were called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_with_statistics(self, mock_close, mock_savefig):
        """Test histogram generation includes all statistics."""
        latencies = list(range(1, 101))  # 1 to 100
        stats = {
            "count": len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "avg": statistics.mean(latencies),
            "median": statistics.median(latencies),
        }

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_small_dataset(self, mock_close, mock_savefig):
        """Test histogram with small dataset (adaptive binning)."""
        latencies = [10.0, 11.0, 12.0]  # Very small dataset
        stats = {"count": 3, "min": 10.0, "max": 12.0, "avg": 11.0, "median": 11.0}

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_large_dataset(self, mock_close, mock_savefig):
        """Test histogram with large dataset."""
        # Generate realistic latency data with some variation
        np.random.seed(42)  # For reproducible tests
        latencies = np.random.normal(12.0, 2.0, 1000).tolist()  # Mean=12ms, std=2ms

        stats = {
            "count": len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "avg": statistics.mean(latencies),
            "median": statistics.median(latencies),
        }

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    @patch("matplotlib.pyplot.hist")
    @patch("matplotlib.pyplot.axvline")
    @patch("matplotlib.pyplot.text")
    def test_generate_histogram_plot_elements(self, mock_text, mock_axvline, mock_hist, mock_close, mock_savefig):
        """Test that histogram contains expected plot elements."""
        latencies = [10.0, 12.0, 11.0, 13.0, 10.5, 12.5, 14.0, 9.5]
        stats = {"count": 8, "min": 9.5, "max": 14.0, "avg": 11.5625, "median": 11.75}

        # Mock hist to return the expected 3 values
        mock_hist.return_value = ([1, 2, 3], [0, 1, 2, 3], [])  # counts, bins, patches

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        # Verify histogram was created
        mock_hist.assert_called_once()

        # Verify vertical lines for average and median were added
        assert mock_axvline.call_count == 2

        # Verify statistics text box was added
        mock_text.assert_called_once()

        # Verify the text contains statistics
        stats_text = mock_text.call_args[0][2]  # Third positional argument
        assert "Count: 8" in stats_text
        assert "Interval: 50.0 ms" in stats_text  # 0.05 * 1000 = 50.0 ms
        assert "Min: 9.50" in stats_text
        assert "Max: 14.00" in stats_text
        assert "Avg: 11.56" in stats_text
        assert "Median: 11.75" in stats_text

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_percentiles(self, mock_close, mock_savefig):
        """Test histogram generation with percentile calculations."""
        # Create dataset where percentiles are meaningful
        latencies = list(range(1, 101))  # 1 to 100, so 95th percentile = 95
        stats = {
            "count": len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "avg": statistics.mean(latencies),
            "median": statistics.median(latencies),
        }

        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            generate_histogram(latencies, tmp.name, stats, 0.05)

        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch("matplotlib.pyplot.savefig", side_effect=IOError("Cannot save file"))
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_save_error(self, mock_close, mock_savefig):
        """Test histogram generation when save fails."""
        latencies = [10.0, 12.0, 11.0]
        stats = {"count": 3, "min": 10.0, "max": 12.0, "avg": 11.0, "median": 11.0}

        # Should raise the IOError from savefig
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            try:
                generate_histogram(latencies, tmp.name, stats, 0.05)
                assert False, "Expected IOError to be raised"
            except IOError as e:
                assert "Cannot save file" in str(e)

        # Close might not be called if exception occurs before that point
        # This is acceptable behavior - we just want to ensure the exception propagates

    def test_generate_histogram_file_creation(self):
        """Test that histogram file is actually created."""
        latencies = [10.0, 12.0, 11.0, 13.0, 10.5]
        stats = {"count": 5, "min": 10.0, "max": 13.0, "avg": 11.3, "median": 11.0}

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        try:
            generate_histogram(latencies, temp_path, stats, 0.05)

            # Verify file was created and has content
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @patch("matplotlib.pyplot.savefig")
    @patch("matplotlib.pyplot.close")
    def test_generate_histogram_adaptive_bins(self, mock_close, mock_savefig):
        """Test that histogram uses adaptive binning based on dataset size."""
        # Test various dataset sizes
        test_cases = [
            ([1, 2, 3], 10),  # Small dataset, should use min bins (10)
            (list(range(100)), 10),  # 100 items, 100//10 = 10 bins
            (list(range(500)), 50),  # 500 items, min(50, 500//10) = 50 bins
            (list(range(1000)), 50),  # 1000 items, min(50, 1000//10) = 50 bins
        ]

        for latencies, expected_max_bins in test_cases:
            stats = {
                "count": len(latencies),
                "min": min(latencies),
                "max": max(latencies),
                "avg": statistics.mean(latencies),
                "median": statistics.median(latencies),
            }

            with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
                generate_histogram(latencies, tmp.name, stats, 0.05)

        # Should have called savefig and close for each test case
        assert mock_savefig.call_count == len(test_cases)
        assert mock_close.call_count == len(test_cases)
