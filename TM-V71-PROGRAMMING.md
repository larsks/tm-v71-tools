## Enter programming mode

```
>>> 0M <space> PROGRAM <cr>
<<< 0M <cr>
```

You will see `PROG MCP` on the display, but if your code does not interact with the radio, the display will change to `PROG ERR`. You can still successfully read and write memory, but additional bits will be set in the response code to memory commands.

## Status response

In programming mode, the radio will acknowledge commands with a one byte status code.
This code does not* indicate that the command was unsuccessful; it simply acknowledges the command and provides information about the state of the radio.

### Successful response

If everything is successful, the radio will response with `0b00000110` (aka `0x06`). 

### Error response

If the radio is in an error state (e.g. because you took too long to interact with it), the radio will response with `0b00001111` (aka 0x0f).

## Exit programming mode

```
>>> E
<<< <status> <cr> <0x00>
```

## Read memory

```
>>> R <block> <offset> <len>
<<< W <block> <offset> <len> <data>
>>> 0x06
<<< <status>

## Write memory

```
>>> W <block> <offset> <len> <data...>
<<< <status>
```
