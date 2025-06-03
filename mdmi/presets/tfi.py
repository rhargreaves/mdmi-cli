from ..preset import Preset


class Tfi(Preset):
    def __init__(self, name):
        Preset.__init__(self)
        self.name = name

    def info(self):
        return super(Tfi, self).info()
