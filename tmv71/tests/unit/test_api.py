import io
import pytest
import struct
from unittest import mock

from tmv71 import api


@pytest.fixture
def radio(serial):
    radio = api.TMV71(port='dummy', speed=0, timeout=0)
    return radio


def test_create_api_object(radio, serial):
    assert radio._port == serial
    assert radio.port == 'dummy'
    assert repr(radio) == '<TMV71 on dummy @ 0>'


def test_clear(radio, serial):
    serial.raise_next_read(api.ReadTimeoutError)
    serial.stuff(b'?\r')
    radio.clear()


def test_radio_id(radio, serial):
    serial.stuff(b'ID DUMMY\r')
    check = radio.radio_id()

    assert serial.rx.getvalue().endswith(b'ID\r')
    assert check == 'DUMMY'


def test_check_id_success(radio, serial):
    serial.stuff(b'ID TM-V71\r')
    radio.check_id()


def test_check_id_failure(radio, serial):
    serial.stuff(b'ID DUMMY\r')
    with pytest.raises(api.UnknownDeviceError):
        radio.check_id()


def test_programming_mode(radio, serial):
    serial.stuff(b'0M\r\x06\r\x00')
    with radio.programming_mode():
        assert radio._programming_mode
    assert not radio._programming_mode


def test_read_block_no_pm(radio, serial):
    with pytest.raises(api.WrongModeError):
        radio.read_block(0, 4)


def test_programming_mode_too_slow(radio, serial, monkeypatch):
    monkeypatch.setattr(api, 'LOG', mock.Mock())
    serial.stuff(b'0M\r\x15\x06\r\x00')
    with radio.programming_mode():
        radio.write_block(0, b'\x00')

    api.LOG.warning.assert_called_with('radio is in error state (continuing)')


def test_read_block(radio, serial):
    test_data = b'\x01\x02\x03\x04'

    serial.stuff(b'0M\rW\x00\x00\x04')
    serial.stuff(test_data)
    serial.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        data = radio.read_block(0, 4)
        assert serial.rx.getvalue().endswith(b'R\x00\x00\x04\x06')
        assert data == test_data


def test_write_block(radio, serial):
    test_data = b'\x01\x02\x03\x04'
    serial.stuff(b'0M\r\x06\x06\r\x00')
    with radio.programming_mode():
        radio.write_block(0, test_data)
        assert serial.rx.getvalue().endswith(test_data)


def test_write_block_invalid_size(radio, serial):
    serial.stuff(b'0M\r\x06\r\x00')
    with radio.programming_mode():
        with pytest.raises(ValueError):
            radio.write_block(0, 'N1LKS' * 1024)


def test_radio_type(radio, serial):
    serial.stuff(b'TY K,0,0,0,0\r')
    res = radio.radio_type()
    assert isinstance(res, dict)
    assert res['model'] == 'K'


def test_get_port_speed(radio, serial):
    args = struct.pack('>HB', api.M_OFFSET_PORT_SPEED, 1)
    serial.stuff(b'0M\r')
    serial.stuff(b'W' + args + b'\x00')
    serial.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        res = radio.get_port_speed()
        assert res == '9600'


def test_set_port_speed(radio, serial):
    serial.stuff(b'0M\r\x06\x06\r\x00')

    with radio.programming_mode():
        radio.set_port_speed('57600')

    assert serial.rx.getvalue().endswith(
        b'W\x00\x21\x01\x03E')


def test_get_channel_entry(radio, serial):
    serial.stuff(b'ME 000,0145430000,0,1,1,0,1,0,23,'
                 b'23,000,00600000,0,0000000000,0,0\r'
                 b'MN 000,TEST\r')
    entry = radio.get_channel_entry(0)
    assert entry['rx_freq'] == 145.43


def test_set_channel_entry(radio, serial):
    expected = {
        'channel': 0,
        'rx_freq': 145.43,
        'rx_step': 5,
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
        'admit': 'C',
        'tone': 146.2,
        'name': 'TEST'
    }
    serial.stuff(b'ME 000,0145430000,0,1,1,0,1,0,23,'
                 b'23,000,00600000,0,0000000000,0,0\r'
                 b'MN 000,TEST\r'
                 b'ME\r'
                 b'MN 000,TEST\r'
                 )
    entry = radio.get_channel_entry(0)
    assert entry == expected
    entry['lockout'] = True
    radio.set_channel_entry(0, entry)
    assert serial.rx.getvalue().endswith(
        b'ME 000,0145430000,0,1,1,0,1,0,23,'
        b'23,000,00600000,0,0000000000,0,1\r'
        b'MN 000,TEST\r'
    )


def test_memory_dump(radio, serial):
    def blockmaker(start=0x0):
        addr = start
        while True:
            args = struct.pack('>HB', addr, 0)
            yield b'W' + args
            yield b'\x00' * 256
            yield b'\x06'
            addr += 256

    buf = io.BytesIO()
    serial.stuff(b'0M\r')
    with radio.programming_mode():
        with serial.tx_from_iter(blockmaker()):
            radio.memory_dump(buf)
        serial.stuff(b'\x06\r\x00')

    assert buf.tell() == (radio.memory_max * 256)


def test_memory_restore(radio, serial):
    serial.stuff(b'0M\rW\x00\x00' + struct.pack('B', len(radio.memory_magic)))
    serial.stuff(radio.memory_magic)

    # We will need to fake responses to 127 individual write
    # commands.
    serial.stuff(b'\x06' * 127)
    serial.stuff(b'\x06\x06\x06\x06\r\x00')

    fd = io.BytesIO()
    fill_data = b'\x01\x02\x03\x04'
    fd.write(fill_data * (0x7f00//len(fill_data)))
    fd.seek(0)
    fd.write(radio.memory_magic)
    fd.seek(0)

    with radio.programming_mode():
        radio.memory_restore(fd)

    assert serial.rx.getvalue().endswith(
        b'W~\x00\x00'
        + fd.getvalue()[-256:]
        + b'W\x00\x00\x02\x00KE'
    )


def test_memory_restore_bad_data(radio, serial):
    serial.stuff(b'0M\rW\x00\x00' + struct.pack('B', len(radio.memory_magic)))
    serial.stuff(radio.memory_magic)
    serial.stuff(b'\x06\x06\r\x00')

    fd = io.BytesIO(b'\x00' * 4)

    with radio.programming_mode():
        with pytest.raises(ValueError):
            radio.memory_restore(fd)


def test_memory_restore_short_data(radio, serial):
    serial.stuff(b'0M\rW\x00\x00' + struct.pack('B', len(radio.memory_magic)))
    serial.stuff(radio.memory_magic)
    serial.stuff(b'\x06\x06\x06\x06\r\x00')

    fd = io.BytesIO(radio.memory_magic)

    with radio.programming_mode():
        with pytest.raises(EOFError):
            radio.memory_restore(fd)


def test_ptt_context(radio, serial):
    serial.stuff(b'TX 1\r')
    serial.stuff(b'RX 1\r')

    assert not radio._ptt
    with radio.ptt():
        assert radio._ptt

    assert serial.rx.getvalue() == b'TX\rRX\r'


@pytest.mark.parametrize('band', [0, 1])
def test_get_frequency_band(radio, serial, band):
    val = api.FREQUENCY_BAND.index('144')
    if band == 0:
        offset = api.M_OFFSET_BANDA_BAND
        val_adjusted = val
    else:
        offset = api.M_OFFSET_BANDB_BAND
        val_adjusted = val + 4

    serial.stuff(b'0M\rW')
    serial.stuff(struct.pack('>HB', offset, 1))
    serial.stuff(struct.pack('B', val_adjusted))
    serial.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        res = radio.get_frequency_band(band)

    expected = b'R' + struct.pack('>HB', offset, 1)
    assert expected in serial.rx.getvalue()
    assert res == api.FREQUENCY_BAND[val]


def test_get_frequency_band_invalid(radio, serial):
    serial.stuff(b'0M\r')
    serial.stuff(b'\x06\r\x00')
    with radio.programming_mode():
        with pytest.raises(ValueError):
            radio.get_frequency_band(2)


def test_set_frequency_band(radio, serial):
    offset = api.M_OFFSET_BANDA_BAND
    serial.stuff(b'0M\r')
    serial.stuff(b'\x06\x06\r\x00')

    with radio.programming_mode():
        radio.set_frequency_band(0, '430')

    index = api.FREQUENCY_BAND.index('430')
    expected = b'W' + struct.pack('>HBB', offset, 1, index)
    assert expected in serial.rx.getvalue()


def test_get_tx_power(radio, serial):
    serial.stuff(b'PC 0,1\r')
    res = radio.get_tx_power(0)
    assert res == 1


def test_set_tx_power(radio, serial):
    serial.stuff(b'PC 0,2\r')
    res = radio.set_tx_power(0, 2)
    assert res == 2


def test_read_bytes_timeout(radio, serial):
    with pytest.raises(api.ReadTimeoutError):
        radio.read_bytes(1)


def test_unknown_command(radio, serial):
    serial.stuff(b'?\r')
    with pytest.raises(api.UnknownCommandError):
        radio.radio_id()


def test_invalid_command(radio, serial):
    serial.stuff(b'N\r')
    with pytest.raises(api.InvalidCommandError):
        radio.radio_id()


def test_unexpected_response(radio, serial):
    serial.stuff(b'DUMMY\r')
    with pytest.raises(api.UnexpectedResponseError):
        radio.radio_id()


def test_send_dtmf(radio, serial):
    serial.stuff(b'DT\rDT\r')
    radio.send_dtmf('12')
    assert b'DT 0,1\rDT 0,2\r' in serial.rx.getvalue()


def test_radio_serial(radio, serial):
    serial.stuff(b'AE 12345,321\r')
    res = radio.radio_serial()

    assert res == dict(serial='12345', extra='321')


def test_radio_firmware(radio, serial):
    serial.stuff(b'FV 0,1.0,2.0,A,1\r')
    res = radio.radio_firmware()

    assert res == dict(unit=0, v1='1.0', v2='2.0', v3='A', v4='1')


def test_get_band_squelch(radio, serial):
    serial.stuff(b'SQ 0A\r')
    res = radio.get_band_squelch(0)

    assert res == 0x0A
    assert b'SQ 0\r' in serial.rx.getvalue()


def test_get_band_squelch_state(radio, serial):
    serial.stuff(b'BY 0,0\r')
    res = radio.get_band_squelch_state(0)

    assert res == 0
    assert b'BY 0\r' in serial.rx.getvalue()


def test_reopen(radio, serial):
    radio.reopen()
    serial.close.assert_called()
    serial.open.assert_called()


def test_get_band_reverse(radio, serial):
    serial.stuff(b'AS 0,1\r')
    res = radio.get_band_reverse(0)

    assert res == 1
    assert b'AS 0\r' in serial.rx.getvalue()


def test_set_band_reverse(radio, serial):
    serial.stuff(b'AS 0,1\r')
    res = radio.set_band_reverse(0, 1)

    assert res == 1
    assert b'AS 0,1\r' in serial.rx.getvalue()


def test_get_lock_state(radio, serial):
    serial.stuff(b'LK 1\r')
    res = radio.get_lock_state()
    assert res == 1
    assert b'LK\r' in serial.rx.getvalue()


def test_set_lock_state(radio, serial):
    serial.stuff(b'LK 1\r')
    res = radio.set_lock_state(True)
    assert res == 1
    assert b'LK 1\r' in serial.rx.getvalue()


def test_get_band_mode(radio, serial):
    serial.stuff(b'VM 0,0\r')
    res = radio.get_band_mode(0)
    assert res == 0
    assert b'VM 0\r' in serial.rx.getvalue()


def test_set_band_mode(radio, serial):
    serial.stuff(b'VM 0,1\r')
    res = radio.set_band_mode(0, 1)
    assert res == 1
    assert b'VM 0,1\r' in serial.rx.getvalue()


def test_get_poweron_message(radio, serial):
    serial.stuff(b'MS DUMMY\r')
    res = radio.get_poweron_message()
    assert res == 'DUMMY'
    assert b'MS\r' in serial.rx.getvalue()


def test_set_poweron_message(radio, serial):
    serial.stuff(b'MS DUMMY\r')
    res = radio.set_poweron_message('DUMMY')
    assert res == 'DUMMY'
    assert b'MS DUMMY\r' in serial.rx.getvalue()


def test_get_ptt_ctrl(radio, serial):
    serial.stuff(b'BC 0,0\r')
    res = radio.get_ptt_ctrl()
    assert res == dict(ptt=0, ctrl=0)


def test_set_ptt_ctrl(radio, serial):
    serial.stuff(b'BC 0,0\r')
    res = radio.set_ptt_ctrl(0, 0)
    assert res == dict(ptt=0, ctrl=0)


def test_get_dual_band_mode(radio, serial):
    serial.stuff(b'DL 0\r')
    res = radio.get_dual_band_mode()
    assert res == 0


def test_set_dual_band_mode(radio, serial):
    serial.stuff(b'DL 0\r')
    res = radio.set_dual_band_mode()
    assert res == 0


def test_set_single_band_mode(radio, serial):
    serial.stuff(b'DL 1\r')
    res = radio.set_single_band_mode()
    assert res == 1


def test_get_channel(radio, serial):
    serial.stuff(b'MR 0,000\r')
    res = radio.get_channel(0)
    assert res == 0


def test_set_channel(radio, serial):
    serial.stuff(b'MR 0,000\r')
    res = radio.set_channel(0, 0)
    assert res == 0
    assert b'MR 0,000' in serial.rx.getvalue()


def test_get_band_vfo(radio, serial):
    serial.stuff(b'FO 0,0145430000,0,2,0,0,1,0,23,23,000,00600000,0\r')
    res = radio.get_band_vfo(0)
    assert res == dict(
        band=0,
        ctcss_freq=146.2,
        ctcss_status=True,
        dcs_code=23,
        dcs_status=False,
        mode='FM',
        offset=0.6,
        reverse=False,
        rx_freq=145.43,
        shift='DOWN',
        rx_step=5,
        tone_freq=146.2,
        tone_status=False,
    )


def test_set_band_vfo(radio, serial):
    fo1 = b'FO 0,0145430000,0,2,0,0,1,0,23,23,000,00600000,0\r'
    fo2 = b'FO 0,0144000000,0,2,0,0,1,0,23,23,000,00600000,0\r'
    serial.stuff(fo1 + fo2)
    res = radio.get_band_vfo(0)
    res['rx_freq'] = 144.0
    res = radio.set_band_vfo(0, res)
    assert res == dict(
        band=0,
        ctcss_freq=146.2,
        ctcss_status=True,
        dcs_code=23,
        dcs_status=False,
        mode='FM',
        offset=0.6,
        reverse=False,
        rx_freq=144.0,
        shift='DOWN',
        rx_step=5,
        tone_freq=146.2,
        tone_status=False,
    )

    assert fo2 in serial.rx.getvalue()


def test_get_call_channel(radio, serial):
    serial.stuff(b'CC 0,0146520000,0,0,0,0,0,0,08,08,'
                 b'000,00600000,0,0000000000,0\r')
    res = radio.get_call_channel(0)
    assert res == dict(
        index=0,
        rx_freq=146.52,
        tone_freq=88.5,
        offset=0.6,
        unknown='0',
        mode='FM',
        tx_freq=0.0,
        ctcss_status=False,
        reverse=False,
        dcs_status=False,
        tone_status=False,
        dcs_code=23,
        ctcss_freq=88.5,
        rx_step=5,
        shift='SIMPLEX'
    )


def test_set_call_channel(radio, serial):
    s1 = b'CC 0,0146520000,0,0,0,0,0,0,08,08,000,00600000,0,0000000000,0\r'
    s2 = b'CC 0,0144000000,0,0,0,0,0,0,08,08,000,00600000,0,0000000000,0\r'
    serial.stuff(s1 + s2)

    res = radio.get_call_channel(0)
    res['rx_freq'] = 144.0
    res = radio.set_call_channel(0, res)
    assert s2 in serial.rx.getvalue()
