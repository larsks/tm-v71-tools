# A CLI and Python API for managing your TM-V71 radio

## Requirements

You will need Python 3.7 (or later), and recent versions of the `setuptools` package (and probably `pip`).

## Installation

You can install this from PyPI using `pip`:

```
pip install tm-v71-tools
```

Or you can install it straight from the GitHub repository:

```
pip install git+https://github.com/larsks/tm-v71-tools
```

## Configuration

You can set the `TMV71_PORT` and `TMV71_SPEED` environment variables, or pass the `--port` and `--speed` options to the `tmv71` command.

## Available commands

<!-- start command list -->
- [band-mode](#band-mode)
- [channel](#channel)
- [control-band](#control-band)
- [dual-band](#dual-band)
- [entry](#entry)
- [firmware](#firmware)
- [frequency-band](#frequency-band)
- [id](#id)
- [poweron-message](#poweron-message)
- [port-speed](#port-speed)
- [ptt](#ptt)
- [tune](#tune)
- [txpower](#txpower)
- [type](#type)
- [export-channels](#export-channels)
- [import-channels](#import-channels)
- [memory read](#memory-read)
- [memory write](#memory-write)
- [memory read-block](#memory-read-block)
- [memory write-block](#memory-write-block)
- [raw](#raw)
<!-- end command list -->

<!-- start command docs -->
### band-mode

```
Usage: tmv71 band-mode [OPTIONS] [0|A|1|B]

  Set selected band to VFO, MEM, call channel, or weather.

Options:
  --vfo
  --mem, --memory
  --call
  --wx, --weather
  --help           Show this message and exit.
```

### channel

```
Usage: tmv71 channel [OPTIONS] [0|A|1|B] [CHANNEL]

  Get or set the memory channel for the selected band.

Options:
  --help  Show this message and exit.
```

### control-band

```
Usage: tmv71 control-band [OPTIONS]

  Select control and ptt band.

Options:
  -c, --control INTEGER
  -p, --ptt INTEGER
  -b, --both, --cp INTEGER
  --help                    Show this message and exit.
```

### dual-band

```
Usage: tmv71 dual-band [OPTIONS]

  Get or set dual-band mode for the control band.

Options:
  -1, --single
  -2, --dual
  --help        Show this message and exit.
```

### entry

```
Usage: tmv71 entry [OPTIONS] CHANNEL

  View or edit memory channels.

Options:
  --rx-freq, --rx FLOAT
  --tx-freq, --tx FLOAT
  --step FLOAT
  --shift [SIMPLEX|UP|DOWN|SPLIT]
  --reverse INTEGER
  --tone-status INTEGER
  --ctcss-status INTEGER
  --dcs-status INTEGER
  --tone-freq FLOAT
  --ctcss-freq FLOAT
  --dcs-freq INTEGER
  --offset FLOAT
  --mode [FM|AM|NFM]
  --lockout / --no-lockout
  -n, --name TEXT
  --help                          Show this message and exit.
```

### firmware

```
Usage: tmv71 firmware [OPTIONS]

  Return information about the radio firmware.

Options:
  --help  Show this message and exit.
```

### frequency-band

```
Usage: tmv71 frequency-band [OPTIONS] [0|A|1|B] [118|144|220|300|430|1200]

  Get or set the frequency band for the selected radio band.

  Frequency bands are named using the names from "SELECTING A FREQUENCY
  BAND" in the TM-V71 manual. Note that band A and band B support a
  different subset of the available frequencies.

Options:
  --help  Show this message and exit.
```

### id

```
Usage: tmv71 id [OPTIONS]

  Return the radio model.

Options:
  --help  Show this message and exit.
```

### poweron-message

```
Usage: tmv71 poweron-message [OPTIONS] [MESSAGE]

  Get or set the power on message.

Options:
  --help  Show this message and exit.
```

### port-speed

```
Usage: tmv71 port-speed [OPTIONS] [[9600|19200|38400|57600]]

  Get or set the PC port speed.

  Note that because this command involves reading from/writing to memory
  directly, it will briefly reset the radio.

  Valid port speeds are 9600, 19200, 38400, and 57600.

Options:
  --help  Show this message and exit.
```

### ptt

```
Usage: tmv71 ptt [OPTIONS]

  Activate or deactivate transmitter.

Options:
  --on
  --off
  --help  Show this message and exit.
```

### tune

```
Usage: tmv71 tune [OPTIONS] [0|A|1|B]

Options:
  --rx-freq, --rx FLOAT
  --tx-freq, --tx FLOAT
  --step FLOAT
  --shift [SIMPLEX|UP|DOWN|SPLIT]
  --reverse INTEGER
  --tone-status INTEGER
  --ctcss-status INTEGER
  --dcs-status INTEGER
  --tone-freq FLOAT
  --ctcss-freq FLOAT
  --dcs-freq INTEGER
  --offset FLOAT
  --mode [FM|AM|NFM]
  --lockout / --no-lockout
  --help                          Show this message and exit.
```

### txpower

```
Usage: tmv71 txpower [OPTIONS] [0|A|1|B]

  Set tx power for the selected band.

Options:
  --low
  --medium, --med
  --high
  --help           Show this message and exit.
```

### type

```
Usage: tmv71 type [OPTIONS]

  Return the radio type.

Options:
  --help  Show this message and exit.
```

### export-channels

```
Usage: tmv71 export-channels [OPTIONS]

  Export channels to a CSJ document.

  A CSJ document is like a CSV document, but each field is valid JSON.

Options:
  -o, --output FILENAME
  -c, --channels TEXT
  --help                 Show this message and exit.
```

### import-channels

```
Usage: tmv71 import-channels [OPTIONS]

  Import channels from a CSJ document.

  A CSJ document is like a CSV document, but each field is valid JSON.

  Use --sync to delete channels on the radio that do not exist in the input
  document.

Options:
  -i, --input FILENAME
  -s, --sync
  --help                Show this message and exit.
```

### memory read

```
Usage: tmv71 memory read [OPTIONS]

  Read radio memory and write it to a file.

Options:
  -o, --output FILENAME
  --help                 Show this message and exit.
```

### memory write

```
Usage: tmv71 memory write [OPTIONS]

  Read memory dump from a file and write it to the radio.

Options:
  -i, --input FILENAME
  --help                Show this message and exit.
```

### memory read-block

```
Usage: tmv71 memory read-block [OPTIONS] BLOCK [OFFSET] [LENGTH]

  Read a memory block from the radio.

Options:
  -o, --output FILENAME
  --help                 Show this message and exit.
```

### memory write-block

```
Usage: tmv71 memory write-block [OPTIONS] BLOCK [OFFSET] [LENGTH]

  Write data to radio memory

Options:
  -i, --input FILENAME
  -d, --hexdata TEXT
  --help                Show this message and exit.
```

### raw

```
Usage: tmv71 raw [OPTIONS] COMMAND [ARGS]...

  Send a raw command to the radio and display the response.

Options:
  --help  Show this message and exit.
```

<!-- end command docs -->

## CLI Examples

### Specify port and speed on the command line

```
tmv71 --port /dev/ttyS0 --speed 9600 id
```

### Export channels to a CSV

```
tmv71 export-channels -o channels.csv
```

### Import channels from a CSV

```
tmv71 import-channels -i channels.csv
```

### Export only channels 1-10

```
tmv71 export-channels -o channels.csv -c 1:10
```

### Back up your radio

```
tmv71 memory read -o backup.dat
```

### Restore from backup

```
tmv71 memory write -i backup.dat
```

### Read block 0 from memory

```
tmv71 memory read-block -o data.bin 0
```

### Set port speed using write-block

The PC port speed is stored as a byte at offset 33 (`0x21`) in block 0. The following command will set the PC port speed to 57600 bps:

```
tmv71 memory write-block -d '03' 0 0x21
```

## API Examples

The following examples assume:

```
>>> from tmv71 import api
>>> radio = api.TMV71(port='/dev/ttyUSB0', speed=57600)
```

### Get radio ID

```
>>> radio.radio_id()
['TM-V71']
```

### Get a channel entry

```
>>> import pprint
>>> pprint.pprint(radio.get_channel_entry(0), indent=2)
{ 'channel': 0,
  'ctcss_freq': 146.2,
  'ctcss_status': True,
  'dcs_freq': 23,
  'dcs_status': False,
  'lockout': False,
  'mode': 'FM',
  'offset': 0.6,
  'reverse': False,
  'rx_freq': 145.43,
  'shift': 'DOWN',
  'step': 5,
  'tone_freq': 146.2,
  'tone_status': False,
  'tx_freq': 0.0,
  'tx_step': 5}
```

### Setting a channel entry

```
>>> entry = radio.get_channel_entry(0)
>>> entry['rx_freq'] = 442.25
>>> radio.set_channel_entry(0, entry)
['']
```

### Get the port speed

The get/set port speed methods rely on direct memory access, which means the radio must be in programming mode before we can use them. The `programming_mode` decorating takes care of entering programming mode and exiting it when the command exits.

```
>>> with radio.programming_mode():
...   radio.get_port_speed()
...
'57600'
```

## Contributing

You are welcome to contribute to this project!  Submit [bug reports][], comments, or [pull requests][] to the GitHub project.

[bug reports]: https://github.com/larsks/tm-v71-tools/issues
[pull requests]: https://github.com/larsks/tm-v71-tools/pulls

## Author

Lars Kellogg-Stedman <lars@oddbit.com>, N1LKS

If you're around the Boston area, you can sometimes find me on the [MMRA][] or [BARC][] repeaters.

[MMRA]: https://www.mmra.org/
[BARC]: http://barc.org/

## License

tm-v71-tools - an api and cli for your Kenwood TM-V71  
Copyright (C) 2019 Lars Kellogg-Stedman

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
