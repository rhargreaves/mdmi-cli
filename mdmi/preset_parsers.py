"""Preset parsers for WOPN, DMP, and TFI formats."""

from dataclasses import dataclass
from typing import List, Optional
import io

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
    dt: int  # Detune
    ar: int  # Attack Rate
    rs: int  # Rate Scaling
    dr: int  # Decay Rate
    am: int  # Amplitude Modulation
    sl: int  # Sustain Level
    sr: int  # Sustain Rate
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
    if len(data) >= 12 and data.startswith(b"WOPN2-B2NK\x00"):
        return "WOPN"
    elif len(data) >= 4 and data.startswith(b".DMP"):
        return "DMP"
    elif len(data) == 42:
        return "TFI"
    elif len(data) > 0 and data[0] in [8, 9, 11]:
        # DMP files can start directly with version byte (8, 9, or 11)
        return "DMP"
    else:
        return "UNKNOWN"


def _convert_fm_operator(fm_op) -> FMOperator:
    """Convert FmOperator to MDMI-compatible FMOperator."""
    return FMOperator(
        mul=getattr(fm_op, "mul", 0),
        dt=getattr(fm_op, "dt", 0),
        ar=getattr(fm_op, "ar", 0),
        rs=getattr(fm_op, "rs", 0),
        dr=getattr(fm_op, "dr", 0),
        am=getattr(fm_op, "am", 0),
        sl=getattr(fm_op, "sl", 0),
        sr=getattr(fm_op, "sr", 0),
        rr=getattr(fm_op, "rr", 0),
        tl=getattr(fm_op, "tl", 0),
        ssg=getattr(fm_op, "ssg", 0),
    )


def parse_preset(data: bytes, format_type: str, **kwargs) -> Preset:
    """Parse preset data using the appropriate parser."""
    if format_type == "WOPN":
        # Use BytesIO instead of temporary file
        file_obj = io.BytesIO(data)
        wopn = parse_wopn(file_obj, name="wopn_data")

        # Extract specific instrument if requested
        bank_index = kwargs.get("bank", 0)
        instrument_index = kwargs.get("instrument", 0)
        bank_type = kwargs.get("bank_type", "melody")  # 'melody' or 'percussion'

        banks = wopn.m_banks if bank_type == "melody" else wopn.p_banks

        if bank_index >= len(banks):
            raise PresetParseError(f"Bank {bank_index} not found")

        bank = banks[bank_index]
        if instrument_index >= len(bank.instruments):
            raise PresetParseError(f"Instrument {instrument_index} not found in bank {bank_index}")

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

    elif format_type == "DMP":
        # Use BytesIO instead of temporary file
        file_obj = io.BytesIO(data)
        dmp = parse_dmp(file_obj, name="dmp_data")

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

    elif format_type == "TFI":
        # Use BytesIO instead of temporary file
        file_obj = io.BytesIO(data)
        tfi = parse_tfi(file_obj, name="tfi_data")

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
    else:
        raise PresetParseError(f"Unsupported format: {format_type}")


def list_wopn_contents(data: bytes) -> dict:
    """List WOPN bank and instrument contents for selection."""
    # Use BytesIO instead of temporary file
    file_obj = io.BytesIO(data)
    wopn = parse_wopn(file_obj, name="wopn_data")

    contents = {"melody_banks": [], "percussion_banks": []}

    # List melody banks
    for i, bank in enumerate(wopn.m_banks):
        bank_info = {"index": i, "name": bank.name, "instruments": []}
        for j, instrument in enumerate(bank.instruments):
            if instrument.name.strip():  # Skip empty instruments
                bank_info["instruments"].append({"index": j, "name": instrument.name})
        contents["melody_banks"].append(bank_info)

    # List percussion banks
    for i, bank in enumerate(wopn.p_banks):
        bank_info = {"index": i, "name": bank.name, "instruments": []}
        for j, instrument in enumerate(bank.instruments):
            if instrument.name.strip():  # Skip empty instruments
                bank_info["instruments"].append({"index": j, "name": instrument.name})
        contents["percussion_banks"].append(bank_info)

    return contents


def parse_dump_response(sysex_data: bytes) -> Preset:
    """Parse MDMI dump response SysEx into a Preset object.

    Args:
        sysex_data: Complete SysEx response from MDMI (F0 00 22 77 0E ...)

    Returns:
        Preset object containing the dumped data

    Raises:
        PresetParseError: If the SysEx data is invalid
    """
    if len(sysex_data) < 8:
        raise PresetParseError("SysEx too short for dump response")

    # Verify it's a valid MDMI dump response
    if sysex_data[0] != 0xF0 or sysex_data[1:4] != bytes([0x00, 0x22, 0x77]) or sysex_data[4] != 0x0E:
        raise PresetParseError("Invalid MDMI dump response SysEx")

    if sysex_data[-1] != 0xF7:
        raise PresetParseError("SysEx not properly terminated")

    # Extract preset data
    preset_type = sysex_data[5]  # Should be 0 for FM
    program = sysex_data[6]

    if preset_type != 0:
        raise PresetParseError(f"Unsupported preset type: {preset_type}")

    # Parse FM parameters - expect at least 4 global + 44 operator bytes
    if len(sysex_data) < 8 + 4 + 44:
        raise PresetParseError("Insufficient data for FM preset")

    data_start = 7
    algorithm = sysex_data[data_start]
    feedback = sysex_data[data_start + 1]
    lfo_ams = sysex_data[data_start + 2]
    lfo_fms = sysex_data[data_start + 3]

    # Parse 4 operators (11 bytes each)
    operators = []
    op_start = data_start + 4

    for i in range(4):
        op_offset = op_start + (i * 11)
        if op_offset + 11 > len(sysex_data) - 1:  # -1 for F7
            raise PresetParseError(f"Insufficient data for operator {i}")

        op_data = sysex_data[op_offset : op_offset + 11]
        operator = FMOperator(
            mul=op_data[0],
            dt=op_data[1],
            ar=op_data[2],
            rs=op_data[3],
            dr=op_data[4],
            am=op_data[5],
            sl=op_data[6],
            sr=op_data[7],
            rr=op_data[8],
            tl=op_data[9],
            ssg=op_data[10],
        )
        operators.append(operator)

    return Preset(
        format_type=None,
        name=f"Preset_{program:03d}",
        algorithm=algorithm,
        feedback=feedback,
        lfo_ams=lfo_ams,
        lfo_fms=lfo_fms,
        operators=operators,
    )


def parse_channel_dump_response(sysex_data: bytes) -> Preset:
    """Parse MDMI channel dump response SysEx into a Preset object.

    Args:
        sysex_data: Complete SysEx response from MDMI (F0 00 22 77 10 ...)

    Returns:
        Preset object containing the dumped channel data

    Raises:
        PresetParseError: If the SysEx data is invalid
    """
    if len(sysex_data) < 8:
        raise PresetParseError("SysEx too short for channel dump response")

    # Verify it's a valid MDMI channel dump response (command 0x10)
    if sysex_data[0] != 0xF0 or sysex_data[1:4] != bytes([0x00, 0x22, 0x77]) or sysex_data[4] != 0x10:
        raise PresetParseError("Invalid MDMI channel dump response SysEx")

    if sysex_data[-1] != 0xF7:
        raise PresetParseError("SysEx not properly terminated")

    # Extract channel data
    preset_type = sysex_data[5]  # Should be 0 for FM
    midi_channel = sysex_data[6]

    if preset_type != 0:
        raise PresetParseError(f"Unsupported channel type: {preset_type}")

    # Parse FM parameters - expect at least 4 global + 44 operator bytes
    if len(sysex_data) < 8 + 4 + 44:
        raise PresetParseError("Insufficient data for FM channel")

    data_start = 7
    algorithm = sysex_data[data_start]
    feedback = sysex_data[data_start + 1]
    lfo_ams = sysex_data[data_start + 2]
    lfo_fms = sysex_data[data_start + 3]

    # Parse 4 operators (11 bytes each)
    operators = []
    op_start = data_start + 4

    for i in range(4):
        op_offset = op_start + (i * 11)
        if op_offset + 11 > len(sysex_data) - 1:  # -1 for F7
            raise PresetParseError(f"Insufficient data for operator {i}")

        op_data = sysex_data[op_offset : op_offset + 11]
        operator = FMOperator(
            mul=op_data[0],
            dt=op_data[1],
            ar=op_data[2],
            rs=op_data[3],
            dr=op_data[4],
            am=op_data[5],
            sl=op_data[6],
            sr=op_data[7],
            rr=op_data[8],
            tl=op_data[9],
            ssg=op_data[10],
        )
        operators.append(operator)

    return Preset(
        format_type=None,
        name=f"Channel_{midi_channel:02d}",
        algorithm=algorithm,
        feedback=feedback,
        lfo_ams=lfo_ams,
        lfo_fms=lfo_fms,
        operators=operators,
    )


def write_dmp_preset(preset: Preset, output_path: str) -> None:
    """Write a Preset object to a DMP file.

    Args:
        preset: Preset object to write
        output_path: Path to write the DMP file

    Raises:
        ValueError: If preset has insufficient operator data
    """
    if len(preset.operators) < 4:
        raise ValueError("DMP format requires 4 operators")

    with open(output_path, "wb") as f:
        # Write DMP data without header (version starts directly)
        # Version 11 (supports system type)
        f.write(bytes([11]))

        # System type (1 = Genesis/Mega Drive)
        f.write(bytes([1]))

        # Instrument mode (1 = FM)
        f.write(bytes([1]))

        # Write FM parameters
        f.write(bytes([preset.lfo_fms]))
        f.write(bytes([preset.feedback]))
        f.write(bytes([preset.algorithm]))
        f.write(bytes([preset.lfo_ams]))

        # Write operators in DMP order (1, 3, 2, 4 -> 0, 2, 1, 3)
        dmp_order = [0, 2, 1, 3]
        for op_idx in dmp_order:
            op = preset.operators[op_idx]
            # DMP operator format: mul, tl, ar, dr, sl, rr, am, rs, dt, sr, ssg
            f.write(
                bytes(
                    [
                        op.mul,
                        op.tl,
                        op.ar,
                        op.dr,
                        op.sl,
                        op.rr,
                        op.am,
                        op.rs,
                        op.dt,
                        op.sr,
                        op.ssg,
                    ]
                )
            )


def write_tfi_preset(preset: Preset, output_path: str) -> None:
    """Write a Preset object to a TFI file.

    Args:
        preset: Preset object to write
        output_path: Path to write the TFI file

    Raises:
        ValueError: If preset has insufficient operator data
    """
    if len(preset.operators) < 4:
        raise ValueError("TFI format requires 4 operators")

    with open(output_path, "wb") as f:
        # Write algorithm and feedback
        f.write(bytes([preset.algorithm]))
        f.write(bytes([preset.feedback]))

        # Write 4 operators (10 bytes each)
        for op in preset.operators:
            # TFI operator format: MUL, DT, TL, RS, AR, DR, SR, RR, SL, SSG
            f.write(
                bytes(
                    [
                        op.mul,
                        op.dt,
                        op.tl,
                        op.rs,
                        op.ar,
                        op.dr,
                        op.sr,
                        op.rr,
                        op.sl,
                        op.ssg,
                    ]
                )
            )
