import pytest
from tmv71 import api

from fakeserial import FakeSerialPort


@pytest.fixture
def serial(monkeypatch):
    monkeypatch.setattr(api.serial, 'Serial', FakeSerialPort)
    port = FakeSerialPort('dummy', register=True)
    port.clear()
    return port
