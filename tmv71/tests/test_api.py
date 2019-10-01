import pytest
from unittest import mock

from tmv71 import api


@pytest.fixture
def radio(monkeypatch):
    monkeypatch.setattr(api.serial, 'Serial', mock.MagicMock())
    monkeypatch.setattr(api.TMV71, 'read_line', mock.MagicMock())
    monkeypatch.setattr(api.TMV71, 'read_bytes', mock.MagicMock())
    monkeypatch.setattr(api.TMV71, 'write_bytes', mock.MagicMock())

    radio = api.TMV71(dev='dummy', speed=0, timeout=0)
    return radio


class TestApi:
    def test_create_api_object(self, radio):
        assert radio.dev == 'dummy'

    def test_radio_id(self, radio):
        radio.read_line.return_value = b'ID DUMMY'
        check = radio.radio_id()

        radio.write_bytes.assert_any_call(b'ID')
        assert check == ['DUMMY']

    def test_programming_mode(self, radio):
        radio.read_line.side_effect = [b'0M']
        radio.read_bytes.side_effect = [b'\x06', b'\r', b'\x00']
        with radio.programming_mode():
            assert radio._programming_mode
        assert not radio._programming_mode

    def test_read_block_no_pm(self, radio):
        with pytest.raises(api.WrongModeError):
            radio.read_block(0, 0, 4)

    def test_read_block(self, radio):
        test_data = b'\x01\x02\x03\x04'

        radio.read_line.side_effect = [b'0M']
        radio.read_bytes.side_effect = [b'W\x00\x00\x04', test_data, b'\x06',
                                        b'\x06', b'\r', b'\x00']
        with radio.programming_mode():
            data = radio.read_block(0, 0, 4)
            radio.write_bytes.assert_any_call(b'R\x00\x00\x04')
            assert data == test_data

    def test_radio_type(self, radio):
        radio.read_line.return_value = b'TY K,0,0,0,0'
        res = radio.radio_type()
        assert isinstance(res, dict)
        assert res['model'] == 'K'

    def test_get_port_speed(self, radio):
        block, offset = api.M_OFFSET_PORT_SPEED

        radio.read_line.side_effect = [b'0M']
        radio.read_bytes.side_effect = [b'W\x00\x00\x04', b'\x03', b'\x06',
                                        b'\x06', b'\r', b'\x00']
        with radio.programming_mode():
            res = radio.get_port_speed()
            assert res == '57600'
