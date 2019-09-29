import hexdump
import logging
import serial

LOG = logging.getLogger(__name__)


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
            args_encoded = ' ' + ','.join(str(arg) for arg in args)
            self.write_bytes(args_encoded)
        self.write_bytes(b'\r')
        return self.read_line()

    def send_command(self, command, *args):
        res = self.send_command_raw(command, *args)

        if res == b'?':
            raise UnknownCommandError(command)
        elif res == b'N':
            raise InvalidCommandError(command)
        elif not res.startswith(command):
            raise UnexpectedResponseError(command)

        return res[3:].split(b',')

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

    def check_id(self, expected=b'TM-V71'):
        self.clear()

        res = self.send_command(b'ID')
        LOG.debug('verify device id: wanted %s, got %s',
                  expected, res[0])
        if res[0] != expected:
            raise UnknownDeviceError(res[0])

    # ----------------------------------------------------------------------

    def enter_programming_mode(self):
        self.write_bytes(b'0M PROGRAM\r')
        res = self.read_line()
        if res != b'0M':
            raise UnexpectedResponseError()

    def read_block(self, block, offset, length):
        self.write_bytes(bytes([ord('R'), block, 0, length]))
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
