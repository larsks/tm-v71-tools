from contextlib import contextmanager
from functools import wraps
import hexdump
import logging
import serial
import sys

from tmv71 import schema

LOG = logging.getLogger(__name__)
PORT_SPEED = ['9600', '19200', '38400', '57600']

M_OFFSET_PORT_SPEED = 0x21


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


class WrongModeError(CommunicationError):
    '''Radio is not in programming mode'''


def pm(f):
    '''Decorator to ensure that radio is in programming mode'''

    @wraps(f)
    def _(self, *args, **kwargs):
        if not self._programming_mode:
            raise WrongModeError()

        return f(self, *args, **kwargs)

    return _


class TMV71:
    def __init__(self, dev, speed=9600, debug=False, timeout=0.5):
        self.dev = dev
        self.speed = speed
        self.debug = debug
        self.timeout = timeout
        self._programming_mode = False
        self.init_serial()

    def __repr__(self):
        return '<TMV71 on {0.dev} @ {0.speed}>'.format(self)

    def init_serial(self):
        LOG.info('opening %s at %d bps', self.dev, self.speed)
        self._port = serial.Serial(self.dev,
                                   baudrate=self.speed,
                                   rtscts=True,
                                   dsrdtr=True,
                                   timeout=self.timeout)

    def write_bytes(self, data):
        '''Write the given data to the radio.'''

        if self.debug:
            print('write:', file=sys.stderr)
            print('\n'.join(hexdump.dumpgen(data)), file=sys.stderr)
        self._port.write(data)

    def read_bytes(self, n=0, until=None):
        '''Read n bytes of data from the radio.'''

        if until is None:
            data = self._port.read(n)
        else:
            data = self._port.read_until(until)

        if not data:
            raise ReadTimeoutError()

        if self.debug:
            print('read:', file=sys.stderr)
            print('\n'.join(hexdump.dumpgen(data)), file=sys.stderr)
        return data

    def read_line(self):
        '''Read a carriage-return terminated line from the radio.'''

        return self.read_bytes(until=b'\r')[:-1]

    def send_command_raw(self, command, *args):
        self.write_bytes(command)
        if (args):
            args_encoded = b' ' + b','.join(args)
            self.write_bytes(args_encoded)
        self.write_bytes(b'\r')
        return self.read_line()

    def send_command(self, *command):
        '''Send a command to the radio.

        Convert the given command and arguments to bytes and send them to the
        radio.  Read a response, convert it into a string, and split it on
        commas.

            >>> radio.send_command('FV', 0)
            ['0', '1.00', '2.10', 'A', '1']

        All arguments are first converted to strings, so
        send_command('FV', 0) and send_command('FV', '0') are
        equivalent.'''

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
        '''Clear the communication channel.

        Ensure the radio is in a known state by attempting to exit
        programming mode, complete any partially entered command, and
        read any remaining output.'''

        self.write_bytes(b'E\r')

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
        '''Return the radio ID'''
        return self.send_command('ID')

    def radio_type(self):
        '''Return the radio type (K for the US, M for Europe)'''

        return schema.TY.from_tuple(self.send_command('TY'))

    def radio_firmware(self):
        return self.send_command('FV', 0)

    def lock(self):
        '''Enable the radio key lock'''
        return self.send_command('LK', 1)

    def unlock(self):
        '''Disable the radio key lock'''
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
        try:
            return self.send_command('ME', channel, '')
        except InvalidCommandError:
            return ['']

    def get_channel_name(self, channel):
        channel = '{:03d}'.format(int(channel))
        res = self.send_command('MN', channel)
        return res[1]

    def set_channel_name(self, channel, name):
        channel = '{:03d}'.format(int(channel))
        res = self.send_command('MN', channel, name)
        return res[1]

    # ----------------------------------------------------------------------

    @pm
    def get_port_speed(self):
        speed = self.read_block(0, M_OFFSET_PORT_SPEED, 1)
        return PORT_SPEED[int.from_bytes(speed, byteorder='big')]

    @pm
    def set_port_speed(self, speed):
        speed = PORT_SPEED.index(speed)
        self.write_block(0, M_OFFSET_PORT_SPEED, bytes([speed]))

    @pm
    def reset(self):
        '''Reset to default configuration'''
        self.write_block(0, 0, b'\xff')

    # ----------------------------------------------------------------------

    @contextmanager
    def programming_mode(self):
        '''Wrap code that interacts with the radio in programming mode.

        You must enclose calls that require programming mode with this
        context manager.  For example:

            with radio.programming_mode():
                radio.read_block(0, 0, 0)

        Failure to use the context manager will result in
        WrongModeError exception.'''

        self.enter_programming_mode()
        yield
        self.exit_programming_mode()

    def enter_programming_mode(self):
        LOG.debug('entering programming mode')
        self.write_bytes(b'0M PROGRAM\r')
        res = self.read_line()
        if res != b'0M':
            raise UnexpectedResponseError()
        self._programming_mode = True

    def exit_programming_mode(self):
        LOG.debug('exiting programming mode')
        self.write_bytes(b'E')
        self._programming_mode = False
        for expected in [b'\x06', b'\r', b'\x00']:
            res = self.read_bytes(1)
            if res != expected:
                raise UnexpectedResponseError()

    @pm
    def read_block(self, block, offset, length):
        '''Read data from the radio'''

        LOG.debug('read block %d, offset %d, length %d', block, offset, length)
        self.write_bytes(bytes([ord('R'), block, offset, length]))
        self.read_bytes(4)
        data = self.read_bytes(length if length else 256)
        self.write_bytes(bytes([6]))
        self.check_ack()
        return data

    @pm
    def write_block(self, block, offset, data):
        '''Write data to the radio'''

        length = len(data)
        LOG.debug('write block %d, offset %d, length %d',
                  block, offset, length)
        if length == 256:
            length = 0

        self.write_bytes(bytes([ord('W'), block, offset, length]))
        self.write_bytes(bytes(data))
        self.check_ack()

    def check_ack(self):
        '''Validate the response to programming mode commands.'''

        res = self.read_bytes(1)
        if res == b'\x15':
            LOG.warning('radio is in error state (continuing)')
        elif res != b'\x06':
            raise UnexpectedResponseError()

    @pm
    def read_memory(self, fd):
        '''Read data from the radio and write it to a file-like object.'''

        for block in range(0x7F):
            LOG.debug('reading block %d', block)
            data = self.read_block(block, 0, 0)
            fd.write(data)

    @pm
    def write_memory(self, fd):
        '''Read data from a file-like object and write it to the radio.'''

        data = self.read_block(0, 0, 4)
        if data != b'\x00\x4b\x01\xff':
            LOG.warning('unexpected content in block 0 (continuing)')

        self.write_block(0, 0, b'\xff')

        fd.seek(4)
        self.write_block(0, 4, fd.read(0xfc))

        for block in range(1, 0x7F):
            LOG.debug('writing block %d', block)
            data = fd.read(256)
            self.write_block(block, 0, data)

        self.write_block(0, 0, b'\x00\x4b\x01\xff')

    # ----------------------------------------------------------------------
