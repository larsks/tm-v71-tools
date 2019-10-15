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

### Configuration file

Tmv71 will read configuration `~/.config/tmv71.json`, if it exists. This file may specify the following configuration keys:

- `port=<device>`
- `speed=<bps>`
- `no_clear=(true|false)`
- `clear_retries=<n>`
- `verbose=<n>`

For example:

```
{
  "port": "/dev/ttyKEYSPAN",
  "speed": 57600,
  "verbose": 1
}
```

### Environment variables

Any command line option can be set from an environment variable named `TMV71_<option>`. For example, you can set the `TMV71_PORT` and `TMV71_SPEED` environment variables instead of passing `--port` and `--speed` on the command line.

For subcommands, you need to include the subcommand name as part of the variable name.  For example, to pass the `--channels 1:10` option to `tmv71 channel export`, you would set:

    TMV71_CHANNEL_EXPORT_CHANNELS=1:10

## Available commands

<!-- start command list -->
- [common options](#common-options)
- [poweron-message](#poweron-message)
- [port-speed](#port-speed)
- [ptt](#ptt)
- [set](#set)
- [send-dtmf](#send-dtmf)
- [band mode](#band-mode)
- [band select](#band-select)
- [band reverse](#band-reverse)
- [band squelch](#band-squelch)
- [band squelch-state](#band-squelch-state)
- [band txpower](#band-select)
- [channel entry](#channel-entry)
- [channel export](#channel-export)
- [channel import](#channel-import)
- [channel tune](#channel-tune)
- [info firmware](#info-firmware)
- [info id](#info-id)
- [info serial](#info-serial)
- [info type](#info-type)
- [memory dump](#memory-dump)
- [memory restore](#memory-restore)
- [memory read-block](#memory-read-block)
- [memory write-block](#memory-write-block)
- [vfo band](#vfo-band)
- [vfo tune](#vfo-tune)
- [raw](#raw)
<!-- end command list -->

<!-- start command docs -->
### common options

```
Usage: tmv71 [OPTIONS] COMMAND [ARGS]...

Options:
  -f, --config-file TEXT          Path to a JSON configuration file  [default:
                                  /home/lars/.config/tmv71.json]
  --no-config                     Do not attempt to read any configuration
                                  file
  -p, --port TEXT                 Path to a serial device
  -s, --speed [9600|19200|38400|57600]
                                  Set the port speed
  -K, --no-clear                  Skip initial clear operation before running
                                  command
  -R, --clear-retries INTEGER     Number of times to retry clear operation
                                  before failing
  -v, --verbose                   Increase verbosity. May be specified
                                  multiple times.
  --help                          Show this message and exit.

Commands:
  band             Commands for controlling the dual bands
  channel          Commands for interacting with memory channels
  info             Commands for getting information about the radio
  lock             Lock or unlock the key lock
  memory           Commands for reading and modifying memory
  op-mode          Control the radio operating mode.
  port-speed       Get or set the PC port speed.
  poweron-message  Get or set the power on message.
  ptt              Activate or deactivate transmitter.
  raw              Send a raw command to the radio and display the response.
  remote-id        Get or set the remote id.
  send-dtmf        Send DTMF tones
  set              Get or set various configuration options.
  version          Print the software version
  vfo              Commands for interacting with the VFO
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

### set

```
Usage: tmv71 set [OPTIONS]

  Get or set various configuration options.

Options:
  --beep / --no-beep
  --beep-volume INTEGER
  --external-speaker-mode INTEGER
  --announce [OFF|AUTO|MANUAL]
  --language [English|Japanese]
  --voice-volume INTEGER
  --voice-speed INTEGER
  --playback-repeat / --no-playback-repeat
  --playback-repeat-interval INTEGER
  --continous-recording / --no-continous-recording
  --vhf-aip / --no-vhf-aip
  --uhf-aip / --no-uhf-aip
  --s-meter-sql-hang-time [OFF|125|250|500]
  --mute-hang-time [OFF|125|250|500|750|1000]
  --beatshift / --no-beatshift
  --timeout-timer INTEGER
  --recall-method [ALL|CURRENT]
  --echolink-speed [FAST|SLOW]
  --dtmf-hold / --no-dtmf-hold
  --dtmf-speed [FAST|SLOW]
  --dtmf-pause [100|250|500|750|1000|1500|2000]
  --dtmf-key-lock / --no-dtmf-key-lock
  --auto-repeater-offset / --no-auto-repeater-offset
  --hold-1750hz / --no-hold-1750hz
  --brightness-level INTEGER
  --auto-brightness / --no-auto-brightness
  --backlight-color [AMBER|GREEN]
  --pf1-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --pf2-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --mic-pf1-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --mic-pf2-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --mic-pf3-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --mic-pf4-key [WX|FREQBAND|CTRL|MONITOR|VGS|VOICE|GROUP_UP|MENU|MUTE|SHIFT|DUAL|MEM_TO_VFO|VFO|MR|CALL|MHZ|TONE|REV|LOW|LOCK|A_B|ENTER|1750HZ]
  --mic-key-lock / --no-mic-key-lock
  --scan-resume [TIME|CARRIER|SEEK]
  --apo [OFF|30|60|90|120|180]
  --ext-data-band [A|B|TXA_RXB|TXB_RXA]
  --ext-data-speed [1200|9600]
  --sqc-source [OFF|BUSY|SQL|TX|BUSY_TX|SQL_TX]
  --auto-pm-store / --no-auto-pm-store
  --display-partition-bar / --no-display-partition-bar
  --reset                         Some options (e.g. brightness-level) require
                                  a reset before they will take effect
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### send-dtmf

```
Usage: tmv71 send-dtmf [OPTIONS] [TONES]...

  Send DTMF tones

Options:
  -w, --wait
  --slow / --fast
  --help           Show this message and exit.
```

### band mode

```
Usage: tmv71 band mode [OPTIONS] [A|B|0|1]

  Set selected band to VFO, MEM, call channel, or weather.

Options:
  --vfo
  --mem, --memory
  --call
  --wx, --weather
  --help           Show this message and exit.
```

### band select

```
Usage: tmv71 band select [OPTIONS] [BAND]

  Select control and ptt band, and select single or dual-band mode

  Use band A as control band and band B as ptt band:

      tmv71 band select A --control     tmv71 band select B --ptt

  Use band B for both control and ptt:

      tmv71 band select B

  Use band B in single band mode:

      tmv71 band select B -1

  Place radio back into dual-band mode:

      tmv71 band select -2

Options:
  -1, --single
  -2, --dual
  -c, --control
  -p, --ptt
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### band reverse

```
Usage: tmv71 band reverse [OPTIONS] [A|B|0|1]

  Activate reverse on the specified band

Options:
  --on / --off
  --help        Show this message and exit.
```

### band squelch

```
Usage: tmv71 band squelch [OPTIONS] [A|B|0|1]

  Get current squelch setting for the specified band.

Options:
  --help  Show this message and exit.
```

### band squelch-state

```
Usage: tmv71 band squelch-state [OPTIONS] [A|B|0|1]

  Report whether squelch is open on the specified band

Options:
  --help  Show this message and exit.
```

### band txpower

```
Usage: tmv71 band txpower [OPTIONS] [A|B|0|1]

  Set tx power for the selected band.

Options:
  --low
  --medium, --med
  --high
  --help           Show this message and exit.
```

### channel entry

```
Usage: tmv71 channel entry [OPTIONS] CHANNEL

  View or edit memory channels.

Options:
  --channel INTEGER
  --rx-freq FLOAT
  --rx-step [5|6.25|28.33|10|12.5|15|20|25|30|50|100]
  --shift [SIMPLEX|UP|DOWN|SPLIT]
  --reverse / --no-reverse
  --tone-status / --no-tone-status
  --ctcss-status / --no-ctcss-status
  --dcs-status / --no-dcs-status
  --tone-freq [67.0|69.3|71.9|74.4|77.0|79.7|82.5|85.4|88.5|91.5|94.8|97.4|100.0|103.5|107.2|110.9|114.8|118.8|123.0|127.3|131.8|136.5|141.3|146.2|151.4|156.7|162.2|167.9|173.8|179.9|186.2|192.8|203.5|240.7|210.7|218.1|225.7|229.1|233.6|241.8|250.3|254.1]
  --ctcss-freq [67.0|69.3|71.9|74.4|77.0|79.7|82.5|85.4|88.5|91.5|94.8|97.4|100.0|103.5|107.2|110.9|114.8|118.8|123.0|127.3|131.8|136.5|141.3|146.2|151.4|156.7|162.2|167.9|173.8|179.9|186.2|192.8|203.5|240.7|210.7|218.1|225.7|229.1|233.6|241.8|250.3|254.1]
  --dcs-code [23|25|26|31|32|36|43|47|51|53|54|65|71|72|73|74|114|115|116|122|125|131|132|134|143|145|152|155|156|162|165|172|174|205|212|223|225|226|243|244|245|246|251|252|255|261|263|265|266|271|274|306|311|315|325|331|332|343|346|351|356|364|365|371|411|412|413|423|431|432|445|446|452|454|455|462|464|465|466|503|506|516|523|565|532|546|565|606|612|624|627|631|632|654|662|664|703|712|723|731|732|734|743|754]
  --offset FLOAT
  --mode [FM|NFM|AM]
  --tx-freq FLOAT
  --tx-step [5|6.25|28.33|10|12.5|15|20|25|30|50|100]
  --lockout / --no-lockout
  -n, --name TEXT
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### channel export

```
Usage: tmv71 channel export [OPTIONS]

  Export channels to a CSV document

Options:
  -o, --output FILENAME
  -c, --channels TEXT    Specify a single chanel (-c 1) or a range of channels
                         (-c 1:10)
  -s, --skip-deleted     Do not export deleted channels
  --help                 Show this message and exit.
```

### channel import

```
Usage: tmv71 channel import [OPTIONS]

  Import channels from a CSV document

Options:
  -i, --input FILENAME
  -s, --sync            Delete channels from the radio that do not exist in
                        input
  -c, --channels TEXT   Specify a single chanel (-c 1) or a range of channels
                        (-c 1:10)
  -I, --ignore-errors   Continue to import channels if there is an error
  --help                Show this message and exit.
```

### channel tune

```
Usage: tmv71 channel tune [OPTIONS] [A|B|0|1] [CHANNEL]

  Get or set the memory channel for the selected band.

Options:
  --help  Show this message and exit.
```

### info firmware

```
Usage: tmv71 info firmware [OPTIONS]

  Return information about the radio firmware.

Options:
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### info id

```
Usage: tmv71 info id [OPTIONS]

  Return the radio model.

Options:
  --help  Show this message and exit.
```

### info serial

```
Usage: tmv71 info serial [OPTIONS]

  Return information about the radio firmware.

Options:
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### info type

```
Usage: tmv71 info type [OPTIONS]

  Return the radio type.

Options:
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
```

### memory dump

```
Usage: tmv71 memory dump [OPTIONS]

  Read entire radio memory and write it to a file.

Options:
  -o, --output FILENAME
  --help                 Show this message and exit.
```

### memory restore

```
Usage: tmv71 memory restore [OPTIONS]

  Read memory dump from a file and write it to the radio.

Options:
  -i, --input FILENAME
  --help                Show this message and exit.
```

### memory read-block

```
Usage: tmv71 memory read-block [OPTIONS] ADDRESS

  Read one or more memory blocks from the radio.

  This command will by default output the binary data to stdout. Use the
  '-o' option to write to a file instead. Use the '--hexdump' option to
  output the data as a formatted hexdump instead.

  You can read a range of addresses by specifying the start and end
  (inclusive) of the range separated by a colon.  E.g., to read addresses
  0x1700 through 0x557f, you could use `tmv71 memory read-block
  0x1700:0x557f`.

  Examples:

  1. Read 16 bytes from address 0x1700, version 1:

     tmv71 memory read-block 0x1700 -l 16 -h

  2. Read 16 bytes from address 0x1700, version 2:

     tmv71 memory read-block 0x1700:0x1710 -h

Options:
  -o, --output FILENAME
  -h, --hexdump
  -l, --length FLEXINT
  --help                 Show this message and exit.
```

### memory write-block

```
Usage: tmv71 memory write-block [OPTIONS] ADDRESS

  Write data to radio memory.

  This command will by default read data from stdin. Use the --input (-i)
  option to read data from a file instead, or --hexdata (-d) to provide
  hexadecimal data on the command line.

  Examples:

  1. Write four bytes to address 0x1700

     tmv71 memory write-block 0x1700 -d 'F0 15 AB 08'

  2. Open 'backup.dat', seek to position 0x1700, read 16 bytes, and    write
  them to address 0x1700:

     tmv71 memory write-block 0x1700 -i backup.dat -s 0x1700 -l 16

Options:
  -i, --input FILENAME
  -d, --hexdata TEXT
  -s, --seek FLEXINT
  -l, --length FLEXINT
  --help                Show this message and exit.
```

### vfo band

```
Usage: tmv71 vfo band [OPTIONS] [A|B|0|1] [[118|144|220|300|430|1200]]

  Get or set the frequency band for the selected radio band.

  Frequency bands are named using the names from "SELECTING A FREQUENCY
  BAND" in the TM-V71 manual. Note that band A and band B support a
  different subset of the available frequencies.

Options:
  --help  Show this message and exit.
```

### vfo tune

```
Usage: tmv71 vfo tune [OPTIONS] [A|B|0|1]

  Get or set VFO frequency and other settings.

  You can only tune to frequencies on the current band. Use the frequency-
  band command to change bands.

Options:
  --rx-freq FLOAT
  --rx-step [5|6.25|28.33|10|12.5|15|20|25|30|50|100]
  --shift [SIMPLEX|UP|DOWN|SPLIT]
  --reverse / --no-reverse
  --tone-status / --no-tone-status
  --ctcss-status / --no-ctcss-status
  --dcs-status / --no-dcs-status
  --tone-freq [67.0|69.3|71.9|74.4|77.0|79.7|82.5|85.4|88.5|91.5|94.8|97.4|100.0|103.5|107.2|110.9|114.8|118.8|123.0|127.3|131.8|136.5|141.3|146.2|151.4|156.7|162.2|167.9|173.8|179.9|186.2|192.8|203.5|240.7|210.7|218.1|225.7|229.1|233.6|241.8|250.3|254.1]
  --ctcss-freq [67.0|69.3|71.9|74.4|77.0|79.7|82.5|85.4|88.5|91.5|94.8|97.4|100.0|103.5|107.2|110.9|114.8|118.8|123.0|127.3|131.8|136.5|141.3|146.2|151.4|156.7|162.2|167.9|173.8|179.9|186.2|192.8|203.5|240.7|210.7|218.1|225.7|229.1|233.6|241.8|250.3|254.1]
  --dcs-code [23|25|26|31|32|36|43|47|51|53|54|65|71|72|73|74|114|115|116|122|125|131|132|134|143|145|152|155|156|162|165|172|174|205|212|223|225|226|243|244|245|246|251|252|255|261|263|265|266|271|274|306|311|315|325|331|332|343|346|351|356|364|365|371|411|412|413|423|431|432|445|446|452|454|455|462|464|465|466|503|506|516|523|565|532|546|565|606|612|624|627|631|632|654|662|664|703|712|723|731|732|734|743|754]
  --offset FLOAT
  --mode [FM|NFM|AM]
  -F, --format [shell|table|json]
  -T, --table-format [fancy_grid|github|grid|html|jira|latex|latex_booktabs|latex_raw|mediawiki|moinmoin|orgtbl|pipe|plain|presto|psql|rst|simple|textile|tsv|youtrack]
  -K, --key TEXT                  Limit output to the specified key (may be
                                  specified multiple times)
  --help                          Show this message and exit.
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
tmv71 channel export -o channels.csv
```

### Import channels from a CSV

```
tmv71 channel import -i channels.csv
```

### Export only channels 1-10

```
tmv71 channel export -o channels.csv -c 1:10
```

### Back up your radio

```
tmv71 memory dump -o backup.dat
```

### Restore from backup

```
tmv71 memory restore -i backup.dat
```

### Read from memory and write binary data to a file

```
tmv71 memory read-block -o data.bin 0
```

### Read from memory and display a hexdump

```
tmv71 memory read-block --hexdump 0
```

### Set port speed using write-block

The PC port speed is stored as a byte at address 33 (`0x21`). The following command will set the PC port speed to 57600 bps:

```
tmv71 memory write-block -d '03' 0x21
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
'TM-V71'

```

### Get a channel entry

```
>>> import pprint
>>> pprint.pprint(radio.get_channel_entry(0), indent=2)
{ 'channel': 0,
  'ctcss_freq': 146.2,
  'ctcss_status': True,
  'dcs_code': 23,
  'dcs_status': False,
  'lockout': False,
  'mode': 'FM',
  'name': 'MRABEL',
  'offset': 0.6,
  'reverse': False,
  'rx_freq': 145.43,
  'shift': 'DOWN',
  'step': 5.0,
  'tone_freq': 67.0,
  'tone_status': False,
  'tx_freq': 0.0,
  'tx_step': 5.0}

```

### Setting a channel entry

```
>>> entry = radio.get_channel_entry(0)
>>> entry['rx_freq'] = 145.43
>>> radio.set_channel_entry(0, entry)
>>>
```

### Get the port speed

The get/set port speed methods rely on direct memory access, which means the radio must be in programming mode before we can use them. The `programming_mode` decorator takes care of entering programming mode and exiting it when the command exits.

```
>>> with radio.programming_mode():
...   radio.get_port_speed()
...
'57600'

```


## Author

Lars Kellogg-Stedman <lars@oddbit.com>, N1LKS

If you're around the Boston area, you can sometimes find me on the [MMRA][] or [BARC][] repeaters.

[MMRA]: https://www.mmra.org/
[BARC]: http://barc.org/

## License

tm-v71-tools - an api and cli for your Kenwood TM-V71  
Copyright (C) 2019 Lars Kellogg-Stedman

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
