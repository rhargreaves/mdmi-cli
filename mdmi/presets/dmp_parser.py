from .dmp import Dmp
from ..fm_operator import FmOperator
from bitstruct import unpack_dict
from ..util import extract_name, read_byte


def parse_dmp(filename):
    with open(filename, "rb") as f:
        version = read_byte(f)
        system_type = None  # Initialize to None by default

        if version == 8 or version == 9:
            instrument_mode = read_byte(f)
            read_byte(f)  # unknown
        elif version == 11:
            system_type = read_byte(f)
            instrument_mode = read_byte(f)
        else:
            # Handle unknown versions gracefully
            instrument_mode = 0

        dmp = Dmp(extract_name(filename), version, system_type, instrument_mode)
        if instrument_mode == 1:
            dmp.lfo_fms = read_byte(f)
            dmp.feedback = read_byte(f)
            dmp.algorithm = read_byte(f)
            dmp.lfo_ams = read_byte(f)
            ops = []
            for _ in range(4):
                ops.append(parse_operator(f))
            dmp.operators.append(ops[0])
            dmp.operators.append(ops[2])
            dmp.operators.append(ops[1])
            dmp.operators.append(ops[3])
        return dmp


def parse_operator(f):
    return FmOperator(
        **unpack_dict(
            "u8u8u8u8u8u8u8u8u8u8u8",
            ["mul", "tl", "ar", "dr", "sl", "rr", "am", "rs", "dt", "d2r", "ssg"],
            f.read(11),
        )
    )
