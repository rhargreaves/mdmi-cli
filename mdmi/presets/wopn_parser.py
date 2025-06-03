from bitstruct import unpack, unpack_dict
from ..fm_operator import FmOperator
from .wopn import Wopn
from .wopn_bank import WopnBank
from .wopn_instrument import WopnInstrument


def parse_wopn(filename):
    p = Wopn()
    with open(filename, "rb") as f:
        p.name = filename
        p.magic_number = unpack('t80p8', f.read(11))[0]
        if p.magic_number == 'WOPN2-B2NK':
            p.version = unpack('u16<', f.read(2))[0]
        else:
            p.version = 1
        p.m_bank_count, p.p_bank_count, p.lfo_enable, p.lfo_freq = unpack(
            'u16u16p4b1u3', f.read(5))
        if p.version >= 2:
            p.m_banks = read_banks(p.m_bank_count, f)
            p.p_banks = read_banks(p.p_bank_count, f)
        for bank in p.m_banks:
            for _ in range(128):
                bank.instruments.append(read_instrument(f))
        for bank in p.p_banks:
            for _ in range(128):
                bank.instruments.append(read_instrument(f))
    return p


def read_instrument(f):
    name, key_offset, percussion_key, feedback, algorithm, lfo_ams, lfo_fms = unpack(
        't248p8' + 'u16u8' + 'p2u3u3' + 'p2u2p1u3', f.read(37))
    instrument = WopnInstrument(name.rstrip('\0'), key_offset,
                                percussion_key, feedback, algorithm, lfo_ams, lfo_fms)
    op1 = read_operator(f)
    op3 = read_operator(f)
    op2 = read_operator(f)
    op4 = read_operator(f)
    instrument.operators.append(op1)
    instrument.operators.append(op2)
    instrument.operators.append(op3)
    instrument.operators.append(op4)
    skip_over_delay_data(f)
    return instrument


def read_operator(f):
    return FmOperator(** unpack_dict(
        'p1u3u4' + 'p1u7' + 'u2p1u5' + 'u1p2u5' + 'p3u5' + 'u4u4' + 'p4u4',
        ['dt', 'mul', 'tl', 'rs', 'ar', 'am', 'dr',
         'd2r', 'sl', 'rr', 'ssg'], f.read(7)))


def skip_over_delay_data(f):
    f.read(4)


def read_banks(bank_count, f):
    banks = []
    for _ in range(bank_count):
        name, index = unpack("t256u16", f.read(34))
        banks.append(WopnBank(name.rstrip('\0'), index))
    return banks
