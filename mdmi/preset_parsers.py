"""Preset parsers for WOPN, DMP, and TFI formats."""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

from .presets.wopn_parser import parse_wopn
from .presets.dmp_parser import parse_dmp
from .presets.tfi_parser import parse_tfi


class PresetParseError(Exception):
    """Exception raised when preset parsing fails."""

    pass


@dataclass
class FMOperator:
    """FM operator parameters compatible with MDMI SysEx."""

    mul: int  # Multiple
    dt1: int  # Detune 1 (mapped from dt)
    ar: int  # Attack Rate
    rs: int  # Rate Scaling
    d1r: int  # Decay 1 Rate (mapped from dr)
    am: int  # Amplitude Modulation
    d1l: int  # Decay 1 Level (mapped from sl)
    d2r: int  # Decay 2 Rate
    rr: int  # Release Rate
    tl: int  # Total Level
    ssg: int  # SSG-EG


@dataclass
class Preset:
    """Base preset class compatible with MDMI SysEx."""

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


def _convert_fm_operator(fm_op) -> FMOperator:
    """Convert FmOperator to MDMI-compatible FMOperator."""
    return FMOperator(
        mul=getattr(fm_op, "mul", 0),
        dt1=getattr(fm_op, "dt", 0),  # Map dt to dt1
        ar=getattr(fm_op, "ar", 0),
        rs=getattr(fm_op, "rs", 0),
        d1r=getattr(fm_op, "dr", 0),  # Map dr to d1r
        am=getattr(fm_op, "am", 0),
        d1l=getattr(fm_op, "sl", 0),  # Map sl to d1l
        d2r=getattr(fm_op, "d2r", 0),
        rr=getattr(fm_op, "rr", 0),
        tl=getattr(fm_op, "tl", 0),
        ssg=getattr(fm_op, "ssg", 0),
    )


def parse_preset(data: bytes, format_type: str, **kwargs) -> Preset:
    """Parse preset data using the appropriate parser."""
    if format_type == "WOPN":
        # For WOPN, we need to write to temp file for file-based parser
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wopn", delete=False) as f:
            f.write(data)
            temp_filename = f.name

        try:
            wopn = parse_wopn(temp_filename)

            # Extract specific instrument if requested
            bank_index = kwargs.get("bank", 0)
            instrument_index = kwargs.get("instrument", 0)
            bank_type = kwargs.get("bank_type", "melody")  # 'melody' or 'percussion'

            banks = wopn.m_banks if bank_type == "melody" else wopn.p_banks

            if bank_index >= len(banks):
                raise PresetParseError(f"Bank {bank_index} not found")

            bank = banks[bank_index]
            if instrument_index >= len(bank.instruments):
                raise PresetParseError(
                    f"Instrument {instrument_index} not found in bank {bank_index}"
                )

            instrument = bank.instruments[instrument_index]

            # Convert to MDMI format
            operators = [_convert_fm_operator(op) for op in instrument.operators]

            preset = Preset(
                format_type="WOPN",
                name=instrument.name,
                algorithm=instrument.algorithm,
                feedback=instrument.feedback,
                lfo_ams=instrument.lfo_ams,
                lfo_fms=instrument.lfo_fms,
                operators=operators,
                melody_banks=len(wopn.m_banks),
                percussion_banks=len(wopn.p_banks),
            )
            return preset

        finally:
            import os

            os.unlink(temp_filename)

    elif format_type == "DMP":
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".dmp", delete=False) as f:
            f.write(data)
            temp_filename = f.name

        try:
            dmp = parse_dmp(temp_filename)

            # Convert operators if they exist
            operators = []
            if hasattr(dmp, "operators") and dmp.operators:
                operators = [_convert_fm_operator(op) for op in dmp.operators]

            preset = Preset(
                format_type="DMP",
                name=dmp.name,
                version=getattr(dmp, "version", None),
                algorithm=getattr(dmp, "algorithm", 0),
                feedback=getattr(dmp, "feedback", 0),
                lfo_ams=getattr(dmp, "lfo_ams", 0),
                lfo_fms=getattr(dmp, "lfo_fms", 0),
                operators=operators,
                system=getattr(dmp, "system_type", None),
            )
            return preset

        finally:
            import os

            os.unlink(temp_filename)

    elif format_type == "TFI":
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".tfi", delete=False) as f:
            f.write(data)
            temp_filename = f.name

        try:
            tfi = parse_tfi(temp_filename)

            # Convert operators
            operators = [_convert_fm_operator(op) for op in tfi.operators]

            preset = Preset(
                format_type="TFI",
                name=tfi.name,
                algorithm=tfi.algorithm,
                feedback=tfi.feedback,
                lfo_ams=getattr(tfi, "lfo_ams", 0),
                lfo_fms=getattr(tfi, "lfo_fms", 0),
                operators=operators,
                fm_parameters=data,
            )
            return preset

        finally:
            import os

            os.unlink(temp_filename)
    else:
        raise PresetParseError(f"Unsupported format: {format_type}")


def list_wopn_contents(data: bytes) -> dict:
    """List WOPN bank and instrument contents for selection."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wopn", delete=False) as f:
        f.write(data)
        temp_filename = f.name

    try:
        wopn = parse_wopn(temp_filename)

        contents = {"melody_banks": [], "percussion_banks": []}

        # List melody banks
        for i, bank in enumerate(wopn.m_banks):
            bank_info = {"index": i, "name": bank.name, "instruments": []}
            for j, instrument in enumerate(bank.instruments):
                if instrument.name.strip():  # Skip empty instruments
                    bank_info["instruments"].append(
                        {"index": j, "name": instrument.name}
                    )
            contents["melody_banks"].append(bank_info)

        # List percussion banks
        for i, bank in enumerate(wopn.p_banks):
            bank_info = {"index": i, "name": bank.name, "instruments": []}
            for j, instrument in enumerate(bank.instruments):
                if instrument.name.strip():  # Skip empty instruments
                    bank_info["instruments"].append(
                        {"index": j, "name": instrument.name}
                    )
            contents["percussion_banks"].append(bank_info)

        return contents

    finally:
        import os

        os.unlink(temp_filename)
