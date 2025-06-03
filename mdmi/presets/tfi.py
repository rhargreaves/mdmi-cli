from ..preset import Preset


class Tfi(Preset):
    def __init__(self, name, algorithm=0, feedback=0):
        Preset.__init__(self)
        self.name = name
        self.algorithm = algorithm
        self.feedback = feedback

    def info(self):
        return super(Tfi, self).info()
