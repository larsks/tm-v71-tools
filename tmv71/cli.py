import click
import csv
import enum
import functools
import hexdump
import json
import logging
import os
import shlex
import sys
import tabulate
import time

from tmv71 import __version__
from tmv71 import api
from tmv71 import schema

TMV71_CONFIG = os.path.expanduser(
    os.path.join(os.environ.get('XDG_CONFIG_HOME', '~/.config'),
                 'tmv71.json')
)

LOG = logging.getLogger(__name__)
BAND_NAMES = ['A', 'B', '0', '1']


class FORMATS(enum.Enum):
    SHELL = 0
    TABLE = 1
    JSON = 2


def fmt_dict(d, format=FORMATS.SHELL, table_format='grid', key=None):
    '''Format a dictionary for output'''

    if isinstance(format, str):
        format = getattr(FORMATS, format.upper())

    if key:
        d = {k: d[k] for k in key}

    if format == FORMATS.SHELL:
        return '\n'.join('{}={}'.format(k, shlex.quote('{}'.format(v)))
                         for k, v in d.items())
    elif format == FORMATS.JSON:
        return json.dumps(d, indent=2)
    elif format == FORMATS.TABLE:
        return tabulate.tabulate(d.items(), tablefmt=table_format)


def formatted(f):
    '''Decoration for commands that produce formatted output.

    Adds formatting options to the command, takes a dictionary
    returned from the command and passes it to fmt_dict for output.'''

    @click.option('--format', '-F',
                  type=click.Choice([x.name.lower() for x in FORMATS]),
                  default=list(FORMATS)[0].name.lower())
    @click.option('--table-format', '-T', default='grid',
                  type=click.Choice(tabulate.tabulate_formats))
    @click.option('--key', '-K', multiple=True,
                  help='Limit output to the specified key (may be '
                  'specified multiple times)')
    @functools.wraps(f)
    def _(format, table_format, key, *args, **kwargs):
        res = f(*args, **kwargs)
        print(fmt_dict(res, format, table_format, key))

    return _


def apply_options_from_schema(model, **kwargs):
    '''Create command line options for fields described in a schema'''

    options = []

    for fname, fspec in model.declared_fields.items():
        display_name = fname.replace('_', '-')
        if fname == 'band':
            pass
        elif isinstance(fspec, schema.RadioBoolean):
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


def clear_first(f):
    '''Clear the communication channel.

    This decorator will use the TMV71.clear() method to attempt to put the
    radio in a known state before running a command.  The top-level option
    --no-clear (-K) will skip this step (or you can set TMV71_NO_CLEAR=1 in
    your environment), and --clear-retries (-R, or TMV71_CLEAR_RETRIES)
    controls how many times it will retry before failing with an error.'''
    @functools.wraps(f)
    def _(ctx, *args, **kwargs):
        if not ctx.settings.no_clear:
            LOG.info('clearing communication channel')
            for i in range(ctx.settings.clear_retries + 1):
                try:
                    ctx.api.clear()
                except api.CommunicationError:
                    LOG.info('no response from the radio (try %d)', i)
                    ctx.api.reopen()
                else:
                    break
            else:
                raise click.ClickException(
                    'failed to communicate with the radio')
        return f(ctx, *args, **kwargs)

    return _


class ApplicationSettings:
    no_clear = False
    clear_retries = 0
    port = '/dev/ttyS0'
    speed = 9600
    verbose = 0


SETTINGS = ApplicationSettings()


class ApplicationContext:
    '''Store settings and global state for the cli'''

    def __init__(self, settings):
        self.settings = settings
        self.init_api()

    def init_api(self):
        self.api = api.TMV71(port=self.settings.port,
                             speed=self.settings.speed,
                             debug=(self.settings.verbose > 2))


def safe_main():
    '''Wrap commands to catch and report expected exceptions'''

    res = 1

    try:
        main()
    except Exception as e:
        if SETTINGS.verbose > 1:
            raise
        else:
            LOG.error('%s', e)
    else:
        res = 0

    sys.exit(res)


@click.group(context_settings=dict(auto_envvar_prefix='TMV71'))
@click.option('-f', '--config-file', default=TMV71_CONFIG, show_default=True,
              help='Path to a JSON configuration file')
@click.option('--no-config', is_flag=True,
              help='Do not attempt to read any configuration file')
@click.option('-p', '--port',
              help='Path to a serial device')
@click.option('-s', '--speed', type=click.Choice(api.PORT_SPEED),
              help='Set the port speed')
@click.option('-K', '--no-clear', is_flag=True, default=None,
              help='Skip initial clear operation before running command')
@click.option('-R', '--clear-retries', type=int,
              help='Number of times to retry clear operation '
              'before failing')
@click.option('-v', '--verbose', count=True,
              help='Increase verbosity. May be specified multiple times.')
@click.pass_context
def main(ctx, config_file, no_config, **kwargs):
    global SETTINGS

    # Override default settings with settings from configuration file
    if not no_config:
        try:
            with open(config_file) as fd:
                conf = json.load(fd)
            LOG.info('loaded configuration from %s', config_file)
            for k, v in conf.items():
                setattr(SETTINGS, k, v)
        except IOError:
            pass

    # Override settings from configuration file with settings from
    # command line
    for k, v in kwargs.items():
        if v is not None:
            setattr(SETTINGS, k, v)

    try:
        loglevel = ['WARNING', 'INFO', 'DEBUG'][SETTINGS.verbose]
    except IndexError:
        loglevel = 'DEBUG'

    logging.basicConfig(level=loglevel)

    ctx.obj = ApplicationContext(SETTINGS)


@main.command()
def version():
    '''Print the software version'''
    print('{}'.format(__version__))


@main.command()
@click.argument('message', default=None, required=False)
@click.pass_obj
@clear_first
def poweron_message(ctx, message):
    '''Get or set the power on message.'''

    if message is None:
        res = ctx.api.get_poweron_message()
    else:
        res = ctx.api.set_poweron_message(message)

    print(res[0])


def normalize_band(band):
    '''Turns a band name into a numeric 0 or 1'''

    if band in ['0', 'A']:
        return 0
    elif band in ['1', 'B']:
        return 1
    else:
        raise ValueError('invalid band number: {}'.format(band))


@main.command()
@click.option('--on', 'ptt_state', flag_value=True)
@click.option('--off', 'ptt_state', flag_value=False, default=False)
@click.pass_obj
@clear_first
def ptt(ctx, ptt_state):
    '''Activate or deactivate transmitter.'''

    ctx.api.set_ptt(ptt_state)


@main.command()
@click.option('--lock/--unlock', 'lock_state', default=None)
@click.pass_obj
@clear_first
def lock(ctx, lock_state):
    '''Lock or unlock the key lock'''

    if lock_state is None:
        res = ctx.api.get_lock_state()
    else:
        res = ctx.api.set_lock_state(lock_state)

    print(*res)


@main.command()
@click.option('-w', '--wait', is_flag=True)
@click.option('--slow/--fast', 'fast')
@click.argument('tones', nargs=-1)
@click.pass_obj
@clear_first
def send_dtmf(ctx, wait, fast, tones):
    '''Send DTMF tones'''

    tones = ''.join(tones).replace(' ', '')
    if wait:
        LOG.info('waiting until channel is free')
        band_state = ctx.api.get_ptt_ctrl()
        ptt = band_state['ptt']
        LOG.debug('current ptt band is %s', ptt)
        while ctx.api.get_band_squelch_state(ptt) == 1:
            LOG.debug('waiting until band %s is not busy', ptt)
            time.sleep(0.5)

    with ctx.api.ptt():
        ctx.api.send_dtmf(tones, fast)

# ----------------------------------------------------------------------


@main.group()
def band():
    '''Commands for controlling the dual bands'''
    pass


@band.command('squelch')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_obj
@clear_first
def band_squelch(ctx, band):
    '''Get current squelch setting for the specified band.'''

    band = normalize_band(band)
    res = ctx.api.get_band_squelch(band)
    print(res)


@band.command('squelch-state')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_obj
@clear_first
def band_squelch_state(ctx, band):
    '''Report whether squelch is open on the specified band'''

    band = normalize_band(band)
    res = ctx.api.get_band_squelch_state(band)
    print(res)


@band.command('reverse')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.option('--on/--off', 'reverse', default=None)
@click.pass_obj
@clear_first
def band_reverse(ctx, band, reverse):
    '''Activate reverse on the specified band'''

    band = normalize_band(band)
    if reverse is None:
        res = ctx.api.get_band_reverse(band)
    else:
        reverse = 1 if reverse else 0
        res = ctx.api.set_band_reverse(band, reverse)

    print(res)


@band.command('mode')
@click.option('--vfo', 'mode',
              flag_value=schema.BAND_MODE.index('VFO'))
@click.option('--mem', '--memory', 'mode',
              flag_value=schema.BAND_MODE.index('MEM'))
@click.option('--call', 'mode',
              flag_value=schema.BAND_MODE.index('CALL'))
@click.option('--wx', '--weather', 'mode',
              flag_value=schema.BAND_MODE.index('WX'))
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_obj
@clear_first
def band_mode(ctx, mode, band):
    '''Set selected band to VFO, MEM, call channel, or weather.'''

    band = normalize_band(band)
    if mode is None:
        res = ctx.api.get_band_mode(band)
    else:
        res = ctx.api.set_band_mode(band, int(mode))

    print(schema.BAND_MODE[res])


@band.command('select')
@click.option('-1', '--single', 'mode', flag_value=1)
@click.option('-2', '--dual', 'mode', flag_value=2)
@click.option('-c', '--control', 'which', flag_value='control')
@click.option('-p', '--ptt', 'which', flag_value='ptt')
@click.argument('band', required=False)
@formatted
@click.pass_obj
@clear_first
def band_select(ctx, band, which, mode):
    '''Select control and ptt band, and select single or dual-band mode

    Use band A as control band and band B as ptt band:

        tmv71 band select A --control
        tmv71 band select B --ptt

    Use band B for both control and ptt:

        tmv71 band select B

    Use band B in single band mode:

        tmv71 band select B -1

    Place radio back into dual-band mode:

        tmv71 band select -2
    '''

    if which and mode:
        raise click.ClickException('-1/-2 and -c/-p are mutually exclusive')

    cur_state = ctx.api.get_ptt_ctrl()
    cur_mode = ctx.api.get_dual_band_mode()

    if mode == 2:
        cur_mode = ctx.api.set_dual_band_mode()
    elif band is not None:
        band = normalize_band(band)

        if mode:
            if mode == 1:
                cur_state['ctrl_band'] = cur_state['ptt'] = band
                cur_mode = ctx.api.set_single_band_mode()
        else:
            if which == 'control':
                cur_state['ctrl_band'] = band
            elif which == 'ptt':
                cur_state['ptt'] = band
            else:
                cur_state['ctrl'] = cur_state['ptt'] = band

        cur_state = ctx.api.set_ptt_ctrl(**cur_state)

    return dict(mode=['dual', 'single'][cur_mode], **cur_state)


@band.command()
@click.option('--low', 'power', flag_value=schema.TX_POWER.index('LOW'))
@click.option('--medium', '--med', 'power',
              flag_value=schema.TX_POWER.index('MED'))
@click.option('--high', 'power',
              flag_value=schema.TX_POWER.index('HIGH'))
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.pass_obj
@clear_first
def txpower(ctx, power, band):
    '''Set tx power for the selected band.'''

    band = normalize_band(band)
    if power is None:
        res = ctx.api.get_tx_power(band)
    else:
        res = ctx.api.set_tx_power(band, int(power))

    print(schema.TX_POWER[res])


def resolve_range(rspec, default=None):
    '''Resolves a range specification into a list of numbers.

    A range specification is a list of numbers and ranges, where a range
    is specified as lower_bound:upper_bound. Given a range specification
    of the form:

        [1, 3, 5, 7:10, 18:20]

    The return value would be:

        [1, 3, 5, 7, 8, 9, 10, 18, 19, 20]

    This method is used by the channel import and export commands.
    '''

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
@click.pass_obj
@clear_first
def port_speed(ctx, speed):
    '''Get or set the PC port speed.

    Note that because this command involves reading from/writing to
    memory directly, it will briefly reset the radio.

    Valid port speeds are 9600, 19200, 38400, and 57600.'''

    with ctx.api.programming_mode():
        if speed is None:
            LOG.info('getting port speed')
            speed = ctx.api.get_port_speed()
        else:
            LOG.info('setting port speed to %d bps', speed)
            ctx.api.set_port_speed(speed)

    print(speed)


@main.command('set')
@apply_options_from_schema(schema.MU)
@click.option('--reset', is_flag=True,
              help='Some options (e.g. brightness-level) require '
              'a reset before they will take effect')
@formatted
@click.pass_obj
@clear_first
def radio_set(ctx, reset, **kwargs):
    '''Get or set various configuration options.'''
    res = ctx.api.get_radio_config()

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if set_radio:
        LOG.info('configuring radio')
        res = ctx.api.set_radio_config(res)

    if reset:
        with ctx.api.programming_mode():
            pass

    return res


@main.command()
@click.option('--wireless/--no-wireless', default=None)
@click.option('--repeater/--no-repeater', default=None)
@click.option('--normal', is_flag=True, default=None)
@click.pass_obj
@clear_first
def op_mode(ctx, wireless, repeater, normal):
    '''Control the radio operating mode.

    Use this to activate the cross-band repeater feature (--repeater),
    the wireless remote control (--wireless), or both. Use --normal to
    return to normal operation.
    '''
    with ctx.api.programming_mode():
        for opt in [wireless, repeater, normal]:
            if opt is not None:
                break
        else:
            print(*ctx.api.get_operating_mode())
            return

        if normal:
            repeater = 0
            wireless = 0

        ctx.api.set_operating_mode(repeater, wireless)


@main.command()
@click.argument('remote_id', required=False)
@click.pass_obj
@clear_first
def remote_id(ctx, remote_id):
    '''Get or set the remote id.

    This is the access code require to control the radio in wireless
    remote mode.'''

    with ctx.api.programming_mode():
        if remote_id is None:
            res = ctx.api.get_remote_id()
            print(res.decode('ascii'))
        else:
            ctx.api.set_remote_id(remote_id.encode('ascii'))

# ----------------------------------------------------------------------


@main.group()
def channel():
    '''Commands for interacting with memory channels'''
    pass


@channel.command('tune')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('channel', type=int, required=False)
@click.pass_obj
@clear_first
def channel_tune(ctx, band, channel):
    '''Get or set the memory channel for the selected band.'''

    band = normalize_band(band)
    if channel is None:
        res = ctx.api.get_channel(band)
    else:
        res = ctx.api.set_channel(band, channel)

    print('{:03d}'.format(res))


@channel.command()
@apply_options_from_schema(schema.ME)
@click.option('-n', '--name')
@click.argument('channel', type=int)
@formatted
@click.pass_obj
@clear_first
def entry(ctx, channel, name, **kwargs):
    '''View or edit memory channels.'''

    res = ctx.api.get_channel_entry(channel)

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if name is not None:
        LOG.info('setting name for channel %s',  channel)
        ctx.api.set_channel_name(channel, name)

    if set_radio:
        LOG.info('configuring channel %s',  channel)
        res = ctx.api.set_channel_entry(channel, res)
        res = ctx.api.get_channel_entry(channel)

    return res


@channel.command('export')
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.option('-c', '--channels', multiple=True,
              help='Specify a single chanel (-c 1) or '
              'a range of channels (-c 1:10)')
@click.option('-s', '--skip-deleted', is_flag=True,
              help='Do not export deleted channels')
@click.pass_obj
@clear_first
def export_channels(ctx, output, channels, skip_deleted):
    '''Export channels to a CSV document'''

    selected = resolve_range(channels, range(1000))
    fields = schema.ME.export_fields

    with output:
        output.write(','.join(list(fields)))
        output.write('\n')
        writer = csv.DictWriter(output, fields)
        for channel in selected:
            LOG.info('getting information for channel %d', channel)

            try:
                channel_config = ctx.api.get_channel_entry(channel)

                # csv.DictWriter complains about unknown fields
                channel_config = {k: channel_config[k] for k in fields}

                writer.writerow(channel_config)
            except api.InvalidCommandError:
                LOG.debug('channel %d does not exist', channel)
                if not skip_deleted:
                    writer.writerow({'channel': channel})


@channel.command('import')
@click.option('-i', '--input', type=click.File('r'), default=sys.stdin)
@click.option('-s', '--sync', is_flag=True,
              help='Delete channels from the radio '
              'that do not exist in input')
@click.option('-c', '--channels', multiple=True,
              help='Specify a single chanel (-c 1) or '
              'a range of channels (-c 1:10)')
@click.option('--continue', '_continue', is_flag=True,
              help='Continue to import channels if there is an error')
@click.pass_obj
@clear_first
def import_channels(ctx, input, sync, channels, _continue):
    '''Import channels from a CSV document'''

    selected = resolve_range(channels, range(1000))
    fields = schema.ME.export_fields

    with input:
        reader = csv.DictReader(input, fields)
        channelmap = {}
        for row in reader:
            # skip the header row
            if row['channel'] == 'channel':
                continue

            # a deleted channel has no rx_freq
            if not row['rx_freq']:
                continue

            channelmap[int(row['channel'])] = row

        for channel in selected:
            if channel not in channelmap:
                if sync:
                    LOG.info('deleting channel %d', channel)
                    ctx.api.delete_channel_entry(channel)
            else:
                LOG.info('setting information for channel %d', channel)
                try:
                    ctx.api.set_channel_entry(channel, channelmap[channel])
                except api.InvalidCommandError:
                    if _continue:
                        LOG.warning('Unable to set channel %d', channel)
                    else:
                        raise


@channel.command('delete')
@click.option('-c', '--channels', multiple=True,
              help='Specify a single chanel (-c 1) or '
              'a range of channels (-c 1:10)')
@click.pass_obj
@clear_first
def delete_channels(ctx, channels):
    '''Delete a channel or range of channels'''

    selected = resolve_range(channels, [])

    for channel in selected:
        LOG.info('deleting channel %d', channel)
        ctx.api.delete_channel_entry(channel)


# ----------------------------------------------------------------------


@main.group()
def info():
    '''Commands for getting information about the radio'''
    pass


@info.command('id')
@click.pass_obj
@clear_first
def radio_id(ctx):
    '''Return the radio model.'''

    res = ctx.api.radio_id()
    print(res)


@info.command('type')
@formatted
@click.pass_obj
@clear_first
def radio_type(ctx):
    '''Return the radio type.'''

    res = ctx.api.radio_type()
    return res


@info.command()
@formatted
@click.pass_obj
@clear_first
def firmware(ctx):
    '''Return information about the radio firmware.'''

    res = ctx.api.radio_firmware()
    return res


@info.command()
@formatted
@click.pass_obj
@clear_first
def serial(ctx):
    '''Return information about the radio firmware.'''

    return ctx.api.radio_serial()

# ----------------------------------------------------------------------


@main.group()
def vfo():
    '''Commands for interacting with the VFO'''
    pass


@vfo.command()
@apply_options_from_schema(schema.FO)
@click.argument('band', type=click.Choice(BAND_NAMES))
@formatted
@click.pass_obj
@clear_first
def tune(ctx, band, **kwargs):
    '''Get or set VFO frequency and other settings.

    You can only tune to frequencies on the current band. Use the
    frequency-band command to change bands.'''

    band = normalize_band(band)
    res = ctx.api.get_band_mode(band)
    if res != 0:
        raise click.ClickException('selected band must be in VFO mode')

    res = ctx.api.get_band_vfo(band)

    set_radio = False
    for k, v in kwargs.items():
        if v is None:
            continue

        set_radio = True
        res[k] = v

    if set_radio:
        LOG.info('setting vfo for band %s', band)
        res = ctx.api.set_band_vfo(band, res)

    return res


@vfo.command('band')
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('freq_band', type=click.Choice(api.FREQUENCY_BAND),
                required=False)
@click.pass_obj
@clear_first
def frequency_band(ctx, band, freq_band):
    '''Get or set the frequency band for the selected radio band.

    Frequency bands are named using the names from "SELECTING A FREQUENCY BAND"
    in the TM-V71 manual. Note that band A and band B support a different
    subset of the available frequencies.'''

    band = normalize_band(band)
    with ctx.api.programming_mode():
        if freq_band is None:
            freq_band = ctx.api.get_frequency_band(band)
            pass
        else:
            ctx.api.set_frequency_band(band, freq_band)

    print(freq_band)

# ----------------------------------------------------------------------


@main.group()
def memory():
    '''Commands for reading and modifying memory'''
    pass


@memory.command()
@click.option('-o', '--output', type=click.File('wb'),
              default=sys.stdout.buffer)
@click.pass_obj
@clear_first
def dump(ctx, output):
    '''Read entire radio memory and write it to a file.'''

    LOG.info('read from radio to file "%s"', output.name)
    try:
        with output, ctx.api.programming_mode():
            try:
                ctx.api.memory_dump(output)
            except api.CommunicationError as err:
                raise click.ClickException(str(err))
    except Exception:
        if output is not sys.stdout.buffer:
            LOG.warning('removing output file %s', output.name)
            os.unlink(output.name)
        raise


@memory.command()
@click.option('-i', '--input', type=click.File('rb'), default=sys.stdin)
@click.pass_obj
@clear_first
def restore(ctx, input):
    '''Read memory dump from a file and write it to the radio.'''

    LOG.info('write to radio from file "%s"', input.name)
    with input, ctx.api.programming_mode():
        try:
            ctx.api.memory_restore(input)
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
@click.pass_obj
@clear_first
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

    with output, ctx.api.programming_mode():
        addr = addr_start
        while addr < addr_end:
            chunklen = min(256, addr_end - addr)

            # The special value '0' means '256 bytes'
            chunklen = 0 if chunklen == 256 else chunklen

            LOG.info('reading %d bytes of memory from 0x%04X',
                     256 if chunklen == 0 else chunklen, addr)
            data = ctx.api.read_block(addr, chunklen)

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
@click.pass_obj
@clear_first
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

    with ctx.api.programming_mode():
        addr = address
        for chunk in hexdump.chunks(data, 256):
            chunklen = len(chunk)
            LOG.info('writing %d bytes of data to address 0x%04X',
                     256 if chunklen == 0 else chunklen, addr)

            addr += 256
            ctx.api.write_block(address, chunk)

# ----------------------------------------------------------------------


@main.command()
@click.argument('command')
@click.argument('args', nargs=-1)
@click.pass_obj
@clear_first
def raw(ctx, command, args):
    '''Send a raw command to the radio and display the response.'''

    res = ctx.api.send_command(command, *args)
    print(*res)
