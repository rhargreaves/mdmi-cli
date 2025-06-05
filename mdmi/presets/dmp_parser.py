from .dmp import Dmp
from ..fm_operator import FmOperator
from bitstruct import unpack_dict
from ..util import read_byte


def parse_dmp(file_obj, name="dmp_data"):
    """Parse DMP data from a file-like object."""
    version = read_byte(file_obj)
    system_type = None  # Initialize to None by default

    if version == 8 or version == 9:
        instrument_mode = read_byte(file_obj)
        read_byte(file_obj)  # unknown
    elif version == 11:
        system_type = read_byte(file_obj)
        instrument_mode = read_byte(file_obj)
    else:
        # Handle unknown versions gracefully
        instrument_mode = 0

    dmp = Dmp(name, version, system_type, instrument_mode)
    if instrument_mode == 1:
        dmp.lfo_fms = read_byte(file_obj)
        dmp.feedback = read_byte(file_obj)
        dmp.algorithm = read_byte(file_obj)
        dmp.lfo_ams = read_byte(file_obj)
        ops = []
        for _ in range(4):
            ops.append(parse_operator(file_obj))
        dmp.operators.append(ops[0])
        dmp.operators.append(ops[2])
        dmp.operators.append(ops[1])
        dmp.operators.append(ops[3])
    return dmp


def parse_operator(f):
    return FmOperator(
        **unpack_dict(
            "u8u8u8u8u8u8u8u8u8u8u8",
            ["mul", "tl", "ar", "dr", "sl", "rr", "am", "rs", "dt", "sr", "ssg"],
            f.read(11),
        )
    )
