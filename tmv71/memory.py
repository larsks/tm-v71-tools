# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Memory(KaitaiStruct):

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
        band_430 = 5
        band_1200 = 6

    class Modulation(Enum):
        fm = 0
        am = 1
        nfm = 2
        invalid = 255

    class ChannelBand(Enum):
        vhf = 5
        uhf = 8

    class TxPower(Enum):
        high = 0
        medium = 1
        low = 2

    class Admit(Enum):
        none = 0
        dcs = 1
        ctcss = 2
        tone = 4
        invalid = 7
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass

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


    class ChannelExtendedFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.band = self._io.read_u1()
            self.flags = self._root.ExtendedFlagBits(self._io, self, self._root)


    class ProgramScanMemory(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lower = self._root.CommonVfoFields(self._io, self, self._root)
            self.upper = self._root.CommonVfoFields(self._io, self, self._root)


    class VfoConfig(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = self._root.CommonVfoFields(self._io, self, self._root)


    class ProgramMemory(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

        @property
        def band_mask_b(self):
            if hasattr(self, '_m_band_mask_b'):
                return self._m_band_mask_b if hasattr(self, '_m_band_mask_b') else None

            _pos = self._io.pos()
            self._io.seek(389)
            self._m_band_mask_b = [None] * (5)
            for i in range(5):
                self._m_band_mask_b[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_band_mask_b if hasattr(self, '_m_band_mask_b') else None

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
        def vfo_settings_a(self):
            if hasattr(self, '_m_vfo_settings_a'):
                return self._m_vfo_settings_a if hasattr(self, '_m_vfo_settings_a') else None

            _pos = self._io.pos()
            self._io.seek(64)
            self._m_vfo_settings_a = [None] * (5)
            for i in range(5):
                self._m_vfo_settings_a[i] = self._root.CommonVfoFields(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_vfo_settings_a if hasattr(self, '_m_vfo_settings_a') else None

        @property
        def current_menu_item(self):
            if hasattr(self, '_m_current_menu_item'):
                return self._m_current_menu_item if hasattr(self, '_m_current_menu_item') else None

            _pos = self._io.pos()
            self._io.seek(21)
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
        def band_a_mode(self):
            if hasattr(self, '_m_band_a_mode'):
                return self._m_band_a_mode if hasattr(self, '_m_band_a_mode') else None

            _pos = self._io.pos()
            self._io.seek(1)
            self._m_band_a_mode = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_band_a_mode if hasattr(self, '_m_band_a_mode') else None

        @property
        def vfo_settings_b(self):
            if hasattr(self, '_m_vfo_settings_b'):
                return self._m_vfo_settings_b if hasattr(self, '_m_vfo_settings_b') else None

            _pos = self._io.pos()
            self._io.seek(144)
            self._m_vfo_settings_b = [None] * (5)
            for i in range(5):
                self._m_vfo_settings_b[i] = self._root.CommonVfoFields(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_vfo_settings_b if hasattr(self, '_m_vfo_settings_b') else None

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
        def poweron_message(self):
            if hasattr(self, '_m_poweron_message'):
                return self._m_poweron_message if hasattr(self, '_m_poweron_message') else None

            _pos = self._io.pos()
            self._io.seek(224)
            self._m_poweron_message = (KaitaiStream.bytes_terminate(self._io.read_bytes(12), 255, False)).decode(u"ascii")
            self._io.seek(_pos)
            return self._m_poweron_message if hasattr(self, '_m_poweron_message') else None

        @property
        def band_a_power(self):
            if hasattr(self, '_m_band_a_power'):
                return self._m_band_a_power if hasattr(self, '_m_band_a_power') else None

            _pos = self._io.pos()
            self._io.seek(7)
            self._m_band_a_power = self._root.TxPower(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_band_a_power if hasattr(self, '_m_band_a_power') else None

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
        def band_mask_a(self):
            if hasattr(self, '_m_band_mask_a'):
                return self._m_band_mask_a if hasattr(self, '_m_band_mask_a') else None

            _pos = self._io.pos()
            self._io.seek(384)
            self._m_band_mask_a = [None] * (5)
            for i in range(5):
                self._m_band_mask_a[i] = self._io.read_u1()

            self._io.seek(_pos)
            return self._m_band_mask_a if hasattr(self, '_m_band_mask_a') else None

        @property
        def band_b_freq_band(self):
            if hasattr(self, '_m_band_b_freq_band'):
                return self._m_band_b_freq_band if hasattr(self, '_m_band_b_freq_band') else None

            _pos = self._io.pos()
            self._io.seek(14)
            self._m_band_b_freq_band = self._root.FreqBand(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_band_b_freq_band if hasattr(self, '_m_band_b_freq_band') else None

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
        def band_a_freq_band(self):
            if hasattr(self, '_m_band_a_freq_band'):
                return self._m_band_a_freq_band if hasattr(self, '_m_band_a_freq_band') else None

            _pos = self._io.pos()
            self._io.seek(2)
            self._m_band_a_freq_band = self._root.FreqBand(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_band_a_freq_band if hasattr(self, '_m_band_a_freq_band') else None

        @property
        def band_b_mode(self):
            if hasattr(self, '_m_band_b_mode'):
                return self._m_band_b_mode if hasattr(self, '_m_band_b_mode') else None

            _pos = self._io.pos()
            self._io.seek(13)
            self._m_band_b_mode = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_band_b_mode if hasattr(self, '_m_band_b_mode') else None

        @property
        def s_meter_squelch(self):
            if hasattr(self, '_m_s_meter_squelch'):
                return self._m_s_meter_squelch if hasattr(self, '_m_s_meter_squelch') else None

            _pos = self._io.pos()
            self._io.seek(21)
            self._m_s_meter_squelch = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_s_meter_squelch if hasattr(self, '_m_s_meter_squelch') else None

        @property
        def band_b_power(self):
            if hasattr(self, '_m_band_b_power'):
                return self._m_band_b_power if hasattr(self, '_m_band_b_power') else None

            _pos = self._io.pos()
            self._io.seek(19)
            self._m_band_b_power = self._root.TxPower(self._io.read_u1())
            self._io.seek(_pos)
            return self._m_band_b_power if hasattr(self, '_m_band_b_power') else None


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
        if hasattr(self, '_m_program_memory'):
            return self._m_program_memory if hasattr(self, '_m_program_memory') else None

        _pos = self._io.pos()
        self._io.seek(512)
        self._raw__m_program_memory = [None] * (6)
        self._m_program_memory = [None] * (6)
        for i in range(6):
            self._raw__m_program_memory[i] = self._io.read_bytes(512)
            io = KaitaiStream(BytesIO(self._raw__m_program_memory[i]))
            self._m_program_memory[i] = self._root.ProgramMemory(io, self, self._root)

        self._io.seek(_pos)
        return self._m_program_memory if hasattr(self, '_m_program_memory') else None

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


