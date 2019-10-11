# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Memory(KaitaiStruct):
    """This is a Kaitai Struct[1] definition that parses the memory
    dump from a Kenwood TM-V71A radio. To generate a Python module from
    this description, use the Kaitai Struct Compiler:
    
        ksc --target python --outdir tmv71 memory.ksy
    
    This will generate `memory.py`.
    
    Example usage:
    
        from tmv71.memory import Memory
    
        data = Memory.from_file('my_dump_file.bin')
        for i, channel in enumerate(data.channels()):
          print('channel {} ({}) rx frequency: {}'.format(
                i, channel.name, channel.common.rx_freq))
    
    [1]: http://kaitai.io/
    """

    class DataBand(Enum):
        data_a = 0
        data_b = 1
        data_a_tx_b_rx = 2
        data_a_rx_b_tx = 3

    class ShiftDirection(Enum):
        simplex = 0
        up = 1
        down = 2
        invalid = 3

    class FreqBand(Enum):
        band_118 = 0
        band_144 = 1
        band_220 = 2
        band_300 = 3
        band_430 = 4
        band_1200 = 5

    class Modulation(Enum):
        fm = 0
        am = 1
        nfm = 2
        invalid = 255

    class PortSpeed(Enum):
        b9600 = 0
        b19200 = 1
        b38400 = 2
        b57600 = 3

    class ChannelBand(Enum):
        vhf = 5
        uhf = 8

    class DataSpeed(Enum):
        b1200 = 0
        b9600 = 1

    class TxPower(Enum):
        high = 0
        medium = 1
        low = 2

    class DisplayMode(Enum):
        vfo = 0
        memory = 1

    class Admit(Enum):
        none = 0
        dcs = 1
        ctcss = 2
        tone = 4
        invalid = 7

    class RepeaterIdtx(Enum):
        false = 0
        morse = 1
        voice = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(2)

    class MiscSettings(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

        @property
        def wireless_remote(self):
            if hasattr(self, '_m_wireless_remote'):
                return self._m_wireless_remote if hasattr(self, '_m_wireless_remote') else None

            _pos = self._io.pos()
            self._io.seek(17)
            self._m_wireless_remote = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_wireless_remote if hasattr(self, '_m_wireless_remote') else None

        @property
        def repeater_hold(self):
            if hasattr(self, '_m_repeater_hold'):
                return self._m_repeater_hold if hasattr(self, '_m_repeater_hold') else None

            _pos = self._io.pos()
            self._io.seek(30)
            self._m_repeater_hold = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_repeater_hold if hasattr(self, '_m_repeater_hold') else None

        @property
        def repeater_id(self):
            if hasattr(self, '_m_repeater_id'):
                return self._m_repeater_id if hasattr(self, '_m_repeater_id') else None

            _pos = self._io.pos()
            self._io.seek(368)
            self._m_repeater_id = (KaitaiStream.bytes_terminate(self._io.read_bytes(6), 255, False)).decode(u"ascii")
            self._io.seek(_pos)
            return self._m_repeater_id if hasattr(self, '_m_repeater_id') else None

        @property
        def pc_port_speed(self):
            if hasattr(self, '_m_pc_port_speed'):
                return self._m_pc_port_speed if hasattr(self, '_m_pc_port_speed') else None

            _pos = self._io.pos()
            self._io.seek(33)
            self._m_pc_port_speed = self._root.PortSpeed(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_pc_port_speed if hasattr(self, '_m_pc_port_speed') else None

        @property
        def repeater_idtx(self):
            if hasattr(self, '_m_repeater_idtx'):
                return self._m_repeater_idtx if hasattr(self, '_m_repeater_idtx') else None

            _pos = self._io.pos()
            self._io.seek(31)
            self._m_repeater_idtx = self._root.RepeaterIdtx(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_repeater_idtx if hasattr(self, '_m_repeater_idtx') else None

        @property
        def remote_id(self):
            if hasattr(self, '_m_remote_id'):
                return self._m_remote_id if hasattr(self, '_m_remote_id') else None

            _pos = self._io.pos()
            self._io.seek(18)
            self._m_remote_id = self._io.read_bytes(3)
            self._io.seek(_pos)
            return self._m_remote_id if hasattr(self, '_m_remote_id') else None

        @property
        def current_pm_channel(self):
            if hasattr(self, '_m_current_pm_channel'):
                return self._m_current_pm_channel if hasattr(self, '_m_current_pm_channel') else None

            _pos = self._io.pos()
            self._io.seek(22)
            self._m_current_pm_channel = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_current_pm_channel if hasattr(self, '_m_current_pm_channel') else None

        @property
        def key_lock(self):
            if hasattr(self, '_m_key_lock'):
                return self._m_key_lock if hasattr(self, '_m_key_lock') else None

            _pos = self._io.pos()
            self._io.seek(23)
            self._m_key_lock = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_key_lock if hasattr(self, '_m_key_lock') else None

        @property
        def crossband_repeat(self):
            if hasattr(self, '_m_crossband_repeat'):
                return self._m_crossband_repeat if hasattr(self, '_m_crossband_repeat') else None

            _pos = self._io.pos()
            self._io.seek(16)
            self._m_crossband_repeat = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_crossband_repeat if hasattr(self, '_m_crossband_repeat') else None


    class ExtendedFlagBits(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown = self._io.read_bits_int(7)
            self.lockout = self._io.read_bits_int(1) != 0


    class Channel(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            self.common = self._root.CommonVfoFields(self._io, self, self._root)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name if hasattr(self, '_m_name') else None

            self._m_name = self._root.channel_names[self.number]
            return self._m_name if hasattr(self, '_m_name') else None

        @property
        def extended_flags(self):
            if hasattr(self, '_m_extended_flags'):
                return self._m_extended_flags if hasattr(self, '_m_extended_flags') else None

            self._m_extended_flags = self._root.channel_extended_flags[self.number]
            return self._m_extended_flags if hasattr(self, '_m_extended_flags') else None


    class CommonVfoFields(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rx_freq_raw = self._io.read_u4le()
            self.rx_step_raw = self._io.read_u1()
            self.mod = self._root.Modulation(self._io.read_u1())
            self.flags = self._root.ChannelFlags(self._io, self, self._root)
            self.tone_frequency_raw = self._io.read_u1()
            self.ctcss_frequency_raw = self._io.read_u1()
            self.dcs_code_raw = self._io.read_u1()
            self.tx_offset_raw = self._io.read_u4le()
            self.tx_step_raw = self._io.read_u1()
            self.padding = self._io.read_u1()

        @property
        def ctcss_freq(self):
            if hasattr(self, '_m_ctcss_freq'):
                return self._m_ctcss_freq if hasattr(self, '_m_ctcss_freq') else None

            self._m_ctcss_freq = self._root.tables.tone_frequency[self.ctcss_frequency_raw]
            return self._m_ctcss_freq if hasattr(self, '_m_ctcss_freq') else None

        @property
        def rx_freq(self):
            if hasattr(self, '_m_rx_freq'):
                return self._m_rx_freq if hasattr(self, '_m_rx_freq') else None

            self._m_rx_freq = (self.rx_freq_raw / 1000000.0)
            return self._m_rx_freq if hasattr(self, '_m_rx_freq') else None

        @property
        def dcs_code(self):
            if hasattr(self, '_m_dcs_code'):
                return self._m_dcs_code if hasattr(self, '_m_dcs_code') else None

            self._m_dcs_code = self._root.tables.dcs_code[self.dcs_code_raw]
            return self._m_dcs_code if hasattr(self, '_m_dcs_code') else None

        @property
        def tx_offset(self):
            if hasattr(self, '_m_tx_offset'):
                return self._m_tx_offset if hasattr(self, '_m_tx_offset') else None

            self._m_tx_offset = (self.tx_offset_raw / 1000000.0)
            return self._m_tx_offset if hasattr(self, '_m_tx_offset') else None

        @property
        def rx_step(self):
            if hasattr(self, '_m_rx_step'):
                return self._m_rx_step if hasattr(self, '_m_rx_step') else None

            self._m_rx_step = self._root.tables.step_size[self.rx_step_raw]
            return self._m_rx_step if hasattr(self, '_m_rx_step') else None

        @property
        def deleted(self):
            if hasattr(self, '_m_deleted'):
                return self._m_deleted if hasattr(self, '_m_deleted') else None

            if self.rx_freq_raw == 4294967295:
                self._m_deleted = True

            return self._m_deleted if hasattr(self, '_m_deleted') else None

        @property
        def tone_freq(self):
            if hasattr(self, '_m_tone_freq'):
                return self._m_tone_freq if hasattr(self, '_m_tone_freq') else None

            self._m_tone_freq = self._root.tables.tone_frequency[self.tone_frequency_raw]
            return self._m_tone_freq if hasattr(self, '_m_tone_freq') else None

        @property
        def tx_step(self):
            if hasattr(self, '_m_tx_step'):
                return self._m_tx_step if hasattr(self, '_m_tx_step') else None

            self._m_tx_step = (0 if self.tx_step_raw == 255 else self.tx_step_raw)
            return self._m_tx_step if hasattr(self, '_m_tx_step') else None


    class BandLimit(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lower = self._io.read_u4le()
            self.upper = self._io.read_u4le()


    class ChannelExtendedFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.band = self._io.read_u1()
            self.flags = self._root.ExtendedFlagBits(self._io, self, self._root)


    class Band(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            pass

        @property
        def freq_band_raw(self):
            if hasattr(self, '_m_freq_band_raw'):
                return self._m_freq_band_raw if hasattr(self, '_m_freq_band_raw') else None

            _pos = self._io.pos()
            self._io.seek(2)
            self._m_freq_band_raw = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_freq_band_raw if hasattr(self, '_m_freq_band_raw') else None

        @property
        def freq_band(self):
            """For reasons known only to the designers, the constants that
            indicate frequency band are different on VFO A and VFO B. We
            can adjust the VFO B constants to match by substracing 4
            from the value.
            """
            if hasattr(self, '_m_freq_band'):
                return self._m_freq_band if hasattr(self, '_m_freq_band') else None

            self._m_freq_band = self._root.FreqBand((self.freq_band_raw - (4 * self.number)))
            return self._m_freq_band if hasattr(self, '_m_freq_band') else None

        @property
        def display_mode(self):
            if hasattr(self, '_m_display_mode'):
                return self._m_display_mode if hasattr(self, '_m_display_mode') else None

            _pos = self._io.pos()
            self._io.seek(1)
            self._m_display_mode = self._root.DisplayMode(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_display_mode if hasattr(self, '_m_display_mode') else None

        @property
        def tx_power(self):
            if hasattr(self, '_m_tx_power'):
                return self._m_tx_power if hasattr(self, '_m_tx_power') else None

            _pos = self._io.pos()
            self._io.seek(7)
            self._m_tx_power = self._root.TxPower(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_tx_power if hasattr(self, '_m_tx_power') else None

        @property
        def s_meter_squelch(self):
            if hasattr(self, '_m_s_meter_squelch'):
                return self._m_s_meter_squelch if hasattr(self, '_m_s_meter_squelch') else None

            _pos = self._io.pos()
            self._io.seek(9)
            self._m_s_meter_squelch = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_s_meter_squelch if hasattr(self, '_m_s_meter_squelch') else None


    class ProgramScanMemory(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lower = self._root.CommonVfoFields(self._io, self, self._root)
            self.upper = self._root.CommonVfoFields(self._io, self, self._root)


    class BandMaskList(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            self.mask = [None] * (self.number)
            for i in range(self.number):
                self.mask[i] = self._io.read_u1()



    class VfoConfig(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = self._root.CommonVfoFields(self._io, self, self._root)


    class VfoSettingsList(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            self.list = [None] * (self.number)
            for i in range(self.number):
                self.list[i] = self._root.CommonVfoFields(self._io, self, self._root)



    class ProgramMemory(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            pass

        @property
        def band_limits(self):
            if hasattr(self, '_m_band_limits'):
                return self._m_band_limits if hasattr(self, '_m_band_limits') else None

            _pos = self._io.pos()
            self._io.seek(256)
            self._m_band_limits = [None] * (2)
            for i in range(2):
                self._m_band_limits[i] = self._root.BandLimitList(5, self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_band_limits if hasattr(self, '_m_band_limits') else None

        @property
        def beep(self):
            if hasattr(self, '_m_beep'):
                return self._m_beep if hasattr(self, '_m_beep') else None

            _pos = self._io.pos()
            self._io.seek(336)
            self._m_beep = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_beep if hasattr(self, '_m_beep') else None

        @property
        def data_speed(self):
            if hasattr(self, '_m_data_speed'):
                return self._m_data_speed if hasattr(self, '_m_data_speed') else None

            _pos = self._io.pos()
            self._io.seek(374)
            self._m_data_speed = self._root.DataSpeed(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_data_speed if hasattr(self, '_m_data_speed') else None

        @property
        def current_menu_item(self):
            if hasattr(self, '_m_current_menu_item'):
                return self._m_current_menu_item if hasattr(self, '_m_current_menu_item') else None

            _pos = self._io.pos()
            self._io.seek(46)
            self._m_current_menu_item = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_current_menu_item if hasattr(self, '_m_current_menu_item') else None

        @property
        def beep_volume(self):
            if hasattr(self, '_m_beep_volume'):
                return self._m_beep_volume if hasattr(self, '_m_beep_volume') else None

            _pos = self._io.pos()
            self._io.seek(337)
            self._m_beep_volume = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_beep_volume if hasattr(self, '_m_beep_volume') else None

        @property
        def ptt_band(self):
            if hasattr(self, '_m_ptt_band'):
                return self._m_ptt_band if hasattr(self, '_m_ptt_band') else None

            _pos = self._io.pos()
            self._io.seek(50)
            self._m_ptt_band = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_ptt_band if hasattr(self, '_m_ptt_band') else None

        @property
        def vfo_settings(self):
            if hasattr(self, '_m_vfo_settings'):
                return self._m_vfo_settings if hasattr(self, '_m_vfo_settings') else None

            _pos = self._io.pos()
            self._io.seek(64)
            self._m_vfo_settings = [None] * (2)
            for i in range(2):
                self._m_vfo_settings[i] = self._root.VfoSettingsList(5, self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_vfo_settings if hasattr(self, '_m_vfo_settings') else None

        @property
        def group_link(self):
            if hasattr(self, '_m_group_link'):
                return self._m_group_link if hasattr(self, '_m_group_link') else None

            _pos = self._io.pos()
            self._io.seek(240)
            self._m_group_link = (KaitaiStream.bytes_terminate(self._io.read_bytes(10), 255, False)).decode(u"ascii")
            self._io.seek(_pos)
            return self._m_group_link if hasattr(self, '_m_group_link') else None

        @property
        def ctrl_band(self):
            if hasattr(self, '_m_ctrl_band'):
                return self._m_ctrl_band if hasattr(self, '_m_ctrl_band') else None

            _pos = self._io.pos()
            self._io.seek(51)
            self._m_ctrl_band = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_ctrl_band if hasattr(self, '_m_ctrl_band') else None

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name if hasattr(self, '_m_name') else None

            if self.number > 0:
                self._m_name = self._root.program_memory_names[(self.number - 1)]

            return self._m_name if hasattr(self, '_m_name') else None

        @property
        def band_masks(self):
            if hasattr(self, '_m_band_masks'):
                return self._m_band_masks if hasattr(self, '_m_band_masks') else None

            _pos = self._io.pos()
            self._io.seek(384)
            self._m_band_masks = [None] * (2)
            for i in range(2):
                self._m_band_masks[i] = self._root.BandMaskList(5, self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_band_masks if hasattr(self, '_m_band_masks') else None

        @property
        def bands(self):
            if hasattr(self, '_m_bands'):
                return self._m_bands if hasattr(self, '_m_bands') else None

            self._raw__m_bands = [None] * (2)
            self._m_bands = [None] * (2)
            for i in range(2):
                self._raw__m_bands[i] = self._io.read_bytes(12)
                io = KaitaiStream(BytesIO(self._raw__m_bands[i]))
                self._m_bands[i] = self._root.Band(i, io, self, self._root)

            return self._m_bands if hasattr(self, '_m_bands') else None

        @property
        def power_on_message(self):
            if hasattr(self, '_m_power_on_message'):
                return self._m_power_on_message if hasattr(self, '_m_power_on_message') else None

            _pos = self._io.pos()
            self._io.seek(224)
            self._m_power_on_message = (KaitaiStream.bytes_terminate(self._io.read_bytes(12), 0, False)).decode(u"ascii")
            self._io.seek(_pos)
            return self._m_power_on_message if hasattr(self, '_m_power_on_message') else None

        @property
        def data_band(self):
            if hasattr(self, '_m_data_band'):
                return self._m_data_band if hasattr(self, '_m_data_band') else None

            _pos = self._io.pos()
            self._io.seek(373)
            self._m_data_band = self._root.DataBand(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_data_band if hasattr(self, '_m_data_band') else None


    class ChannelFlags(KaitaiStruct):
        """These flags are included in byte 6 of the channel entry.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown = self._io.read_bits_int(1) != 0
            self.admit = self._root.Admit(self._io.read_bits_int(3))
            self.reverse = self._io.read_bits_int(1) != 0
            self.split = self._io.read_bits_int(1) != 0
            self.shift = self._root.ShiftDirection(self._io.read_bits_int(2))


    class Tables(KaitaiStruct):
        """This is a value-only collection of tables used to map
        numeric constants in the channel data into actual values.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

        @property
        def step_size(self):
            if hasattr(self, '_m_step_size'):
                return self._m_step_size if hasattr(self, '_m_step_size') else None

            self._m_step_size = [5, 6.25, 28.33, 10, 12.5, 15, 20, 25, 30, 50, 100]
            return self._m_step_size if hasattr(self, '_m_step_size') else None

        @property
        def tone_frequency(self):
            if hasattr(self, '_m_tone_frequency'):
                return self._m_tone_frequency if hasattr(self, '_m_tone_frequency') else None

            self._m_tone_frequency = [67, 69.3, 71.9, 74.4, 77, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8, 97.4, 100, 103.5, 107.2, 110.9, 114.8, 118.8, 123, 127.3, 131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2, 192.8, 203.5, 240.7, 210.7, 218.1, 225.7, 229.1, 233.6, 241.8, 250.3, 254.1]
            return self._m_tone_frequency if hasattr(self, '_m_tone_frequency') else None

        @property
        def dcs_code(self):
            if hasattr(self, '_m_dcs_code'):
                return self._m_dcs_code if hasattr(self, '_m_dcs_code') else None

            self._m_dcs_code = [23, 25, 26, 31, 32, 36, 43, 47, 51, 53, 54, 65, 71, 72, 73, 74, 114, 115, 116, 122, 125, 131, 132, 134, 143, 145, 152, 155, 156, 162, 165, 172, 174, 205, 212, 223, 225, 226, 243, 244, 245, 246, 251, 252, 255, 261, 263, 265, 266, 271, 274, 306, 311, 315, 325, 331, 332, 343, 346, 351, 356, 364, 365, 371, 411, 412, 413, 423, 431, 432, 445, 446, 452, 454, 455, 462, 464, 465, 466, 503, 506, 516, 523, 565, 532, 546, 565, 606, 612, 624, 627, 631, 632, 654, 662, 664, 703, 712, 723, 731, 732, 734, 743, 754]
            return self._m_dcs_code if hasattr(self, '_m_dcs_code') else None


    class BandLimitList(KaitaiStruct):
        def __init__(self, number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.number = number
            self._read()

        def _read(self):
            self.list = [None] * (self.number)
            for i in range(self.number):
                self.list[i] = self._root.BandLimit(self._io, self, self._root)



    @property
    def channels(self):
        if hasattr(self, '_m_channels'):
            return self._m_channels if hasattr(self, '_m_channels') else None

        _pos = self._io.pos()
        self._io.seek(5888)
        self._m_channels = [None] * (1000)
        for i in range(1000):
            self._m_channels[i] = self._root.Channel(i, self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_channels if hasattr(self, '_m_channels') else None

    @property
    def program_memory(self):
        """The radio has 6 programmable memory regions. One is used when no
        PM channel is selected, and then there are 5 numbered PM channels.
        The PM channels store a variety of radio configuration settings so
        that you can quickly switch between them.
        """
        if hasattr(self, '_m_program_memory'):
            return self._m_program_memory if hasattr(self, '_m_program_memory') else None

        _pos = self._io.pos()
        self._io.seek(512)
        self._raw__m_program_memory = [None] * (6)
        self._m_program_memory = [None] * (6)
        for i in range(6):
            self._raw__m_program_memory[i] = self._io.read_bytes(512)
            io = KaitaiStream(BytesIO(self._raw__m_program_memory[i]))
            self._m_program_memory[i] = self._root.ProgramMemory(i, io, self, self._root)

        self._io.seek(_pos)
        return self._m_program_memory if hasattr(self, '_m_program_memory') else None

    @property
    def misc_settings(self):
        if hasattr(self, '_m_misc_settings'):
            return self._m_misc_settings if hasattr(self, '_m_misc_settings') else None

        _pos = self._io.pos()
        self._io.seek(0)
        self._raw__m_misc_settings = self._io.read_bytes(512)
        io = KaitaiStream(BytesIO(self._raw__m_misc_settings))
        self._m_misc_settings = self._root.MiscSettings(io, self, self._root)
        self._io.seek(_pos)
        return self._m_misc_settings if hasattr(self, '_m_misc_settings') else None

    @property
    def echolink_names(self):
        if hasattr(self, '_m_echolink_names'):
            return self._m_echolink_names if hasattr(self, '_m_echolink_names') else None

        _pos = self._io.pos()
        self._io.seek(288)
        self._m_echolink_names = [None] * (10)
        for i in range(10):
            self._m_echolink_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_echolink_names if hasattr(self, '_m_echolink_names') else None

    @property
    def program_scan_memory(self):
        if hasattr(self, '_m_program_scan_memory'):
            return self._m_program_scan_memory if hasattr(self, '_m_program_scan_memory') else None

        _pos = self._io.pos()
        self._io.seek(21888)
        self._m_program_scan_memory = [None] * (10)
        for i in range(10):
            self._m_program_scan_memory[i] = self._root.ProgramScanMemory(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_program_scan_memory if hasattr(self, '_m_program_scan_memory') else None

    @property
    def group_names(self):
        if hasattr(self, '_m_group_names'):
            return self._m_group_names if hasattr(self, '_m_group_names') else None

        _pos = self._io.pos()
        self._io.seek(32000)
        self._m_group_names = [None] * (8)
        for i in range(8):
            self._m_group_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_group_names if hasattr(self, '_m_group_names') else None

    @property
    def wx_channel_names(self):
        if hasattr(self, '_m_wx_channel_names'):
            return self._m_wx_channel_names if hasattr(self, '_m_wx_channel_names') else None

        _pos = self._io.pos()
        self._io.seek(30688)
        self._m_wx_channel_names = [None] * (10)
        for i in range(10):
            self._m_wx_channel_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_wx_channel_names if hasattr(self, '_m_wx_channel_names') else None

    @property
    def dtmf_codes(self):
        if hasattr(self, '_m_dtmf_codes'):
            return self._m_dtmf_codes if hasattr(self, '_m_dtmf_codes') else None

        _pos = self._io.pos()
        self._io.seek(48)
        self._m_dtmf_codes = [None] * (10)
        for i in range(10):
            self._m_dtmf_codes[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_dtmf_codes if hasattr(self, '_m_dtmf_codes') else None

    @property
    def program_memory_names(self):
        if hasattr(self, '_m_program_memory_names'):
            return self._m_program_memory_names if hasattr(self, '_m_program_memory_names') else None

        _pos = self._io.pos()
        self._io.seek(32160)
        self._m_program_memory_names = [None] * (5)
        for i in range(5):
            self._m_program_memory_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_program_memory_names if hasattr(self, '_m_program_memory_names') else None

    @property
    def dtmf_names(self):
        if hasattr(self, '_m_dtmf_names'):
            return self._m_dtmf_names if hasattr(self, '_m_dtmf_names') else None

        _pos = self._io.pos()
        self._io.seek(208)
        self._m_dtmf_names = [None] * (10)
        for i in range(10):
            self._m_dtmf_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_dtmf_names if hasattr(self, '_m_dtmf_names') else None

    @property
    def channel_extended_flags(self):
        """The TM-V71A appears to maintain some extended channel flags. At
        the moment I have only identify the `lockout` flag, used to
        skip a channel during scans.
        """
        if hasattr(self, '_m_channel_extended_flags'):
            return self._m_channel_extended_flags if hasattr(self, '_m_channel_extended_flags') else None

        _pos = self._io.pos()
        self._io.seek(3584)
        self._m_channel_extended_flags = [None] * (1000)
        for i in range(1000):
            self._m_channel_extended_flags[i] = self._root.ChannelExtendedFlags(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_channel_extended_flags if hasattr(self, '_m_channel_extended_flags') else None

    @property
    def channel_names(self):
        if hasattr(self, '_m_channel_names'):
            return self._m_channel_names if hasattr(self, '_m_channel_names') else None

        _pos = self._io.pos()
        self._io.seek(22528)
        self._m_channel_names = [None] * (1000)
        for i in range(1000):
            self._m_channel_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_channel_names if hasattr(self, '_m_channel_names') else None

    @property
    def tables(self):
        """A list of lookup tables used to convert numeric constants stored
        in radio memory to their corresponding values.
        """
        if hasattr(self, '_m_tables'):
            return self._m_tables if hasattr(self, '_m_tables') else None

        self._m_tables = self._root.Tables(self._io, self, self._root)
        return self._m_tables if hasattr(self, '_m_tables') else None

    @property
    def echolink_codes(self):
        if hasattr(self, '_m_echolink_codes'):
            return self._m_echolink_codes if hasattr(self, '_m_echolink_codes') else None

        _pos = self._io.pos()
        self._io.seek(400)
        self._m_echolink_codes = [None] * (10)
        for i in range(10):
            self._m_echolink_codes[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 255, False)).decode(u"ascii")

        self._io.seek(_pos)
        return self._m_echolink_codes if hasattr(self, '_m_echolink_codes') else None


