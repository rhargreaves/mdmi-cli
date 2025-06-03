from .tfi import Tfi
from ..fm_operator import FmOperator
from bitstruct import unpack_dict
from ..util import extract_name, read_byte


def parse_tfi(filename):
    with open(filename, "rb") as f:
        tfi = Tfi(extract_name(filename))
        tfi.algorithm = read_byte(f)
        tfi.feedback = read_byte(f)
        tfi.lfo_fms = 0
        tfi.lfo_ams = 0
        ops = []
        for _ in range(4):
            ops.append(parse_operator(f))
        tfi.operators.append(ops[0])
        tfi.operators.append(ops[2])
        tfi.operators.append(ops[1])
        tfi.operators.append(ops[3])
        return tfi


def parse_operator(f):
    d = unpack_dict(
        'u8u8u8u8u8u8u8u8u8u8', ['mul', 'dt', 'tl', 'rs', 'ar', 'dr', 'd2r', 'rr', 'sl',
                                 'ssg', 'am'], f.read(10))
    d['am'] = 0
    return FmOperator(**d)
