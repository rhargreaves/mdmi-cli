"""Base preset class for FM instruments."""


class Preset:
    """Base preset class for FM instruments."""

    def __init__(self):
        self.name = ""
        self.algorithm = 0
        self.feedback = 0
        self.lfo_ams = 0
        self.lfo_fms = 0
        self.operators = []

    def info(self):
        """Return formatted information about the preset."""
        text = f"Name: {self.name}\n"
        text += f"Algorithm: {self.algorithm}\n"
        text += f"Feedback: {self.feedback}\n"
        text += f"LFO AMS: {self.lfo_ams}\n"
        text += f"LFO FMS: {self.lfo_fms}\n"
        for i, op in enumerate(self.operators):
            text += f"Operator {i + 1}: {op}\n"
        return text
