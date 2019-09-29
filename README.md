## Backing up your radio

```
tmv71 backup --port /dev/ttyUSB0 -o backup.dat
```

### Restore from backup

```
tmv71 write --port /dev/ttyUSB0 -i backup.dat
```
