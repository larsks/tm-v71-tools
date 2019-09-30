from marshmallow import Schema
from marshmallow.fields import Field, String, Float, Boolean, Integer
from marshmallow.validate import OneOf
from marshmallow_enum import EnumField
from enum import Enum

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

DCS_FREQUENCY = [
    0,
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


class ShiftDirection(Enum):
    SIMPLEX = '0'
    UP = '1'
    DOWN = '2'
    SPLIT = '3'


class RadioSchema(Schema):
    def from_tuple(self, values):
        '''Read in values from a tuple

        Order of items in tuple must match order of declared fields
        for this schema.'''

        return self.load(dict(zip(self.declared_fields, values)))

    def to_tuple(self, obj):
        '''Convert object to a tuple'''

        data = self.dump(obj)
        return [data[f] for f in self.declared_fields]

    def from_csv(self, s):
        '''Read in values from a comma-separated string'''

        return self.from_tuple(s.split(','))

    def to_csv(self, obj):
        '''Convert object to a comma-separated string'''

        return ','.join(self.to_tuple(obj))


class Mode(Enum):
    FM = '0'
    AM = '1'
    NFM = '2'


class Indexed(Field):
    def __init__(self, values, fmt='{}', **kwargs):
        super().__init__(**kwargs)
        self.values = values
        self.fmt = fmt

    def _serialize(self, value, attr, obj, **kwargs):
        return self.fmt.format(self.values.index(value))

    def _deserialize(self, value, attr, data, **kwargs):
        return self.values[int(value)]


class RadioFloat(Float):
    def __init__(self, length=10, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            value = 0

        fmt = '{:0' + str(self.length) + 'd}'
        return fmt.format(int(value * 1000000))

    def _deserialize(self, value, attr, data, **kwargs):
        return int(value) / 1000000.0


class RadioBoolean(Boolean):
    def _serialize(self, value, attr, obj, **kwargs):
        return '1' if value else '0'


class FormattedInteger(Integer):
    def __init__(self, fmt='{}', **kwargs):
        super().__init__(**kwargs)
        self.fmt = fmt

    def _serialize(self, value, attr, obj, **kwargs):
        return self.fmt.format(value)


class ME_Schema(RadioSchema):
    channel = FormattedInteger('{:03d}', required=True)
    rx_freq = RadioFloat(required=True)
    step = Indexed(values=STEP_SIZE, required=True)
    shift = EnumField(ShiftDirection, by_value=True, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True)
    dcs_freq = Indexed(values=DCS_FREQUENCY, required=True, fmt='{:03d}')
    offset = RadioFloat(length=8, required=True)
    mode = EnumField(Mode, by_value=True, required=True)
    tx_freq = RadioFloat(required=True)
    unknown = String(missing='0')
    lockout = RadioBoolean(required=True)


class FO_Schema(RadioSchema):
    band = FormattedInteger(required=True)
    rx_freq = RadioFloat(required=True)
    step = Indexed(values=STEP_SIZE, required=True)
    shift = EnumField(ShiftDirection, by_value=True, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True)
    dcs_freq = Indexed(values=DCS_FREQUENCY, required=True)
    offset = RadioFloat(length=8, required=True)
    mode = EnumField(Mode, by_value=True, required=True)


class CC_Schema(RadioSchema):
    index = Integer(required=True)
    rx_freq = RadioFloat(required=True)
    step = Indexed(values=STEP_SIZE, required=True)
    shift = EnumField(ShiftDirection, by_value=True, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True)
    dcs_freq = Indexed(values=DCS_FREQUENCY, required=True)
    offset = RadioFloat(length=8, required=True)
    mode = EnumField(Mode, by_value=True, required=True)
    tx_freq = RadioFloat(required=True)
    unknown = String(missing='0')


class TY_Schema(RadioSchema):
    model = String(validate=OneOf('K', 'M'))
    mars_tx_expansion = Integer()
    max_tx_expansion = Integer()
    crossband = Integer()
    skycommand = Integer()


# Dynamically create instances of each schema

_classes = list(locals().values())
_globals = globals()
for cls in _classes:
    name = getattr(cls, '__name__', None)
    if name and name.endswith('_Schema'):
        varname = name[:-7]
        _globals[varname] = cls()
