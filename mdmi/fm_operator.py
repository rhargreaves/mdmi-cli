"""FM operator class for YM2612 parameters."""


class FmOperator:
    """FM operator with YM2612 parameters."""

    def __init__(self, dt=0, mul=0, tl=0, rs=0, ar=0, am=0, dr=0, sr=0, sl=0, rr=0, ssg=0):
        self.dt = dt
        self.mul = mul
        self.tl = tl
        self.rs = rs
        self.ar = ar
        self.am = am
        self.dr = dr
        self.sr = sr
        self.sl = sl
        self.rr = rr
        self.ssg = ssg

    def __str__(self):
        return (
            f"DT:{self.dt} MUL:{self.mul} TL:{self.tl} RS:{self.rs} AR:{self.ar}"
            + f"AM:{self.am} DR:{self.dr} SR:{self.sr} SL:{self.sl} RR:{self.rr} SSG:{self.ssg}"
        )
