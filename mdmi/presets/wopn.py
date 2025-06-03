from ..ui import generate_line


class Wopn():
    def __init__(self):
        self.magic_number = None
        self.version = None
        self.m_banks = None
        self.p_banks = None
        self.lfo_enable = None
        self.lfo_freq = None

    def info(self):
        text = 'WOPN\n'
        text = text + 'M_Banks' + "{0:>5}\n".format(len(self.m_banks))
        text = text + 'P_Banks' + "{0:>5}\n".format(len(self.p_banks))
        text = text + 'LFO' + \
            "{0:>9}\n".format('On' if self.lfo_enable else 'Off')
        text = text + 'LFO Freq' + "{0:>4}\n".format(self.lfo_freq)
        for bank_index, bank in enumerate(self.m_banks):
            text = text + self.bank_info(bank, bank_index, 'M')
        for bank_index, bank in enumerate(self.p_banks):
            text = text + self.bank_info(bank, bank_index, 'P')
        return text

    def bank_info(self, bank, bank_index, bank_type):
        text = generate_line('=')
        text = text + bank_type + '. Bank' + \
            "{0:>8}".format(bank_index) + \
            '    ' + bank.name + '\n'
        text = text + generate_line('=')
        for instrument_index, instrument in enumerate(bank.instruments):
            text = text + self.instrument_info(instrument, instrument_index)
        return text

    def instrument_info(self, instrument, instrument_index):
        text = generate_line('=')
        text = text + 'Instrument' + \
            "{0:>5}".format(instrument_index) + \
            '    ' + instrument.name + '\n'
        text = text + generate_line('=')
        text = text + instrument.info()
        return text
