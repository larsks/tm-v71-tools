# A CLI and Python API for managing your TM-V71 radio

## Available commands

- `band-mode`
- `channel`
- `control-band`
- `dual-band`
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

## Backing up your radio

```
tmv71 read --port /dev/ttyUSB0 -o backup.dat
```

### Restore from backup

```
tmv71 write --port /dev/ttyUSB0 -i backup.dat
```
