"""Preset parsers for WOPN, DMP, and TFI formats."""

from dataclasses import dataclass
from typing import List, Optional


class PresetParseError(Exception):
    """Exception raised when preset parsing fails."""

    pass


@dataclass
class FMOperator:
    """FM operator parameters."""

    mul: int  # Multiple
    dt1: int  # Detune 1
    ar: int  # Attack Rate
    rs: int  # Rate Scaling
    d1r: int  # Decay 1 Rate
    am: int  # Amplitude Modulation
    d1l: int  # Decay 1 Level
    d2r: int  # Decay 2 Rate
    rr: int  # Release Rate
    tl: int  # Total Level
    ssg: int  # SSG-EG


@dataclass
class Preset:
    """Base preset class."""

    format_type: str
    name: str = ""
    version: Optional[int] = None

    # FM Parameters
    algorithm: int = 0
    feedback: int = 0
    lfo_ams: int = 0
    lfo_fms: int = 0
    operators: List[FMOperator] = None

    # Format-specific fields
    system: Optional[int] = None  # DMP
    melody_banks: Optional[int] = None  # WOPN
    percussion_banks: Optional[int] = None  # WOPN
    fm_parameters: Optional[bytes] = None  # TFI raw data

    def __post_init__(self):
        if self.operators is None:
            self.operators = []


def detect_preset_format(data: bytes) -> str:
    """Detect preset format from data content."""
    if len(data) >= 12 and data.startswith(b"WOPN2-BANK\x00"):
        return "WOPN"
    elif len(data) >= 4 and data.startswith(b".DMP"):
        return "DMP"
    elif len(data) == 42:
        return "TFI"
    else:
        return "UNKNOWN"


def parse_preset(data: bytes, format_type: str) -> Preset:
    """Parse preset data using the appropriate parser."""
    if format_type == "WOPN":
        parser = WOPNParser()
    elif format_type == "DMP":
        parser = DMPParser()
    elif format_type == "TFI":
        parser = TFIParser()
    else:
        raise PresetParseError(f"Unsupported format: {format_type}")

    return parser.parse(data)


class WOPNParser:
    """Parser for WOPN preset files."""

    def parse(self, data: bytes) -> Preset:
        """Parse WOPN format data."""
        if len(data) < 16:
            raise PresetParseError("File too small to be valid WOPN")

        # Check header
        if not data.startswith(b"WOPN2-BANK\x00"):
            raise PresetParseError("Invalid WOPN header")

        # Parse header
        version = data[12]
        if version not in [1, 2]:
            raise PresetParseError(f"Unsupported WOPN version: {version}")

        melody_banks = data[15]
        percussion_banks = data[16]

        preset = Preset(
            format_type="WOPN",
            version=version,
            melody_banks=melody_banks,
            percussion_banks=percussion_banks,
        )

        return preset


class DMPParser:
    """Parser for DMP preset files."""

    def parse(self, data: bytes) -> Preset:
        """Parse DMP format data."""
        if len(data) < 4:
            raise PresetParseError("File too small to be valid DMP")

        # Check signature
        if not data.startswith(b".DMP"):
            raise PresetParseError("Invalid DMP signature")

        if len(data) < 38:  # Minimum size for DMP v11
            raise PresetParseError("DMP file too small")

        version = data[4]
        system = data[5]

        # Extract name (32 bytes, null-terminated)
        name_bytes = data[6:38]
        name = name_bytes.split(b"\x00")[0].decode("utf-8", errors="ignore")

        # Parse FM parameters based on version
        if version == 11 and len(data) >= 49:
            fm_data = data[38:49]  # 11 bytes of FM parameters

            # Extract basic FM parameters
            algorithm = fm_data[0] & 0x07
            feedback = (fm_data[0] >> 3) & 0x07
            lfo_ams = fm_data[1] & 0x03
            lfo_fms = (fm_data[1] >> 4) & 0x07

            preset = Preset(
                format_type="DMP",
                version=version,
                system=system,
                name=name,
                algorithm=algorithm,
                feedback=feedback,
                lfo_ams=lfo_ams,
                lfo_fms=lfo_fms,
            )
        else:
            preset = Preset(
                format_type="DMP",
                version=version,
                system=system,
                name=name,
            )

        return preset


class TFIParser:
    """Parser for TFI preset files."""

    def parse(self, data: bytes) -> Preset:
        """Parse TFI format data."""
        if len(data) != 42:
            raise PresetParseError(
                f"Invalid TFI size: expected 42 bytes, got {len(data)}"
            )

        # TFI format is 42 bytes of FM parameters
        # Extract basic parameters
        algorithm = data[0] & 0x07
        feedback = (data[0] >> 3) & 0x07

        # Parse operators
        operators = []
        for i in range(4):  # 4 operators
            op_offset = 1 + (i * 10)  # Each operator is 10 bytes
            if op_offset + 10 <= len(data):
                operators.append(
                    FMOperator(
                        mul=data[op_offset] & 0x0F,
                        dt1=(data[op_offset] >> 4) & 0x07,
                        ar=data[op_offset + 1] & 0x1F,
                        rs=(data[op_offset + 1] >> 6) & 0x03,
                        d1r=data[op_offset + 2] & 0x1F,
                        am=(data[op_offset + 2] >> 7) & 0x01,
                        d1l=data[op_offset + 3] & 0x0F,
                        d2r=(data[op_offset + 3] >> 4) & 0x0F,
                        rr=data[op_offset + 4] & 0x0F,
                        tl=data[op_offset + 5] & 0x7F,
                        ssg=data[op_offset + 6] & 0x0F,
                    )
                )

        preset = Preset(
            format_type="TFI",
            algorithm=algorithm,
            feedback=feedback,
            operators=operators,
            fm_parameters=data,
        )

        return preset
