import io
import pytest

from tmv71 import api


class FakeSerialPort:
    def __init__(self, port, **kwargs):
        self.rx = io.BytesIO()
        self.tx = io.BytesIO()
        self.exc = None

    def raise_next_read(self, exc):
        self.exc = exc

    def stuff(self, data):
        pos = self.tx.tell()
        self.tx.seek(0, 2)
        self.tx.write(data)
        self.tx.seek(pos)

    def read(self, size=1):
        if self.exc is not None:
            exc = self.exc
            self.exc = None
            raise exc()

        data = self.tx.read(size)
        return data

    def read_until(self, terminator=b'\n', size=None):
        acc = []
        while True:
            res = self.read()
            acc.append(res)
            if res == terminator or (size is not None and len(acc) >= size):
                break

        return b''.join(acc)

    def write(self, data):
        return self.rx.write(data)

    def reset(self):
        self.rx.truncate(0)
        self.tx.truncate(0)


@pytest.fixture
def patch_serial(monkeypatch):
    monkeypatch.setattr(api.serial, 'Serial', FakeSerialPort)


@pytest.fixture
def radio(patch_serial):
    radio = api.TMV71(dev='dummy', speed=0, timeout=0)
    return radio


class TestApi:
    def test_create_api_object(self, radio):
        assert radio.dev == 'dummy'

    def test_clear(self, radio):
        radio._port.raise_next_read(api.ReadTimeoutError)
        radio._port.stuff(b'?\r')
        radio.clear()

    def test_radio_id(self, radio):
        radio._port.stuff(b'ID DUMMY\r')
        check = radio.radio_id()

        assert radio._port.rx.getvalue().endswith(b'ID\r')
        assert check == ['DUMMY']

    def test_programming_mode(self, radio):
        radio._port.stuff(b'0M\r\x06\r\x00')
        with radio.programming_mode():
            assert radio._programming_mode
        assert not radio._programming_mode

    def test_read_block_no_pm(self, radio):
        with pytest.raises(api.WrongModeError):
            radio.read_block(0, 0, 4)

    def test_read_block(self, radio):
        test_data = b'\x01\x02\x03\x04'

        radio._port.stuff(b'0M\rW\x00\x00\x04')
        radio._port.stuff(test_data)
        radio._port.stuff(b'\x06\x06\r\x00')

        with radio.programming_mode():
            data = radio.read_block(0, 0, 4)
            assert radio._port.rx.getvalue().endswith(b'R\x00\x00\x04\x06')
            assert data == test_data

    def test_radio_type(self, radio):
        radio._port.stuff(b'TY K,0,0,0,0\r')
        res = radio.radio_type()
        assert isinstance(res, dict)
        assert res['model'] == 'K'

    def test_get_port_speed(self, radio):
        block, offset = api.M_OFFSET_PORT_SPEED

        radio._port.stuff(b'0M\rW\x00\x00\x04\x03')
        radio._port.stuff(b'\x06\x06\r\x00')

        with radio.programming_mode():
            res = radio.get_port_speed()
            assert res == '57600'

    def test_set_port_speed(self, radio):
        block, offset = api.M_OFFSET_PORT_SPEED

        radio._port.stuff(b'0M\r\x06\x06\r\x00')

        with radio.programming_mode():
            radio.set_port_speed('57600')

        assert radio._port.rx.getvalue().endswith(
            b'W\x00\x21\x01\x03E')

    def test_get_channel_entry(self, radio):
        radio._port.stuff(b'ME 000,0145430000,0,1,1,0,1,0,23,'
                          b'23,000,00600000,0,0000000000,0,0\r')
        entry = radio.get_channel_entry(0)
        assert entry['rx_freq'] == 145.43

    def test_set_channel_entry(self, radio):
        expected = {
            'channel': 0,
            'rx_freq': 145.43,
            'step': 5,
            'shift': 'UP',
            'reverse': True,
            'tone_status': False,
            'ctcss_status': True,
            'dcs_status': False,
            'tone_freq': 146.2,
            'ctcss_freq': 146.2,
            'dcs_freq': 23,
            'offset': 0.6,
            'mode': 'FM',
            'tx_freq': 0.0,
            'tx_step': 5,
            'lockout': False,
        }
        radio._port.stuff(b'ME 000,0145430000,0,1,1,0,1,0,23,'
                          b'23,000,00600000,0,0000000000,0,0\r'
                          b'ME\r')
        entry = radio.get_channel_entry(0)
        assert entry == expected
        entry['lockout'] = True
        radio.set_channel_entry(0, entry)
        assert radio._port.rx.getvalue() == (
            b'ME 000\rME 000,0145430000,0,1,1,0,1,0,23,'
            b'23,000,00600000,0,0000000000,0,1\r'
        )
