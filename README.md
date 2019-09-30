# A CLI and Python API for managing your TM-V71 radio

## Requirements

You will need Python 3.7 (or later), and recent versions of the `setuptools` package (and probably `pip`).

## Installation

You can install this from PyPI using `pip`:

```
pip install tmv71-tools
```

Or you can install it straight from the GitHub repository:

```
pip install git+https://github.com/larsks/tm-v71-tools
```

## Configuration

You can set the `TMV71_PORT` and `TMV71_SPEED` environment variables, or pass the `--port` and `--speed` options to the `tmv71` command.

## Available commands

- [band-mode](#band-mode)
- [channel](#channel)
- [control-band](#control-band)
- [dual-band](#dual-band)
- [entry](#entry)
- [firmware](#firmware)
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

<!-- start command docs -->
### band-mode

```
Usage: tmv71 band-mode [OPTIONS] BAND

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
Usage: tmv71 channel [OPTIONS] [0|1|A|B] [CHANNEL]

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
  --shift ENUM
  --reverse INTEGER
  --tone-status INTEGER
  --ctcss-status INTEGER
  --dcs-status INTEGER
  --tone-freq FLOAT
  --ctcss-freq FLOAT
  --dcs-freq INTEGER
  --offset FLOAT
  --mode ENUM
  --lockout / --no-lockout
  -n, --name TEXT
  --help                    Show this message and exit.
```

### firmware

```
Usage: tmv71 firmware [OPTIONS]

  Return information about the radio firmware.

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
Usage: tmv71 tune [OPTIONS] BAND

Options:
  --rx-freq, --rx FLOAT
  --tx-freq, --tx FLOAT
  --step FLOAT
  --shift ENUM
  --reverse INTEGER
  --tone-status INTEGER
  --ctcss-status INTEGER
  --dcs-status INTEGER
  --tone-freq FLOAT
  --ctcss-freq FLOAT
  --dcs-freq INTEGER
  --offset FLOAT
  --mode ENUM
  --lockout / --no-lockout
  --help                    Show this message and exit.
```

### txpower

```
Usage: tmv71 txpower [OPTIONS] BAND

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

  Export channels to a CSV document.

Options:
  -o, --output FILENAME
  --help                 Show this message and exit.
```

### import-channels

```
Usage: tmv71 import-channels [OPTIONS]

  Import channels from a CSV document.

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

## Examples

### Specifying port and speed on the command line

```
tmv71 --port /dev/ttyS0 --speed 9600 id
```

### Exporting channels to a CSV

```
tmv71 export-channels -o channels.csv
```

### Importing channels from a CSV

```
tmv71 import-channels -i channels.csv
```

### Backing up your radio

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
tmv71 memory write-block -d '03' 0 33
```
