from ..preset import Preset


class WopnInstrument(Preset):
    def __init__(self, name, key_offset, percussion_key, feedback, algorithm, lfo_ams, lfo_fms):
        Preset.__init__(self)
        self.name = name
        self.key_offset = key_offset
        self.percussion_key = percussion_key
        self.feedback = feedback
        self.algorithm = algorithm
        self.lfo_ams = lfo_ams
        self.lfo_fms = lfo_fms
