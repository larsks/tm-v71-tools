MODE = ['FM', 'AM', 'NFM']

STEP_SIZE = [
    5,
    6.25,
    28.33,
    10,
    12.5,
    15,
    20,
    25,
    30,
    50,
    100,
]

SHIFT_DIR = ['N', '+', '-', 'S']

TONE_FREQUENCY = [
    0,
    67,
    69.3,
    71.9,
    74.4,
    77,
    79.7,
    82.5,
    85.4,
    88.5,
    91.5,
    94.8,
    97.4,
    100,
    103.5,
    107.2,
    110.9,
    114.8,
    118.8,
    123,
    127.3,
    131.8,
    136.5,
    141.3,
    146.2,
    151.4,
    156.7,
    162.2,
    167.9,
    173.8,
    179.9,
    186.2,
    192.8,
    203.5,
    240.7,
    210.7,
    218.1,
    225.7,
    229.1,
    233.6,
    241.8,
    250.3,
    254.1,
]

CTCSS_FREQUENCY = TONE_FREQUENCY

DCS_FREQUENCY = [
    23,
    25,
    26,
    31,
    32,
    36,
    43,
    47,
    51,
    53,
    54,
    65,
    71,
    72,
    73,
    74,
    114,
    115,
    116,
    122,
    125,
    131,
    132,
    134,
    143,
    145,
    152,
    155,
    156,
    162,
    165,
    172,
    174,
    205,
    212,
    223,
    225,
    226,
    243,
    244,
    245,
    246,
    251,
    252,
    255,
    261,
    263,
    265,
    266,
    271,
    274,
    306,
    311,
    315,
    325,
    331,
    332,
    343,
    346,
    351,
    356,
    364,
    365,
    371,
    411,
    412,
    413,
    423,
    431,
    432,
    445,
    446,
    452,
    454,
    455,
    462,
    464,
    465,
    466,
    503,
    506,
    516,
    523,
    565,
    532,
    546,
    565,
    606,
    612,
    624,
    627,
    631,
    632,
    654,
    662,
    664,
    703,
    712,
    723,
    731,
    732,
    734,
    743,
    754,
]


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


class common_transformations:
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

    def tone_freq_out(self, v):
        return TONE_FREQUENCY[int(v)]

    def tone_freq_in(self, v):
        return TONE_FREQUENCY.index(v)

    def ctcss_freq_out(self, v):
        return CTCSS_FREQUENCY[int(v)]

    def ctcss_freq_in(self, v):
        return CTCSS_FREQUENCY.index(v)

    def dcs_freq_out(self, v):
        return DCS_FREQUENCY[int(v)]

    def dcs_freq_in(self, v):
        return DCS_FREQUENCY.index(v)

    def shift_out(self, v):
        return SHIFT_DIR[int(v)]

    def shift_in(self, v):
        return SHIFT_DIR.index(v)

    def step_out(self, v):
        return STEP_SIZE[int(v)]

    def step_in(self, v):
        return STEP_SIZE.index(v)

    def lockout_out(self, v):
        return int(v) == 1

    def lockout_in(self, v):
        return 1 if v else 0


class ME_Response(Response, common_transformations):
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


class FO_Response(Response, common_transformations):
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
