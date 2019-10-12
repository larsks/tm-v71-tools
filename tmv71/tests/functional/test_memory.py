import pytest

from tmv71 import memory


@pytest.fixture
def initial(request):
    try:
        fd = open('dumps/initial.bin', 'rb')
        yield memory.Memory.from_io(fd)
    finally:
        fd.close()


def test_remote_id(initial):
    assert initial.misc_settings.remote_id == b'000'


def test_port_speed(initial):
    assert initial.misc_settings.pc_port_speed == initial.PortSpeed.b9600


@pytest.mark.parametrize('attr,value', [
    ('power_on_message', 'HELLO !!'),
    ('beep', 1),
    ('beep_volume', 4),
    ('ptt_band', 0),
    ('ctrl_band', 0),
    ('group_link', ''),
])
def test_pm_settings(initial, attr, value):
    assert getattr(initial.program_memory[0], attr) == value


@pytest.mark.parametrize('band', [0, 1])
def test_pm_band_mask(initial, band):
    assert initial.program_memory[0].band_masks[band].mask == [1, 1, 1, 1, 1]


@pytest.mark.parametrize('band,freq_band,rx_freq', [
    (0, 0, 118.000),
    (0, 1, 144.000),
    (0, 2, 223.000),
    (0, 3, 340.000),
    (0, 4, 440.000),
    (1, 0, 144.000),
    (1, 1, 223.000),
    (1, 2, 340.000),
    (1, 3, 440.000),
    (1, 4, 1240.000),
])
def test_vfo_settings(initial, band, freq_band, rx_freq):
    assert (
        initial.program_memory[0].vfo_settings[band].
        list[freq_band].rx_freq == rx_freq
    )


@pytest.mark.parametrize('band,freq_band', [
    (0, memory.Memory.FreqBand.band_144),
    (1, memory.Memory.FreqBand.band_430),
])
def test_band_config(initial, band, freq_band):
    assert (
        initial.program_memory[0].bands[band].display_mode ==
        initial.DisplayMode.vfo
    )
    assert (
        initial.program_memory[0].bands[band].freq_band ==
        freq_band
    )
    assert (
        initial.program_memory[0].bands[band].tx_power ==
        initial.TxPower.high
    )
