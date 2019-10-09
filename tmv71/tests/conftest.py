import pytest
from tmv71 import api

from fakeserial import FakeSerialPortFactory


@pytest.fixture
def serial(monkeypatch):
    monkeypatch.setattr(api.serial, 'Serial', FakeSerialPortFactory)
    port = FakeSerialPortFactory('dummy', register=True)
    port.clear()
    return port
