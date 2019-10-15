import binascii
import json
import os
import pytest
import tempfile

from click.testing import CliRunner
from tmv71 import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def environ():
    os.environ["TMV71_NO_CONFIG"] = "1"
    os.environ["TMV71_PORT"] = "dummy"
    os.environ["TMV71_NO_CLEAR"] = "1"


def test_main(runner):
    res = runner.invoke(cli.main, "--help")
    assert res.exit_code == 0


def test_info_id(runner, serial, environ):
    serial.stuff(b"ID DUMMY\r")
    res = runner.invoke(cli.main, ["info", "id"])
    assert res.exit_code == 0
    assert serial.rx.getvalue() == b"ID\r"
    assert res.output == "DUMMY\n"


def test_info_id_debug(runner, serial, environ):
    serial.stuff(b"ID DUMMY\r")
    res = runner.invoke(cli.main, ["-vvv", "info", "id"])
    assert res.exit_code == 0
    assert serial.rx.getvalue() == b"ID\r"
    assert "49 44 20 44 55 4D 4D 59" in res.output


def test_info_type(runner, serial, environ):
    serial.stuff(b"TY K,1,0,1,0\r")
    res = runner.invoke(cli.main, ["info", "type"])
    assert res.exit_code == 0
    assert "model=K" in res.output
    assert "mars_tx_expansion=1" in res.output


def test_info_type_json(runner, serial, environ):
    expected = dict(
        model="K", mars_tx_expansion=1, max_tx_expansion=0, crossband=1, skycommand=0
    )

    serial.stuff(b"TY K,1,0,1,0\r")
    res = runner.invoke(cli.main, ["info", "type", "-F", "json"])
    assert res.exit_code == 0
    res_decoded = json.loads(res.output)
    assert res_decoded == expected


def test_memory_read_block(runner, serial, environ):
    test_data = b"\x01\x02\x03\x04"

    serial.stuff(b"0M\rW\x00\x00\x04")
    serial.stuff(test_data)
    serial.stuff(b"\x06\x06\r\x00")

    with tempfile.NamedTemporaryFile() as tmp:
        res = runner.invoke(
            cli.main, ["memory", "read-block", "0", "-l", "4", "-o", tmp.name]
        )
        assert res.exit_code == 0

        tmp.seek(0)
        val = tmp.read()
        assert test_data in val


def test_memory_read_block_hexdump(runner, serial, environ):
    test_data = b"\x01\x02\x03\x04"

    serial.stuff(b"0M\rW\x00\x00\x04")
    serial.stuff(test_data)
    serial.stuff(b"\x06\x06\r\x00")

    with tempfile.NamedTemporaryFile() as tmp:
        res = runner.invoke(
            cli.main,
            ["memory", "read-block", "0", "-l", "4", "--hexdump", "-o", tmp.name],
        )
        assert res.exit_code == 0

        tmp.seek(0)
        val = tmp.read()
        assert b"00000000: 01 02 03 04" in val


def test_memory_write_block(runner, serial, environ):
    expected = b"\x01\x02\x03\x04"
    expected_hex = binascii.hexlify(expected)

    serial.stuff(b"0M\r")
    serial.stuff(b"\x06\x06\r\x00")

    res = runner.invoke(cli.main, ["memory", "write-block", "0", "-d", expected_hex])
    assert res.exit_code == 0
    assert expected in serial.rx.getvalue()


def test_info_firmware(runner, serial, environ):
    serial.stuff(b"FV 0,1.0,2.0,A,1\r")
    res = runner.invoke(cli.main, ["info", "firmware", "-F", "json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data == dict(unit=0, v1="1.0", v2="2.0", v3="A", v4="1")


def test_band_select(runner, serial, environ):
    serial.stuff(b"BC 1,1\r")
    serial.stuff(b"DL 0\r")
    serial.stuff(b"BC 1,1\r")
    res = runner.invoke(cli.main, ["band", "select", "B", "-F", "json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data == dict(ctrl=1, ptt=1, mode="dual")
