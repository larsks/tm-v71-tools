class Response(dict):
    fields = []

    def __init__(self, params):
        super().__init__(zip(self.fields, params))

        for param, value in self.items():
            xform = getattr(self, '{}_out'.format(param), None)
            if xform:
                self[param] = xform(value)

    def as_tuple(self):
        data = []
        for param, value in self.items():
            xform = getattr(self, '{}_in'.format(param), None)
            if xform:
                value = xform(value)

            data.append(value)

        return tuple(data)


class TY_Response(Response):
    fields = [
        'type',
        'mars_cap_tx_expansion',
        'max_tx_expansion',
        'cross_band',
        'sky_command',
    ]


class ME_Response(Response):
    fields = [
        'index',
        'rx_freq',
        'step',
        'shift',
        'reverse',
        'tone_status',
        'ctcss_status',
        'dcs_status',
        'tone_freq',
        'ctcss_freq',
        'dcs_freq',
        'offset',
        'mode',
        'tx_freq',
        'unknown0',
        'lockout'
    ]


class FO_Response(Response):
    fields = [
        'band',
        'rx_freq',
        'step',
        'shift',
        'reverse',
        'tone_status',
        'ctcss_status',
        'dcs_status',
        'tone_freq',
        'ctcss_freq',
        'dcs_freq',
        'offset',
        'mode',
    ]

    def offset_out(self, v):
        return int(v)/1000000.0

    def offset_in(self, v):
        return '{:08d}'.format(int(v * 1000000))

    def tx_freq_out(self, v):
        return int(v)/1000000.0

    def tx_freq_in(self, v):
        return '{:010d}'.format(int(v * 1000000))

    def rx_freq_out(self, v):
        return int(v)/1000000.0

    def rx_freq_in(self, v):
        return '{:010d}'.format(int(v * 1000000))


class CC_Response(Response):
    fields = [
        'index',
        'rx_freq',
        'step',
        'shift',
        'reverse',
        'tone_status',
        'ctcss_status',
        'dcs_status',
        'tone_freq',
        'ctcss_freq',
        'dcs_freq',
        'offset',
        'mode',
        'tx_freq',
        'unknown0',
    ]
