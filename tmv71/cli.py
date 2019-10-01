import binascii
import click
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


@main.command('id')
@click.pass_context
def get_id(ctx):
    '''Return the radio model.'''

    res = ctx.obj.radio_id()
    print(res[0])


def fmt_dict(d):
    return '\n'.join('{}={}'.format(k, v) for k, v in d.items())


@main.command('type')
@click.pass_context
def radio_type(ctx):
    '''Return the radio type.'''

    res = ctx.obj.radio_type()
    print(fmt_dict(res))


@main.command()
@click.pass_context
def firmware(ctx):
    '''Return information about the radio firmware.'''

    res = ctx.obj.radio_firmware()
    print(*res)


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
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('channel', type=int, required=False)
@click.pass_context
def channel(ctx, band, channel):
    '''Get or set the memory channel for the selected band.'''

    band = normalize_band(band)
    if channel is None:
        res = ctx.obj.get_channel(band)
    else:
        res = ctx.obj.set_channel(band, channel)

    print('{:03d}'.format(int(res[1])))


@main.command()
@click.option('-c', '--control', type=int)
@click.option('-p', '--ptt', type=int)
@click.option('-b', '--both', '--cp', type=int)
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

    print(*res)


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


@main.command()
@click.argument('band', type=click.Choice(BAND_NAMES))
@click.argument('freq_band', type=click.Choice(api.FREQUENCY_BAND))
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
        else:
            ctx.obj.set_frequency_band(band, freq_band)

    print(band)


def apply_channel_options(f):
    options = [
        click.option('--rx-freq', '--rx', type=float),
        click.option('--tx-freq', '--tx', type=float),
        click.option('--step', type=float),
        click.option('--shift', type=click.Choice(schema.SHIFT_DIRECTION)),
        click.option('--reverse', type=int),
        click.option('--tone-status', type=int),
        click.option('--ctcss-status', type=int),
        click.option('--dcs-status', type=int),
        click.option('--tone-freq', type=float),
        click.option('--ctcss-freq', type=float),
        click.option('--dcs-freq', type=int),
        click.option('--offset', type=float),
        click.option('--mode', type=click.Choice(schema.MODE)),
        click.option('--lockout/--no-lockout', is_flag=True, default=None),
    ]

    for option in reversed(options):
        f = option(f)

    return f


@main.command()
@apply_channel_options
@click.pass_context
@click.argument('band', type=click.Choice(BAND_NAMES))
def tune(ctx, band, **kwargs):
    print('Not implemented')


@main.command()
@apply_channel_options
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
        ctx.obj.set_channel_name(channel, name)

    if set_radio:
        res = ctx.obj.set_channel_entry(channel, res)
    else:
        print(fmt_dict(res))


@main.command()
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.option('-c', '--channels', multiple=True)
@click.pass_context
def export_channels(ctx, output, channels):
    '''Export channels to a CSJ document.

    A CSJ document is like a CSV document, but each field is valid JSON.'''

    selected = None
    if channels:
        selected = []
        for channel in channels:
            if ':' in channel:
                ch_start, ch_end = (int(x) for x in channel.split(':'))
                selected.extend(range(ch_start, ch_end + 1))
            else:
                selected.append(int(channel))

    with output:
        output.write(','.join(list(schema.ME.declared_fields) + ['name']))
        output.write('\n')
        for channel in range(1000):
            if selected is not None and channel not in selected:
                continue

            LOG.info('getting information for channel %d', channel)

            try:
                channel_config = ctx.obj.get_channel_entry(channel)
                values = schema.ME.to_raw_tuple(channel_config)
                values.append(ctx.obj.get_channel_name(channel))

                output.write(','.join(json.dumps(x) for x in values))
                output.write('\n')
            except api.InvalidCommandError:
                LOG.debug('channel %d does not exist', channel)
                continue


@main.command()
@click.option('-i', '--input', type=click.File('r'), default=sys.stdin)
@click.option('-s', '--sync', is_flag=True)
@click.pass_context
def import_channels(ctx, input, sync):
    '''Import channels from a CSJ document.

    A CSJ document is like a CSV document, but each field is valid JSON.

    Use --sync to delete channels on the radio that do not exist
    in the input document.'''
    with input:
        channels = {}
        for line in input:
            if line.startswith('channel'):
                continue
            line = line.rstrip()
            values = [json.loads(x) for x in line.split(',')]
            channels[values[0]] = values

        for channel in range(1000):
            if channel not in channels:
                if sync:
                    LOG.info('deleting channel %d', channel)
                    ctx.obj.delete_channel_entry(channel)
            else:
                LOG.info('setting information for channel %d', channel)
                channel_config = schema.ME.from_raw_tuple(channels[channel])
                channel_name = channels[channel][-1]

                ctx.obj.set_channel_entry(channel, channel_config)
                ctx.obj.set_channel_name(channel, channel_name)


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


@main.group()
def memory():
    pass


@memory.command()
@click.option('-o', '--output', type=click.File('wb'),
              default=sys.stdout.buffer)
@click.pass_context
def read(ctx, output):
    '''Read radio memory and write it to a file.'''

    LOG.info('read from radio to file "%s"', output.name)
    try:
        with output, ctx.obj.programming_mode():
            try:
                ctx.obj.read_memory(output)
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
def write(ctx, input):
    '''Read memory dump from a file and write it to the radio.'''

    LOG.info('write to radio from file "%s"', input.name)
    with input, ctx.obj.programming_mode():
        try:
            ctx.obj.write_memory(input)
        except api.CommunicationError as err:
            raise click.ClickException(str(err))


def flexint(v):
    return int(v, 0)


@memory.command()
@click.option('-o', '--output', type=click.File('wb'),
              default=sys.stdout.buffer)
@click.argument('block', type=flexint)
@click.argument('offset', type=flexint, default='0', required=False)
@click.argument('length', type=flexint, default='0', required=False)
@click.pass_context
def read_block(ctx, output, block, offset, length):
    '''Read a memory block from the radio.'''

    LOG.info('reading %d bytes of memory from block %d offset %d',
             256 if length == 0 else length, block, offset)

    with output, ctx.obj.programming_mode():
        output.write(ctx.obj.read_block(block, offset, length))


@memory.command()
@click.option('-i', '--input', type=click.File('rb'))
@click.option('-d', '--hexdata')
@click.argument('block', type=flexint)
@click.argument('offset', type=flexint, default='0', required=False)
@click.argument('length', type=flexint, default='0', required=False)
@click.pass_context
def write_block(ctx, input, hexdata, block, offset, length):
    '''Write data to radio memory'''

    if hexdata:
        data = binascii.unhexlify(hexdata)
    elif input:
        with input:
            data = input.read()
    else:
        raise click.ClickException('No data')

    datalen = len(data)
    if datalen > 256:
        raise ValueError('Data too large')
    elif datalen == 256:
        datalen = 0

    LOG.info('writing %d bytes of data to block %d offset %d',
             256 if datalen == 0 else datalen, block, offset)

    with ctx.obj.programming_mode():
        ctx.obj.write_block(block, offset, data)
