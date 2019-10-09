import io
import pytest
import struct

from tmv71 import api


@pytest.fixture
def radio(serial):
    radio = api.TMV71(port='dummy', speed=0, timeout=0)
    return radio


def test_create_api_object(radio):
    assert radio.port == 'dummy'
    assert repr(radio) == '<TMV71 on dummy @ 0>'


def test_clear(radio):
    radio._port.raise_next_read(api.ReadTimeoutError)
    radio._port.stuff(b'?\r')
    radio.clear()


def test_radio_id(radio):
    radio._port.stuff(b'ID DUMMY\r')
    check = radio.radio_id()

    assert radio._port.rx.getvalue().endswith(b'ID\r')
    assert check == 'DUMMY'


def test_check_id_success(radio):
    radio._port.stuff(b'ID TM-V71\r')
    radio.check_id()


def test_check_id_failure(radio):
    radio._port.stuff(b'ID DUMMY\r')
    with pytest.raises(api.UnknownDeviceError):
        radio.check_id()


def test_programming_mode(radio):
    radio._port.stuff(b'0M\r\x06\r\x00')
    with radio.programming_mode():
        assert radio._programming_mode
    assert not radio._programming_mode


def test_read_block_no_pm(radio):
    with pytest.raises(api.WrongModeError):
        radio.read_block(0, 4)


def test_read_block(radio):
    test_data = b'\x01\x02\x03\x04'

    radio._port.stuff(b'0M\rW\x00\x00\x04')
    radio._port.stuff(test_data)
    radio._port.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        data = radio.read_block(0, 4)
        assert radio._port.rx.getvalue().endswith(b'R\x00\x00\x04\x06')
        assert data == test_data


def test_radio_type(radio):
    radio._port.stuff(b'TY K,0,0,0,0\r')
    res = radio.radio_type()
    assert isinstance(res, dict)
    assert res['model'] == 'K'


def test_get_port_speed(radio):
    radio._port.stuff(b'0M\rW\x00\x00\x04\x03')
    radio._port.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        res = radio.get_port_speed()
        assert res == '57600'


def test_set_port_speed(radio):
    radio._port.stuff(b'0M\r\x06\x06\r\x00')

    with radio.programming_mode():
        radio.set_port_speed('57600')

    assert radio._port.rx.getvalue().endswith(
        b'W\x00\x21\x01\x03E')


def test_get_channel_entry(radio):
    radio._port.stuff(b'ME 000,0145430000,0,1,1,0,1,0,23,'
                      b'23,000,00600000,0,0000000000,0,0\r')
    entry = radio.get_channel_entry(0)
    assert entry['rx_freq'] == 145.43


def test_set_channel_entry(radio):
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
        'dcs_code': 23,
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


def test_memory_restore(radio):
    radio._port.stuff(b'0M\rW\x00\x00\x04')
    radio._port.stuff(radio.memory_magic)

    # We will need to fake responses to 127 individual write
    # commands.
    radio._port.stuff(b'\x06' * 127)
    radio._port.stuff(b'\x06\x06\x06\x06\r\x00')

    fd = io.BytesIO(radio.memory_magic + b'\x00' * 32508)

    with radio.programming_mode():
        radio.memory_restore(fd)


def test_memory_restore_bad_data(radio):
    radio._port.stuff(b'0M\rW\x00\x00\x04')
    radio._port.stuff(radio.memory_magic)
    radio._port.stuff(b'\x06\x06\r\x00')

    fd = io.BytesIO(b'\x00' * 4)

    with radio.programming_mode():
        with pytest.raises(ValueError):
            radio.memory_restore(fd)


def test_memory_restore_short_data(radio):
    radio._port.stuff(b'0M\rW\x00\x00\x04')
    radio._port.stuff(radio.memory_magic)
    radio._port.stuff(b'\x06\x06\x06\x06\r\x00')

    fd = io.BytesIO(radio.memory_magic)

    with radio.programming_mode():
        with pytest.raises(EOFError):
            radio.memory_restore(fd)


def test_ptt_context(radio):
    radio._port.stuff(b'TX 1\r')
    radio._port.stuff(b'RX 1\r')

    assert not radio._ptt
    with radio.ptt():
        assert radio._ptt

    assert radio._port.rx.getvalue() == b'TX\rRX\r'


def test_get_frequency_band(radio):
    offset = api.M_OFFSET_BANDA_BAND
    radio._port.stuff(b'0M\rW')
    radio._port.stuff(struct.pack('>HB', offset, 1))
    radio._port.stuff(struct.pack('B', 1))
    radio._port.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        res = radio.get_frequency_band(0)

    expected = b'R' + struct.pack('>HB', offset, 1)
    assert expected in radio._port.rx.getvalue()
    assert res == api.FREQUENCY_BAND[1]


def test_set_frequency_band(radio):
    offset = api.M_OFFSET_BANDA_BAND
    radio._port.stuff(b'0M\r')
    radio._port.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        radio.set_frequency_band(0, '430')

    index = api.FREQUENCY_BAND.index('430')
    expected = b'W' + struct.pack('>HBB', offset, 1, index)
    assert expected in radio._port.rx.getvalue()


def test_get_tx_power(radio):
    radio._port.stuff(b'PC 0,1\r')
    res = radio.get_tx_power(0)
    assert res == 1


def test_set_tx_power(radio):
    radio._port.stuff(b'PC 0,2\r')
    res = radio.set_tx_power(0, 2)
    assert res == 2


def test_read_bytes_timeout(radio):
    with pytest.raises(api.ReadTimeoutError):
        radio.read_bytes(1)


def test_unknown_command(radio):
    radio._port.stuff(b'?\r')
    with pytest.raises(api.UnknownCommandError):
        radio.radio_id()


def test_invalid_command(radio):
    radio._port.stuff(b'N\r')
    with pytest.raises(api.InvalidCommandError):
        radio.radio_id()


def test_unexpected_response(radio):
    radio._port.stuff(b'DUMMY\r')
    with pytest.raises(api.UnexpectedResponseError):
        radio.radio_id()


def test_send_dtmf(radio):
    radio._port.stuff(b'DT\rDT\r')
    radio.send_dtmf('12')
    assert b'DT 0,1\rDT 0,2\r' in radio._port.rx.getvalue()
