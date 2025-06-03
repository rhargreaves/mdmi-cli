"""Utility functions for preset parsing."""

import os


def extract_name(filename):
    """Extract name from filename without extension."""
    return os.path.splitext(os.path.basename(filename))[0]


def read_byte(f):
    """Read a single byte from file and return as int."""
    return int.from_bytes(f.read(1), byteorder="little")
