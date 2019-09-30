import enum
import hexdump
import logging
import serial

from tmv71 import schema

LOG = logging.getLogger(__name__)


class BAND_MODE(enum.IntEnum):
    VFO = 0
    MEM = 1
    CALL = 2
    WX = 3


class TX_POWER(enum.IntEnum):
    LOW = 2
    MED = 1
    HIGH = 0


class CommunicationError(Exception):
    def __init__(self, msg=None):
        super().__init__(msg or self.__doc__)


class UnknownDeviceError(CommunicationError):
    '''Unknown device'''


class UnknownCommandError(CommunicationError):
    '''The radio did not recognize the given command'''


class InvalidCommandError(CommunicationError):
    '''The radio was unable to execute the given command'''


class UnexpectedResponseError(CommunicationError):
    '''The radio returned an unexpected response'''


class ReadTimeoutError(CommunicationError):
    '''A read operation timed out'''


class TMV71:
    def __init__(self, dev, speed=9600, debug=False):
        self.dev = dev
        self.speed = speed
        self.debug = debug
        self.init_serial()

    def init_serial(self):
        LOG.info('opening %s at %d bps', self.dev, self.speed)
        self._port = serial.Serial(self.dev,
                                   baudrate=self.speed,
                                   rtscts=True,
                                   dsrdtr=True,
                                   timeout=1)

    def write_bytes(self, data):
        if self.debug:
            print('write:')
            print('\n'.join(hexdump.dumpgen(data)))
        self._port.write(data)

    def read_bytes(self, n):
        data = self._port.read(n)
        if not data:
            raise ReadTimeoutError()

        if self.debug:
            print('read:')
            print('\n'.join(hexdump.dumpgen(data)))
        return data

    def read_line(self):
        data = self._port.read_until(b'\r')
        if not data:
            raise ReadTimeoutError()

        if self.debug:
            print('read:')
            print('\n'.join(hexdump.dumpgen(data)))
        return data[:-1]

    def send_command_raw(self, command, *args):
        self.write_bytes(command)
        if (args):
            args_encoded = b' ' + b','.join(args)
            self.write_bytes(args_encoded)
        self.write_bytes(b'\r')
        return self.read_line()

    def send_command(self, *command):
        LOG.debug('sending command: %s', command)

        command_encoded = [str(arg).encode('ascii')
                           for arg in command]
        res = self.send_command_raw(*command_encoded).decode('ascii')

        if res == '?':
            raise UnknownCommandError(command[0])
        elif res == 'N':
            raise InvalidCommandError(command[0])
        elif not res.startswith(command[0]):
            raise UnexpectedResponseError(command[0])

        return res[3:].split(',')

    # ----------------------------------------------------------------------

    def clear(self):
        self.write_bytes(b'\r')

        while True:
            try:
                self.read_bytes(1024)
            except ReadTimeoutError:
                break

        self.write_bytes(b'\r')
        res = self.read_line()
        if res != b'?':
            raise UnexpectedResponseError()

    def check_id(self, expected='TM-V71'):
        res = self.radio_id()
        LOG.debug('verify device id: wanted %s, got %s', expected, res[0])
        if res[0] != expected:
            raise UnknownDeviceError(res[0])

        return res

    def radio_id(self):
        return self.send_command('ID')

    def radio_type(self):
        return schema.TY.from_tuple(self.send_command('TY'))

    def radio_firmware(self):
        return self.send_command('FV', 0)

    def lock(self):
        return self.send_command('LK', 1)

    def unlock(self):
        return self.send_command('LK', 0)

    def get_poweron_message(self):
        return self.send_command('MS')

    def set_poweron_message(self, msg):
        return self.send_command('MS', msg)

    def get_dual_band_mode(self):
        return self.send_command('DL')

    def set_dual_band_mode(self):
        return self.send_command('DL', 0)

    def set_single_band_mode(self):
        return self.send_command('DL', 1)

    def get_channel(self, band):
        return self.send_command('MR', band)

    def set_channel(self, band, channel):
        channel = '{:03d}'.format(channel)
        return self.send_command('MR', band, channel)

    def get_ptt_ctrl_band(self):
        return self.send_command('BC')

    def set_ptt_ctrl_band(self, ctrl_band, ptt_band):
        return self.send_command('BC', ctrl_band, ptt_band)

    def set_ptt(self, ptt_state):
        if ptt_state:
            return self.send_command('TX')
        else:
            return self.send_command('RX')

    def get_band_mode(self, band):
        return self.send_command('VM', band)

    def set_band_mode(self, band, mode):
        return self.send_command('VM', band, mode)

    def get_tx_power(self, band):
        return self.send_command('PC', band)

    def set_tx_power(self, band, power):
        return self.send_command('PC', band, power)

    def get_band_vfo(self, band):
        return schema.FO.from_tuple(
            self.send_command('FO', band))

    def set_band_vfo(self, band, settings):
        settings['band'] = band
        return schema.FO.from_tuple(
            self.send_command('FO', schema.FO.to_csv(settings)))

    def get_channel_entry(self, channel):
        channel = '{:03d}'.format(channel)
        return schema.ME.from_tuple(self.send_command('ME', channel))

    def set_channel_entry(self, channel, settings):
        settings[channel] = channel
        return self.send_command('ME', schema.ME.to_csv(settings))

    def delete_channel_entry(self, channel):
        channel = '{:03d}'.format(channel)
        return self.send_command('ME', '')

    def get_channel_name(self, channel):
        channel = '{:03d}'.format(int(channel))
        res = self.send_command('MN', channel)
        return res[1]

    def set_channel_name(self, channel, name):
        channel = '{:03d}'.format(int(channel))
        res = self.send_command('MN', channel, name)
        return res[1]

    # ----------------------------------------------------------------------

    def enter_programming_mode(self):
        self.write_bytes(b'0M PROGRAM\r')
        res = self.read_line()
        if res != b'0M':
            raise UnexpectedResponseError()

    def read_block(self, block, offset, length):
        self.write_bytes(bytes([ord('R'), block, offset, length]))
        self.read_bytes(4)
        data = self.read_bytes(length if length else 256)
        self.write_bytes(bytes([6]))
        self.check_ack()
        return data

    def write_block(self, block, offset, data):
        dlen = len(data)
        if dlen == 256:
            dlen = 0

        self.write_bytes(bytes([ord('W'), block, offset, dlen]))
        self.write_bytes(bytes(data))
        self.check_ack()

    def check_ack(self):
        res = self.read_bytes(1)
        if res == b'\x15':
            LOG.warning('radio is in error state (continuing)')
        elif res != b'\x06':
            raise UnexpectedResponseError()

    def read_memory(self, fd):
        try:
            self.enter_programming_mode()

            for block in range(0x7F):
                LOG.debug('reading block %d', block)
                data = self.read_block(block, 0, 0)
                fd.write(data)
        finally:
            self.exit_programming_mode()

    def write_memory(self, fd):
        try:
            self.enter_programming_mode()
            data = self.read_block(0, 0, 4)
            if data != b'\x00\x4b\x01\xff':
                LOG.warning('unexpected response from radio (continue)')

            self.write_block(0, 0, b'\xff')

            fd.seek(4)
            self.write_block(0, 4, fd.read(0xfc))

            for block in range(1, 0x7F):
                LOG.debug('writing block %d', block)
                data = fd.read(256)
                self.write_block(block, 0, data)

            self.write_block(0, 0, b'\x00\x4b\x01\xff')
        finally:
            self.exit_programming_mode()

    def exit_programming_mode(self):
        self.write_bytes(b'E')
        for expected in [b'\x06', b'\r', b'\x00']:
            res = self.read_bytes(1)
            if res != expected:
                raise UnexpectedResponseError()

    # ----------------------------------------------------------------------
