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

## Available commands

- `band-mode`
- `channel`
- `control-band`
- `dual-band`
- `entry`
- `firmware`
- `id`
- `poweron-message`
- `ptt`
- `raw`
- `read`
- `read-block`
- `tune`
- `txpower`
- `type`
- `write`

<!-- start command docs -->
### band-mode

```
Usage: tmv71 band-mode [OPTIONS] BAND

  Set selected band to VFO, MEM, call channel, or weather

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

  Get or set the memory channel for the selected band

Options:
  --help  Show this message and exit.
```

### control-band

```
Usage: tmv71 control-band [OPTIONS]

  Select control and ptt band

Options:
  -c, --control INTEGER
  -p, --ptt INTEGER
  -b, --both, --cp INTEGER
  --help                    Show this message and exit.
```

### dual-band

```
Usage: tmv71 dual-band [OPTIONS]

  Get or set dual-band mode for the control band

Options:
  -1, --single
  -2, --dual
  --help        Show this message and exit.
```

### entry

```
Usage: tmv71 entry [OPTIONS] CHANNEL

Options:
  --rx-freq, --rx FLOAT
  --tx-freq, --tx FLOAT
  --step FLOAT
  --shift [N|+|-|S]
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
  --help                    Show this message and exit.
```

### firmware

```
Usage: tmv71 firmware [OPTIONS]

  Return information about the radio firmware

Options:
  --help  Show this message and exit.
```

### id

```
Usage: tmv71 id [OPTIONS]

  Return the radio model

Options:
  --help  Show this message and exit.
```

### poweron-message

```
Usage: tmv71 poweron-message [OPTIONS] [MESSAGE]

  Get or set the power on message

Options:
  --help  Show this message and exit.
```

### ptt

```
Usage: tmv71 ptt [OPTIONS]

  Activate or deactivate transmitter

Options:
  --on
  --off
  --help  Show this message and exit.
```

### raw

```
Usage: tmv71 raw [OPTIONS] COMMAND [ARGS]...

  Send a raw command to the radio and display the response

Options:
  --help  Show this message and exit.
```

### read

```
Usage: tmv71 read [OPTIONS]

  Read radio memory and write it to a file

Options:
  -o, --output FILENAME
  --help                 Show this message and exit.
```

### read-block

```
Usage: tmv71 read-block [OPTIONS] BLOCK [OFFSET] [LENGTH]

  Read a memory block from the radio and dump it to stdout

Options:
  --help  Show this message and exit.
```

### tune

```
Usage: tmv71 tune [OPTIONS] BAND

Options:
  --rx-freq, --rx FLOAT
  --tx-freq, --tx FLOAT
  --step FLOAT
  --shift [N|+|-|S]
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
  --help                    Show this message and exit.
```

### txpower

```
Usage: tmv71 txpower [OPTIONS] BAND

  Set tx power for the selected band

Options:
  --low
  --medium, --med
  --high
  --help           Show this message and exit.
```

### type

```
Usage: tmv71 type [OPTIONS]

  Return the radio type

Options:
  --help  Show this message and exit.
```

### write

```
Usage: tmv71 write [OPTIONS]

  Read memory dump from a file and write it to the radio

Options:
  -i, --input FILENAME
  --help                Show this message and exit.
```

<!-- end command docs -->

## Backing up your radio

```
tmv71 read --port /dev/ttyUSB0 -o backup.dat
```

### Restore from backup

```
tmv71 write --port /dev/ttyUSB0 -i backup.dat
```
