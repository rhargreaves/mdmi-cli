"""TFI parser for Texas Instruments FM format."""

from .tfi import Tfi
from ..fm_operator import FmOperator


def parse_tfi(file_obj, name="tfi_data"):
    """Parse TFI data from a file-like object."""
    # Read algorithm and feedback as individual bytes
    algorithm = int.from_bytes(file_obj.read(1), byteorder="little")
    feedback = int.from_bytes(file_obj.read(1), byteorder="little")

    tfi = Tfi(name, algorithm, feedback)

    # Parse 4 operators (10 bytes each)
    for _ in range(4):
        tfi.operators.append(parse_operator(file_obj))
    return tfi


def parse_operator(f):
    # Read 10 bytes for one operator
    data = f.read(10)
    if len(data) < 10:
        # Pad with zeros if not enough data
        data = data + b"\x00" * (10 - len(data))

    # TFI format appears to be: MUL, DT, TL, RS, AR, DR, SR, RR, SL, SSG (1 byte each)
    mul = data[0]
    dt = data[1]
    tl = data[2]
    rs = data[3]
    ar = data[4]
    dr = data[5]
    sr = data[6]
    rr = data[7]
    sl = data[8]
    ssg = data[9]

    return FmOperator(
        mul=mul,
        dt=dt,
        tl=tl,
        rs=rs,
        ar=ar,
        am=0,  # AM not in TFI format
        dr=dr,
        sr=sr,
        sl=sl,
        rr=rr,
        ssg=ssg,
    )
