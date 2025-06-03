from ..preset import Preset


class Dmp(Preset):
    def __init__(self, name, version, system_type, instrument_mode):
        Preset.__init__(self)
        self.version = version
        self.system_type = system_type
        self.instrument_mode = instrument_mode
        self.name = name

    def info(self):
        text = self.dmp_type() + '\n'
        text = text + super(Dmp, self).info()
        return text

    def format_instrument_mode(self, mode):
        return "FM" if mode == 1 else "STD"

    def format_system(self, system_type):
        return "Genesis" if system_type == 2 else "Unknown"

    def dmp_type(self):
        return "{0:<11}{1:<8}{2:<9}{3:<7}".format(
            "Version",
            self.version,
            self.format_instrument_mode(self.instrument_mode),
            self.format_system(self.system_type))
