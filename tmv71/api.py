from contextlib import contextmanager
from functools import wraps
import hexdump
import logging
import serial
import struct
import sys
import time

from tmv71 import schema

LOG = logging.getLogger(__name__)
PORT_SPEED = ['9600', '19200', '38400', '57600']
FREQUENCY_BAND = ['118', '144', '220', '300', '430', '1200']
DTMF_TONES = '0123456789ABCD*#'

M_OFFSET_PORT_SPEED = 0x21
M_OFFSET_BANDA_BAND = 0x202
M_OFFSET_BANDB_BAND = 0x20E
M_OFFSET_OPERATING_MODE = 0x10
M_OFFSET_REMOTE_ID = 0x12


class CommunicationError(Exception):
    def __init__(self, msg=None):
        super().__init__(msg or self.__doc__)

    def __str__(self):
        return self.__doc__.format(*self.args)


class UnknownDeviceError(CommunicationError):
    '''Unknown device: {}'''


class UnknownCommandError(CommunicationError):
    '''The radio did not recognize the "{}" command'''


class InvalidCommandError(CommunicationError):
    '''The radio was unable to execute the "{}" command'''


class UnexpectedResponseError(CommunicationError):
    '''The radio returned an unexpected response'''


class ReadTimeoutError(CommunicationError):
    '''A read operation timed out'''


class WrongModeError(CommunicationError):
    '''Radio is not in programming mode'''


def schemacommand(schema):

    def decorator(f):

        @wraps(f)
        def inner(*args, **kwargs):
            return schema.from_tuple(f(*args, **kwargs))

        return inner

    return decorator


def bandcommand(f):
    '''A decorator for commands that have (band, value) results'''

    @wraps(f)
    def _(*args, **kwargs):
        res = f(*args, **kwargs)
        return int(res[1])

    return _


def pm(f):
    '''Decorator to ensure that radio is in programming mode'''

    @wraps(f)
    def _(self, *args, **kwargs):
        if not self._programming_mode:
            raise WrongModeError()

        return f(self, *args, **kwargs)

    if _.__doc__ is None:
        _.__doc__ = ''

    _.__doc__ += '\n\n[REQUIRES PROGRAMMING MODE]'

    return _


class TMV71:
    expected_id = 'TM-V71'
    memory_max = 0x7f
    memory_magic = struct.pack('BB', 0x0, 0x4b)

    def __init__(self, port, speed=9600, debug=False, timeout=0.5):
        self.port = port
        self.speed = speed
        self.debug = debug
        self.timeout = timeout
        self._programming_mode = False
        self._ptt = False
        self.init_serial()

    def __repr__(self):
        return '<TMV71 on {0.port} @ {0.speed}>'.format(self)

    def init_serial(self):
        LOG.info('opening %s at %d bps', self.port, self.speed)
        self._port = serial.Serial(self.port,
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

    def reopen(self):
        '''Close and re-open the serial port'''
        self._port.close()
        self._port.open()

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

    def check_id(self):
        res = self.radio_id()
        LOG.debug('check_id: wanted %s, got %s',
                  self.expected_id, res)
        if res != self.expected_id:
            raise UnknownDeviceError(res)

    def radio_id(self):
        '''Return the radio ID'''
        return self.send_command('ID')[0]

    @schemacommand(schema.TY)
    def radio_type(self):
        '''Return the radio type (K for the US, M for Europe)'''

        return self.send_command('TY')

    @schemacommand(schema.AE)
    def radio_serial(self):
        '''Return the radio serial number'''

        return self.send_command('AE')

    @schemacommand(schema.FV)
    def radio_firmware(self):
        return self.send_command('FV', 0)

    def get_band_squelch(self, band):
        '''Return the squelch setting for the given band'''

        return int(self.send_command('SQ', band)[0], 16)

    @bandcommand
    def get_band_squelch_state(self, band):
        '''Return the squelch setting for the given band'''

        return self.send_command('BY', band)

    @bandcommand
    def get_band_reverse(self, band):
        '''Return the state of reverse mode for the given band'''

        return self.send_command('AS', band)

    @bandcommand
    def set_band_reverse(self, band, reverse_state):
        '''Return the state of reverse mode for the given band'''

        return self.send_command('AS', band, reverse_state)

    def get_lock_state(self):
        '''Get the current state of the key lock'''
        return bool(self.send_command('LK')[0])

    def set_lock_state(self, lock_state):
        '''Set the current state of the key lock'''
        return bool(self.send_command('LK', 1 if lock_state else 0)[0])

    def get_poweron_message(self):
        return self.send_command('MS')[0]

    def set_poweron_message(self, msg):
        return self.send_command('MS', msg)[0]

    def get_dual_band_mode(self):
        return int(self.send_command('DL')[0])

    def set_dual_band_mode(self):
        return int(self.send_command('DL', 0)[0])

    def set_single_band_mode(self):
        return int(self.send_command('DL', 1)[0])

    @bandcommand
    def get_channel(self, band):
        return self.send_command('MR', band)

    @bandcommand
    def set_channel(self, band, channel):
        channel = '{:03d}'.format(channel)
        return self.send_command('MR', band, channel)

    @schemacommand(schema.BC)
    def get_ptt_ctrl(self):
        return self.send_command('BC')

    @schemacommand(schema.BC)
    def set_ptt_ctrl(self, ctrl_band, ptt_band):
        return self.send_command('BC', ctrl_band, ptt_band)

    def set_ptt(self, ptt_state):
        if ptt_state:
            self._ptt = True
            return self.send_command('TX')
        else:
            self._ptt = False
            return self.send_command('RX')

    @contextmanager
    def ptt(self):
        '''A context manager that ensures ptt is released'''

        try:
            self.set_ptt(True)
            yield
        finally:
            self.set_ptt(False)

    dtmf_tone_slow = 0.250
    dtmf_tone_fast = 0.040

    def send_dtmf(self, tones, fast=False):
        '''Send a series of DTMF tones.

        This will send each tone for <delay> seconds (default 0.250).
        When sending tones there are no "spaces" between tones. This
        appears to be a limitation of the underlying `DT` command.
        '''

        delay = self.dtmf_tone_fast if fast else self.dtmf_tone_slow

        time.sleep(delay)
        for tone in tones:
            self.send_command('DT', 0, '{:X}'.format(
                DTMF_TONES.index(tone.upper())))
            time.sleep(delay)

    @bandcommand
    def get_band_mode(self, band):
        return self.send_command('VM', band)

    @bandcommand
    def set_band_mode(self, band, mode):
        return self.send_command('VM', band, mode)

    @bandcommand
    def get_tx_power(self, band):
        return self.send_command('PC', band)

    @bandcommand
    def set_tx_power(self, band, power):
        return self.send_command('PC', band, power)

    @schemacommand(schema.FO)
    def get_band_vfo(self, band):
        return self.send_command('FO', band)

    @schemacommand(schema.FO)
    def set_band_vfo(self, band, settings):
        settings['band'] = band
        return self.send_command('FO', schema.FO.to_csv(settings))

    @schemacommand(schema.CC)
    def get_call_channel(self, index):
        return self.send_command('CC', index)

    @schemacommand(schema.CC)
    def set_call_channel(self, index, settings):
        settings[index] = index
        return self.send_command('CC', schema.CC.to_csv(settings))

    @schemacommand(schema.ME)
    def get_channel_entry(self, channel):
        res = self.send_command('ME', '{:03d}'.format(channel))
        res.append(self.get_channel_name(channel))
        return res

    def set_channel_entry(self, channel, settings):
        settings[channel] = channel
        self.send_command('ME', schema.ME_no_name.to_csv(settings))
        self.set_channel_name(channel, settings['name'])

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

    @schemacommand(schema.MU)
    def get_radio_config(self):
        return self.send_command('MU')

    @schemacommand(schema.MU)
    def set_radio_config(self, settings):
        return self.send_command('MU', schema.MU.to_csv(settings))

    # ----------------------------------------------------------------------

    @pm
    def get_port_speed(self):
        speed = self.read_block(M_OFFSET_PORT_SPEED, 1)
        speed = struct.unpack('B', speed)[0]
        return PORT_SPEED[speed]

    @pm
    def set_port_speed(self, speed):
        speed = PORT_SPEED.index(speed)
        self.write_block(M_OFFSET_PORT_SPEED, bytes([speed]))

    @pm
    def get_frequency_band(self, band):
        if band == 0:
            address = M_OFFSET_BANDA_BAND
        elif band == 1:
            address = M_OFFSET_BANDB_BAND
        else:
            raise ValueError('invalid band: {}'.format(band))

        res = self.read_block(address, 1)
        res = struct.unpack('B', res)[0]

        # The constants in FREQUENCY_BAND are correct for band A, but
        # for band B we need to add 4 to the value.
        res -= (4 * band)

        return FREQUENCY_BAND[res]

    @pm
    def set_frequency_band(self, band, freq_band):
        freq_band = FREQUENCY_BAND.index(freq_band)

        # The constants in FREQUENCY_BAND are correct for band A, but
        # for band B we need to add 4 to the value.
        freq_band += (4 * band)

        if band == 0:
            address = M_OFFSET_BANDA_BAND
        elif band == 1:
            address = M_OFFSET_BANDB_BAND
        else:
            raise ValueError('invalid band: {}'.format(band))

        self.write_block(address, bytes([freq_band]))

    @pm
    def reset(self):
        '''Reset to default configuration'''
        self.write_block(0, b'\xff')

    @pm
    def get_operating_mode(self):
        '''Get current radio operating mode'''

        res = self.read_block(M_OFFSET_OPERATING_MODE, 2)
        return struct.unpack('BB', res)

    @pm
    def set_operating_mode(self, repeater, wireless):
        wireless = 1 if wireless else 0
        repeater = 1 if repeater else 0

        self.write_block(M_OFFSET_OPERATING_MODE,
                         struct.pack('BB', repeater, wireless))

    @pm
    def get_remote_id(self):
        res = self.read_block(0x12, 3)
        return res

    @pm
    def set_remote_id(self, remote_id):
        if len(remote_id) != 3:
            raise ValueError('remote id must be three digits')

        self.write_block(0x12, remote_id)

    # ----------------------------------------------------------------------

    @contextmanager
    def programming_mode(self):
        '''Wrap code that interacts with the radio in programming mode.

        You must enclose calls that require programming mode with this
        context manager.  For example:

            with radio.programming_mode():
                radio.read_block(0, 0)

        Failure to use the context manager will result in
        WrongModeError exception.'''

        self.enter_programming_mode()
        try:
            yield
        finally:
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
    def read_block(self, address, size):
        '''Read data from the radio'''

        LOG.debug('read address %d, size %d', address, size)

        args = struct.pack('>HB', address, size)

        self.write_bytes(b'R' + args)
        res = self.read_bytes(4)
        if res != b'W' + args:
            raise UnexpectedResponseError(res)

        data = self.read_bytes(size if size else 256)
        self.write_bytes(bytes([6]))
        self.check_ack()
        return data

    @pm
    def write_block(self, address, data):
        '''Write data to the radio'''

        size = len(data)
        if size > 256:
            raise ValueError('write_block cannot write more than 256 bytes')

        LOG.debug('write address %d, size %d', address, size)
        if size == 256:
            size = 0

        self.write_bytes(struct.pack('>BHB', ord('W'), address, size))
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
    def memory_dump(self, fd):
        '''Read data from the radio and write it to a file-like object.'''

        for block in range(self.memory_max):
            addr = block * 256
            LOG.debug('reading block %d', block)
            data = self.read_block(addr, 0)
            fd.write(data)

    @pm
    def memory_restore(self, fd, force=False):
        '''Read data from a file-like object and write it to the radio.

        This command is similar to the behavior of the MCP-2A "Write
        data to the receiver" command"; in particular, it initially
        writes 0xFF to address 0 before proceeding to load the data
        from the input file descriptor to the radio. This will cause
        the radio to reset to defaults if the write operation is
        interrupted.'''

        magiclen = len(self.memory_magic)

        # Check that radio state seems sane
        data = self.read_block(0, magiclen)
        if data != self.memory_magic:
            if force:
                LOG.warning('Radio does not contain expected '
                            'data (continuing)')
            else:
                raise ValueError('radio does not contain expected data')

        # Check that input data seems sane
        data = fd.read(magiclen)
        if data != self.memory_magic:
            if force:
                LOG.warning('Input does not contain expected '
                            'data (continuing)')
            else:
                raise ValueError('input does not contain expected data')

        self.write_block(0, b'\xff')

        fd.seek(magiclen)
        self.write_block(magiclen, fd.read(256 - magiclen))

        for block in range(1, self.memory_max):
            addr = block * 256
            LOG.debug('writing block %d', block)
            data = fd.read(256)
            if not data:
                raise EOFError('Ran out of data in memory_restore')
            self.write_block(addr, data)

        self.write_block(0, self.memory_magic)

    # ----------------------------------------------------------------------


class TMD710(TMV71):
    expected_id = 'TM-D710'
    memory_magic = struct.pack('BB', 0x0, 0x4D)
    memory_max = 0xFF
