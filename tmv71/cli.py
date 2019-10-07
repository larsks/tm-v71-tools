import click
import hexdump
import json
import logging
import os
import sys

from tmv71 import api
from tmv71 import schema

LOG = logging.getLogger(__name__)
BAND_NAMES = ['0', 'A', '1', 'B']


@click.group(context_settings=dict(auto_envvar_prefix='TMV71'))
@click.option('-p', '--port', default='/dev/ttyS0')
@click.option('-s', '--speed', default=9600)
@click.option('-v', '--verbose', count=True)
@click.option('-K', '--no-clear', is_flag=True)
@click.pass_context
def main(ctx, port, speed, verbose, no_clear):
    try:
        loglevel = ['WARNING', 'INFO', 'DEBUG'][verbose]
    except IndexError:
        loglevel = 'DEBUG'

    logging.basicConfig(level=loglevel)

    ctx.obj = api.TMV71(port, speed=speed, debug=(verbose > 2))

    if not no_clear:
        LOG.info('clearing communication channel')
        ctx.obj.clear()


@main.command()
@click.argument('command')
@click.argument('args', nargs=-1)
@click.pass_context
def raw(ctx, command, args):
    '''Send a raw command to the radio and display the response.'''

    res = ctx.obj.send_command(command, *args)
    print(*res)


def fmt_dict(d):
    return '\n'.join('{}={}'.format(k, v) for k, v in d.items())


@main.command()
@click.argument('message', default=None, required=False)
@click.pass_context
def poweron_message(ctx, message):
    '''Get or set the power on message.'''

    if message is None:
        res = ctx.obj.get_poweron_message()
    else:
        res = ctx.obj.set_poweron_message(message)

    print(res[0])


@main.command()
@click.option('-1', '--single', 'mode', flag_value=1)
@click.option('-2', '--dual', 'mode', flag_value=2)
@click.pass_context
def dual_band(ctx, mode):
    '''Get or set dual-band mode for the control band.'''

    if mode is None:
        res = ctx.obj.get_dual_band_mode()
    elif mode == 1:
        res = ctx.obj.set_single_band_mode()
    elif mode == 2:
        res = ctx.obj.set_dual_band_mode()
    else:
        raise click.ClickException('mode must be 1 or 2')

    print(['dual', 'single'][int(res[0])])


def normalize_band(band):
    if band in ['0', 'A']:
        return 0
    elif band in ['1', 'B']:
        return 1
    else:
        raise ValueError('invalid band number: {}'.format(band))


@main.command()
@click.option('-c', '--control')
@click.option('-p', '--ptt')
@click.option('-b', '--both', '--cp')
@click.pass_context
def control_band(ctx, control, ptt, both):
    '''Select control and ptt band.'''

    res = ctx.obj.get_ptt_ctrl_band()

    if both is not None:
        control = ptt = both

    if control is None and ptt is None:
        print(*res)
        return

    if control is not None:
        control = normalize_band(control)
        res[0] = control

    if ptt is not None:
        ptt = normalize_band(ptt)
        res[1] = ptt

    res = ctx.obj.set_ptt_ctrl_band(*res)
    print(*res)


@main.command()
@click.option('--on', 'ptt_state', flag_value=True)
@click.option('--off', 'ptt_state', flag_value=False, default=False)
@click.pass_context
def ptt(ctx, ptt_state):
    '''Activate or deactivate transmitter.'''

    ctx.obj.set_ptt(ptt_state)


@main.command()
@click.option('--vfo', 'mode',
              flag_value=schema.BAND_MODE.index('VFO'))
@click.option('--mem', '--memory', 'mode',
              flag_value=schema.BAND_MODE.index('MEM'))
@click.option('--call', 'mode',
              flag_value=schema.BAND_MODE.index('CALL'))
@click.option('--wx', '--weather', 'mode',
              flag_value=schema.BAND_MODE.index('WX'))
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_context
def band_mode(ctx, mode, band):
    '''Set selected band to VFO, MEM, call channel, or weather.'''

    band = normalize_band(band)
    if mode is None:
        res = ctx.obj.get_band_mode(band)
    else:
        res = ctx.obj.set_band_mode(band, int(mode))

    print(schema.BAND_MODE[int(res[1])])


@main.command()
@click.option('--low', 'power', flag_value=schema.TX_POWER.index('LOW'))
@click.option('--medium', '--med', 'power',
              flag_value=schema.TX_POWER.index('MED'))
@click.option('--high', 'power',
              flag_value=schema.TX_POWER.index('HIGH'))
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_context
def txpower(ctx, power, band):
    '''Set tx power for the selected band.'''

    band = normalize_band(band)
    if power is None:
        res = ctx.obj.get_tx_power(band)
    else:
        res = ctx.obj.set_tx_power(band, int(power))

    print(*res)


def apply_options_from_schema(model, **kwargs):
    options = []

    for fname, fspec in model.declared_fields.items():
        display_name = fname.replace('_', '-')
        if isinstance(fspec, schema.RadioBoolean):
            options.append(
                click.option('--{0}/--no-{0}'.format(display_name),
                             default=None,
                             **kwargs.get(fname, {})))
        elif isinstance(fspec, schema.Indexed):
            values = [str(v) for v in fspec.values]
            options.append(click.option('--{}'.format(display_name),
                                        type=click.Choice(values),
                                        **kwargs.get(fname, {})))
        elif isinstance(fspec, schema.FormattedInteger):
            options.append(click.option('--{}'.format(display_name),
                                        type=int,
                                        **kwargs.get(fname, {})))
        elif isinstance(fspec, schema.RadioFloat):
            options.append(click.option('--{}'.format(display_name),
                                        type=float,
                                        **kwargs.get(fname, {})))

    def _apply_options(f):
        for option in reversed(options):
            f = option(f)

        return f

    return _apply_options


def resolve_range(rspec, default=None):
    selected = default
    if rspec:
        selected = []
        for entry in rspec:
            if ':' in entry:
                r_start, r_end = (int(x) for x in entry.split(':'))
                selected.extend(range(r_start, r_end + 1))
            else:
                selected.append(int(entry))

    return selected


@main.command()
@click.argument('speed', type=click.Choice(api.PORT_SPEED), required=False)
@click.pass_context
def port_speed(ctx, speed):
    '''Get or set the PC port speed.

    Note that because this command involves reading from/writing to
    memory directly, it will briefly reset the radio.

    Valid port speeds are 9600, 19200, 38400, and 57600.'''

    with ctx.obj.programming_mode():
        if speed is None:
            LOG.info('getting port speed')
            speed = ctx.obj.get_port_speed()
        else:
            LOG.info('setting port speed to %d bps', speed)
            ctx.obj.set_port_speed(speed)

    print(speed)


@main.command('set')
@apply_options_from_schema(schema.MU)
@click.option('--reset', is_flag=True,
              help='Some options (e.g. brightness-level) require '
              'a reset before they will take effect')
@click.pass_context
def radio_set(ctx, reset, **kwargs):
    '''Get or set various configuration options.'''
    res = ctx.obj.get_radio_config()

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if set_radio:
        LOG.info('configuring radio')
        res = ctx.obj.set_radio_config(res)

    if reset:
        with ctx.obj.programming_mode():
            pass

    print(fmt_dict(res))


@main.command()
@click.option('--wireless/--no-wireless', default=None)
@click.option('--repeater/--no-repeater', default=None)
@click.option('--normal', is_flag=True, default=None)
@click.pass_context
def op_mode(ctx, wireless, repeater, normal):
    '''Control the radio operating mode.

    Use this to activate the cross-band repeater feature (--repeater),
    the wireless remote control (--wireless), or both. Use --normal to
    return to normal operation.
    '''
    with ctx.obj.programming_mode():
        for opt in [wireless, repeater, normal]:
            if opt is not None:
                break
        else:
            print(*ctx.obj.get_operating_mode())
            return

        if normal:
            repeater = 0
            wireless = 0

        ctx.obj.set_operating_mode(repeater, wireless)


@main.command()
@click.argument('remote_id', required=False)
@click.pass_context
def remote_id(ctx, remote_id):
    '''Get or set the remote id.

    This is the access code require to control the radio in wireless
    remote mode.'''

    with ctx.obj.programming_mode():
        if remote_id is None:
            res = ctx.obj.get_remote_id()
            print(res.decode('ascii'))
        else:
            ctx.obj.set_remote_id(remote_id.encode('ascii'))

# ----------------------------------------------------------------------


@main.group()
def channel():
    '''Commands for interacting with memory channels'''
    pass


@channel.command('tune')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('channel', type=int, required=False)
@click.pass_context
def channel_tune(ctx, band, channel):
    '''Get or set the memory channel for the selected band.'''

    band = normalize_band(band)
    if channel is None:
        res = ctx.obj.get_channel(band)
    else:
        res = ctx.obj.set_channel(band, channel)

    print('{:03d}'.format(int(res[1])))


@channel.command()
@apply_options_from_schema(schema.ME)
@click.option('-n', '--name')
@click.argument('channel', type=int)
@click.pass_context
def entry(ctx, channel, name, **kwargs):
    '''View or edit memory channels.'''

    res = ctx.obj.get_channel_entry(channel)

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if name is not None:
        LOG.info('setting name for channel %s',  channel)
        ctx.obj.set_channel_name(channel, name)

    if set_radio:
        LOG.info('configuring channel %s',  channel)
        res = ctx.obj.set_channel_entry(channel, res)
        res = ctx.obj.get_channel_entry(channel)

    print(fmt_dict(res))


@channel.command('export')
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.option('-c', '--channels', multiple=True)
@click.pass_context
def export_channels(ctx, output, channels):
    '''Export channels to a CSJ document.

    A CSJ document is like a CSV document, but each field is valid JSON.'''

    selected = resolve_range(channels, range(1000))

    with output:
        output.write(','.join(list(schema.ME.declared_fields) + ['name']))
        output.write('\n')
        for channel in selected:
            LOG.info('getting information for channel %d', channel)

            try:
                channel_config = ctx.obj.get_channel_entry(channel)
                values = channel_config.schema.to_raw_tuple(channel_config)
                values.append(ctx.obj.get_channel_name(channel))

                output.write(','.join(json.dumps(x) for x in values))
                output.write('\n')
            except api.InvalidCommandError:
                LOG.debug('channel %d does not exist', channel)
                continue


@channel.command('import')
@click.option('-i', '--input', type=click.File('r'), default=sys.stdin)
@click.option('-s', '--sync', is_flag=True)
@click.option('-c', '--channels', multiple=True)
@click.pass_context
def import_channels(ctx, input, sync, channels):
    '''Import channels from a CSJ document.

    A CSJ document is like a CSV document, but each field is valid JSON.

    Use --sync to delete channels on the radio that do not exist
    in the input document.'''
    selected = resolve_range(channels, range(1000))

    with input:
        channelmap = {}
        for line in input:
            if line.startswith('channel'):
                continue
            line = line.rstrip()
            values = [json.loads(x) for x in line.split(',')]
            channelmap[values[0]] = values

        for channel in selected:
            if channel not in channelmap:
                if sync:
                    LOG.info('deleting channel %d', channel)
                    ctx.obj.delete_channel_entry(channel)
            else:
                LOG.info('setting information for channel %d', channel)
                channel_config = schema.ME.from_raw_tuple(channelmap[channel])
                channel_name = channelmap[channel][-1]

                ctx.obj.set_channel_entry(channel, channel_config)
                ctx.obj.set_channel_name(channel, channel_name)

# ----------------------------------------------------------------------


@main.group()
def info():
    '''Commands for getting information about the radio'''
    pass


@info.command('id')
@click.pass_context
def radio_id(ctx):
    '''Return the radio model.'''

    res = ctx.obj.radio_id()
    print(res[0])


@info.command('type')
@click.pass_context
def radio_type(ctx):
    '''Return the radio type.'''

    res = ctx.obj.radio_type()
    print(fmt_dict(res))


@info.command()
@click.pass_context
def firmware(ctx):
    '''Return information about the radio firmware.'''

    res = ctx.obj.radio_firmware()
    print(*res)

# ----------------------------------------------------------------------


@main.group()
def vfo():
    '''Commands for interacting with the VFO'''
    pass


@vfo.command()
@apply_options_from_schema(schema.FO)
@click.argument('band', type=click.Choice(schema.BANDS))
@click.pass_context
def tune(ctx, band, **kwargs):
    '''Get or set VFO frequency and other settings.

    You can only tune to frequencies on the current band. Use the
    frequency-band command to change bands.'''

    res = ctx.obj.get_band_vfo(band)

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if set_radio:
        LOG.info('setting vfo for band %s', band)
        res = ctx.obj.set_band_vfo(band, res)

    print(fmt_dict(res))


@vfo.command('band')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('freq_band', type=click.Choice(api.FREQUENCY_BAND),
                required=False)
@click.pass_context
def frequency_band(ctx, band, freq_band):
    '''Get or set the frequency band for the selected radio band.

    Frequency bands are named using the names from "SELECTING A FREQUENCY BAND"
    in the TM-V71 manual. Note that band A and band B support a different
    subset of the available frequencies.'''

    band = normalize_band(band)
    with ctx.obj.programming_mode():
        if freq_band is None:
            freq_band = ctx.obj.get_frequency_band(band)
            pass
        else:
            ctx.obj.set_frequency_band(band, freq_band)

    print(freq_band)

# ----------------------------------------------------------------------


@main.group()
def memory():
    '''Commands for reading and modifying memory'''
    pass


@memory.command()
@click.option('-o', '--output', type=click.File('wb'),
              default=sys.stdout.buffer)
@click.pass_context
def dump(ctx, output):
    '''Read entire radio memory and write it to a file.'''

    LOG.info('read from radio to file "%s"', output.name)
    try:
        with output, ctx.obj.programming_mode():
            try:
                ctx.obj.memory_dump(output)
            except api.CommunicationError as err:
                raise click.ClickException(str(err))
    except Exception:
        if output is not sys.stdout.buffer:
            LOG.warning('removing output file %s', output.name)
            os.unlink(output.name)
        raise


@memory.command()
@click.option('-i', '--input', type=click.File('rb'), default=sys.stdin)
@click.pass_context
def restore(ctx, input):
    '''Read memory dump from a file and write it to the radio.'''

    LOG.info('write to radio from file "%s"', input.name)
    with input, ctx.obj.programming_mode():
        try:
            ctx.obj.memory_restore(input)
        except api.CommunicationError as err:
            raise click.ClickException(str(err))


def flexint(v):
    '''Convert strings to integer values.

    The block read/write commands accept integer values as either
    decimal or hexadecimal. This function converts either format into
    integer values.'''

    if isinstance(v, int):
        return v
    else:
        return int(v, 0)


@memory.command()
@click.option('-o', '--output', type=click.File('wb'),
              default=sys.stdout.buffer)
@click.option('-h', '--hexdump', '_hexdump', is_flag=True)
@click.option('-l', '--length', type=flexint, default=0)
@click.argument('address')
@click.pass_context
def read_block(ctx, output, _hexdump, address, length):
    '''Read one or more memory blocks from the radio.

    This command will by default output the binary data to stdout. Use the
    '-o' option to write to a file instead. Use the '--hexdump' option
    to output the data as a formatted hexdump instead.

    You can read a range of addresses by specifying the start and end
    (inclusive) of the range separated by a colon.  E.g., to read addresses
    0x1700 through 0x557f, you could use `tmv71 memory read-block
    0x1700:0x557f`.

    Examples:

    1. Read 16 bytes from address 0x1700, version 1:

       tmv71 memory read-block 0x1700 -l 16 -h

    2. Read 16 bytes from address 0x1700, version 2:

       tmv71 memory read-block 0x1700:0x1710 -h
    '''

    if ':' in address and length != 0:
        raise ValueError('you cannot specify a length '
                         'when using an address range')
    elif ':' in address:
        addr_start, addr_end = (flexint(x) for x in address.split(':'))
    else:
        addr_start = flexint(address)
        addr_end = addr_start + (length if length else 256)

    with output, ctx.obj.programming_mode():
        addr = addr_start
        while addr < addr_end:
            chunklen = min(256, addr_end - addr)

            # The special value '0' means '256 bytes'
            chunklen = 0 if chunklen == 256 else chunklen

            LOG.info('reading %d bytes of memory from 0x%04X',
                     256 if chunklen == 0 else chunklen, addr)
            data = ctx.obj.read_block(addr, chunklen)

            if _hexdump:
                output.write(
                    hexdump.hexdump(data, result='return').encode('ascii'))
                output.write(b'\n')
            else:
                output.write(data)

            addr = min(addr_end, addr + 256)


@memory.command()
@click.option('-i', '--input', type=click.File('rb'))
@click.option('-d', '--hexdata')
@click.option('-s', '--seek', type=flexint, default=0)
@click.option('-l', '--length', type=flexint)
@click.argument('address', type=flexint)
@click.pass_context
def write_block(ctx, input, hexdata, seek, length, address):
    '''Write data to radio memory.

    This command will by default read data from stdin. Use the --input (-i)
    option to read data from a file instead, or --hexdata (-d) to provide
    hexadecimal data on the command line.

    Examples:

    1. Write four bytes to address 0x1700

       tmv71 memory write-block 0x1700 -d 'F0 15 AB 08'

    2. Open 'backup.dat', seek to position 0x1700, read 16 bytes, and
       write them to address 0x1700:

       tmv71 memory write-block 0x1700 -i backup.dat -s 0x1700 -l 16
    '''

    LOG.debug('seek %d length %d address %d', seek, length, address)

    if input:
        LOG.debug('reading data from %s', input.name)
        with input:
            input.seek(seek)
            data = input.read(length)
    elif hexdata:
        LOG.debug('reading data from hexdata option')
        data = hexdump.dehex(hexdata)
        if seek:
            data = data[seek:]
        if length:
            data = data[:length]
    elif sys.stdin.buffer.seekable():
        LOG.debug('reading data from stdin (seekable)')
        sys.stdin.buffer.seek(seek)
        data = sys.stdin.buffer.read(length)
    else:
        LOG.debug('reading data from stdin (not seekable)')
        data = sys.stdin.buffer.read()[seek:]
        if length:
            data = data[:length]

    with ctx.obj.programming_mode():
        addr = address
        for chunk in hexdump.chunks(data, 256):
            chunklen = len(chunk)
            LOG.info('writing %d bytes of data to address 0x%04X',
                     256 if chunklen == 0 else chunklen, addr)

            addr += 256
            ctx.obj.write_block(address, chunk)
