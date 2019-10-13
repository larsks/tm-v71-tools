from marshmallow import Schema, post_load, pre_dump, validate
from marshmallow.fields import Field, String, Float, Boolean, Integer
from marshmallow.validate import OneOf, Range

BANDS = ['A', 'B']
BAND_MODE = ['VFO', 'MEM', 'CALL', 'WX']
TX_POWER = ['HIGH', 'MED', 'LOW']
ANNOUNCE = ['OFF', 'AUTO', 'MANUAL']
LANGUAGE = ['English', 'Japanese']
SQL_HANG_TIME = ['OFF', '125', '250', '500']
MUTE_HANG_TIME = ['OFF', '125', '250', '500', '750', '1000']
RECALL_METHOD = ['ALL', 'CURRENT']
SPEED = ['FAST', 'SLOW']
DTMF_PAUSE = ['100', '250', '500', '750', '1000', '1500', '2000']
BACKLIGHT_COLOR = ['AMBER', 'GREEN']
KEY_FUNCTIONS = ['WX', 'FREQBAND', 'CTRL', 'MONITOR', 'VGS', 'VOICE',
                 'GROUP_UP', 'MENU', 'MUTE', 'SHIFT', 'DUAL',
                 'MEM_TO_VFO', 'VFO', 'MR', 'CALL', 'MHZ',
                 'TONE', 'REV', 'LOW', 'LOCK', 'A_B', 'ENTER',
                 '1750HZ']
SCAN_RESUME = ['TIME', 'CARRIER', 'SEEK']
APO = ['OFF', '30', '60', '90', '120', '180']
EXT_DATA_BAND = ['A', 'B', 'TXA_RXB', 'TXB_RXA']
EXT_DATA_SPEED = ['1200', '9600']
SQC_SOURCE = ['OFF', 'BUSY', 'SQL', 'TX', 'BUSY_TX', 'SQL_TX']
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
    67.0,
    69.3,
    71.9,
    74.4,
    77.0,
    79.7,
    82.5,
    85.4,
    88.5,
    91.5,
    94.8,
    97.4,
    100.0,
    103.5,
    107.2,
    110.9,
    114.8,
    118.8,
    123.0,
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

DCS_CODE = [
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

SHIFT_DIRECTION = ['SIMPLEX', 'UP', 'DOWN', 'SPLIT']

MODE = ['FM', 'NFM', 'AM']


class SchemaDict(dict):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def items(self):
        return [(k, self[k]) for k in self.schema._declared_fields]


class RadioSchema(Schema):
    def from_tuple(self, values):
        '''Read in values from a tuple

        Order of items in tuple must match order of declared fields
        for this schema.'''

        data = self.load(dict(zip(self.declared_fields, values)))
        return data

    def to_tuple(self, obj, **kwargs):
        '''Convert object to a tuple'''

        data = self.dump(obj, **kwargs)
        return [data[f]
                for f in self.declared_fields
                if f in data]

    def from_csv(self, s):
        '''Read in values from a comma-separated string'''

        return self.from_tuple(s.split(','))

    def to_csv(self, obj, **kwargs):
        '''Convert object to a comma-separated string'''

        return ','.join(self.to_tuple(obj, **kwargs))

    def to_raw_tuple(self, obj):
        return [obj[f] for f in self.declared_fields]

    def from_raw_tuple(self, values):
        return dict(zip(self.declared_fields, values))

    @post_load
    def add_schema(self, data, **kwargs):
        return SchemaDict(self, data)


class Indexed(Field):
    def __init__(self, values, fmt='{}', int_base=10, type=None, **kwargs):
        super().__init__(**kwargs)
        self.values = values
        self.fmt = fmt
        self.int_base = int_base
        self.type = type

    def _serialize(self, value, attr, obj, **kwargs):
        if self.type is not None:
            value = self.type(value)

        return self.fmt.format(self.values.index(value))

    def _deserialize(self, value, attr, data, **kwargs):
        res = self.values[int(value, self.int_base)]
        if self.type is not None:
            res = self.type(res)

        return res


class RadioFloat(Float):
    def __init__(self, length=10, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            value = 0

        fmt = '{:0' + str(self.length) + 'd}'
        return fmt.format(int(float(value) * 1000000))

    def _deserialize(self, value, attr, data, **kwargs):
        return int(value) / 1000000.0


class RadioBoolean(Boolean):
    truthy = [1, '1', 'true', 'True', 'TRUE', True]

    def _serialize(self, value, attr, obj, **kwargs):
        return '1' if value in self.truthy else '0'


class FormattedInteger(Integer):
    def __init__(self, fmt='{}', **kwargs):
        super().__init__(**kwargs)
        self.fmt = fmt

    def _serialize(self, value, attr, obj, **kwargs):
        return self.fmt.format(int(value))


class ME_Schema(RadioSchema):
    channel = FormattedInteger('{:03d}', required=True)
    rx_freq = RadioFloat(required=True)
    step = Indexed(STEP_SIZE, required=True, type=float)
    shift = Indexed(SHIFT_DIRECTION, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True, type=float,
                        default=67)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True, type=float,
                         default=67)
    dcs_code = Indexed(values=DCS_CODE, required=True, fmt='{:03d}', type=int,
                       default=23)
    offset = RadioFloat(length=8, required=True)
    mode = Indexed(MODE, required=True)
    tx_freq = RadioFloat(required=True)
    tx_step = Indexed(STEP_SIZE, required=True, type=float)
    lockout = RadioBoolean(required=True)
    name = String()

    export_fields = (
        'channel', 'rx_freq', 'step', 'shift',
        'reverse', 'admit', 'tone',
        'offset', 'mode', 'tx_freq', 'tx_step',
        'lockout', 'name'
    )

    @post_load
    def compute_admit_load(self, data, **kwargs):
        if data['tone_status']:
            data['admit'] = 'T'
            data['tone'] = data['tone_freq']
        elif data['ctcss_status']:
            data['admit'] = 'C'
            data['tone'] = data['ctcss_freq']
        elif data['dcs_status']:
            data['admit'] = 'D'
            data['tone'] = data['dcs_code']
        else:
            data['admit'] = ''
            data['tone'] = ''

        return data

    @pre_dump
    def compute_admit_dump(self, obj, **kwargs):
        admit = obj['admit']

        obj['tone_status'] = obj['ctcss_status'] = \
            obj['dcs_status'] = False

        if admit == 'T':
            obj['tone_status'] = True
            obj['tone_freq'] = obj['tone']
        elif admit == 'C':
            obj['ctcss_status'] = True
            obj['ctcss_freq'] = obj['tone']
        elif admit == 'D':
            obj['dcs_status'] = True
            obj['dcs_code'] = obj['tone']

        return obj


class FO_Schema(RadioSchema):
    band = FormattedInteger(required=True, validate=Range(0, 1))
    rx_freq = RadioFloat(required=True)
    step = Indexed(values=STEP_SIZE, required=True)
    shift = Indexed(SHIFT_DIRECTION, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True, type=float)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True, type=float)
    dcs_code = Indexed(values=DCS_CODE, required=True, fmt='{:03d}', type=int)
    offset = RadioFloat(length=8, required=True)
    mode = Indexed(MODE, required=True)


class CC_Schema(RadioSchema):
    index = FormattedInteger(required=True)
    rx_freq = RadioFloat(required=True)
    step = Indexed(values=STEP_SIZE, required=True)
    shift = Indexed(SHIFT_DIRECTION, required=True)
    reverse = RadioBoolean(required=True)
    tone_status = RadioBoolean(required=True)
    ctcss_status = RadioBoolean(required=True)
    dcs_status = RadioBoolean(required=True)
    tone_freq = Indexed(values=TONE_FREQUENCY, required=True,
                        fmt='{:02d}', type=float)
    ctcss_freq = Indexed(values=TONE_FREQUENCY, required=True,
                         fmt='{:02d}', type=float)
    dcs_code = Indexed(values=DCS_CODE, required=True, fmt='{:03d}', type=int)
    offset = RadioFloat(length=8, required=True)
    mode = Indexed(MODE, required=True)
    tx_freq = RadioFloat(required=True)
    unknown = String(missing='0')


class TY_Schema(RadioSchema):
    model = String(validate=OneOf('K', 'M'))
    mars_tx_expansion = Integer()
    max_tx_expansion = Integer()
    crossband = Integer()
    skycommand = Integer()


class BC_Schema(RadioSchema):
    ctrl = Integer()
    ptt = Integer()


class AE_Schema(RadioSchema):
    serial = String()
    extra = String()


class FV_Schema(RadioSchema):
    unit = Integer()
    v1 = String()
    v2 = String()
    v3 = String()
    v4 = String()


# 0,4,0,1,0,4,1,0,10,0,0,0,0,0,0,2,0,0,0,0,2,0,1,0,0,8,0,0,00,02,14,0D,0C,15,0,0,0,0,0,4,1,1
class MU_Schema(RadioSchema):
    beep = RadioBoolean(required=True)
    beep_volume = FormattedInteger(
        validate=validate.Range(min=0, max=7),
        required=True)
    external_speaker_mode = FormattedInteger(
        validate=validate.Range(min=0, max=2), required=True)
    announce = Indexed(ANNOUNCE, fmt='{:02X}', required=True)
    language = Indexed(LANGUAGE, fmt='{:02X}', required=True)
    voice_volume = FormattedInteger(validate=validate.Range(min=0, max=7),
                                    required=True)
    voice_speed = FormattedInteger(validate=validate.Range(min=0, max=4),
                                   required=True)
    playback_repeat = RadioBoolean(required=True)
    playback_repeat_interval = FormattedInteger(
        validate=validate.Range(min=0, max=60), required=True)
    continous_recording = RadioBoolean(required=True)
    vhf_aip = RadioBoolean(required=True)
    uhf_aip = RadioBoolean(required=True)
    s_meter_sql_hang_time = Indexed(SQL_HANG_TIME, fmt='{:02X}', required=True)
    mute_hang_time = Indexed(MUTE_HANG_TIME, fmt='{:02X}', required=True)
    beatshift = RadioBoolean(required=True)
    timeout_timer = FormattedInteger(
        validate=validate.Range(min=0, max=3),
        required=True)
    recall_method = Indexed(RECALL_METHOD, fmt='{:02X}', required=True)
    echolink_speed = Indexed(SPEED, fmt='{:02X}', required=True)
    dtmf_hold = RadioBoolean(required=True)
    dtmf_speed = Indexed(SPEED, fmt='{:02X}', required=True)
    dtmf_pause = Indexed(DTMF_PAUSE, fmt='{:02X}', required=True)
    dtmf_key_lock = RadioBoolean(required=True)
    auto_repeater_offset = RadioBoolean(required=True)
    hold_1750hz = RadioBoolean(required=True)
    unknown = String()
    brightness_level = FormattedInteger(required=True)
    auto_brightness = RadioBoolean(required=True)
    backlight_color = Indexed(BACKLIGHT_COLOR, fmt='{:02X}', required=True)
    pf1_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}', required=True, int_base=16)
    pf2_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}', required=True, int_base=16)
    mic_pf1_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}',
                          required=True, int_base=16)
    mic_pf2_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}',
                          required=True, int_base=16)
    mic_pf3_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}',
                          required=True, int_base=16)
    mic_pf4_key = Indexed(KEY_FUNCTIONS, fmt='{:02X}',
                          required=True, int_base=16)
    mic_key_lock = RadioBoolean(required=True)
    scan_resume = Indexed(SCAN_RESUME, fmt='{:02X}', required=True)
    apo = Indexed(APO, fmt='{:02X}', required=True)
    ext_data_band = Indexed(EXT_DATA_BAND, fmt='{:02X}', required=True)
    ext_data_speed = Indexed(EXT_DATA_SPEED, fmt='{:02X}', required=True)
    sqc_source = Indexed(SQC_SOURCE, fmt='{:02X}', required=True)
    auto_pm_store = RadioBoolean(required=True)
    display_partition_bar = RadioBoolean(required=True)


ME_no_name = ME_Schema(exclude=['name'])

# Dynamically create instances of each schema

_classes = list(locals().values())
_globals = globals()
for cls in _classes:
    name = getattr(cls, '__name__', None)
    if name and name.endswith('_Schema'):
        varname = name[:-7]
        _globals[varname] = cls()
