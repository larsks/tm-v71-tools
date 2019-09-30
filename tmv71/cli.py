import click
import csv
import logging
import os
import sys

from tmv71 import api
from tmv71 import schema

LOG = logging.getLogger(__name__)


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
    '''Send a raw command to the radio and display the response'''

    res = ctx.obj.send_command(command, *args)
    print(*res)


@main.command()
@click.option('-o', '--output', type=click.File('wb'), default=sys.stdout)
@click.pass_context
def read(ctx, output):
    '''Read radio memory and write it to a file'''

    ctx.obj.check_id()
    LOG.info('read from radio to file "%s"', output.name)
    try:
        with output:
            try:
                ctx.obj.read_memory(output)
            except api.CommunicationError as err:
                raise click.ClickException(str(err))
    except Exception:
        if output is not sys.stdout:
            LOG.warning('removing output file %s', output.name)
            os.unlink(output.name)
        raise


@main.command()
@click.option('-i', '--input', type=click.File('rb'), default=sys.stdin)
@click.pass_context
def write(ctx, input):
    '''Read memory dump from a file and write it to the radio'''

    ctx.obj.check_id()
    LOG.info('write to radio from file "%s"', input.name)
    with input:
        try:
            ctx.obj.write_memory(input)
        except api.CommunicationError as err:
            raise click.ClickException(str(err))


@main.command()
@click.argument('block', type=int)
@click.argument('offset', type=int, default=0, required=False)
@click.argument('length', type=int, default=0, required=False)
@click.pass_context
def read_block(ctx, block, offset, length):
    '''Read a memory block from the radio and dump it to stdout'''

    try:
        ctx.obj.enter_programming_mode()
        sys.stdout.buffer.write(ctx.obj.read_block(block, offset, length))
    finally:
        ctx.obj.exit_programming_mode()


@main.command('id')
@click.pass_context
def get_id(ctx):
    '''Return the radio model'''

    res = ctx.obj.radio_id()
    print(res[0])


def fmt_dict(d):
    return '\n'.join('{}={}'.format(k, v) for k, v in d.items())


@main.command('type')
@click.pass_context
def radio_type(ctx):
    '''Return the radio type'''

    res = ctx.obj.radio_type()
    print(fmt_dict(res))


@main.command()
@click.pass_context
def firmware(ctx):
    '''Return information about the radio firmware'''

    res = ctx.obj.radio_firmware()
    print(*res)


@main.command()
@click.argument('message', default=None, required=False)
@click.pass_context
def poweron_message(ctx, message):
    '''Get or set the power on message'''

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
    '''Get or set dual-band mode for the control band'''

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
    if band in ['0', 'A', 0]:
        return 0
    elif band in ['1', 'B', 1]:
        return 1
    else:
        raise ValueError('invalid band number: {}'.format(band))


@main.command()
@click.argument('band', type=click.Choice(['0', '1', 'A', 'B']))
@click.argument('channel', type=int, required=False)
@click.pass_context
def channel(ctx, band, channel):
    '''Get or set the memory channel for the selected band'''

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
    '''Select control and ptt band'''

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
    '''Activate or deactivate transmitter'''

    ctx.obj.set_ptt(ptt_state)


@main.command()
@click.option('--vfo', 'mode', flag_value=api.BAND_MODE.VFO)
@click.option('--mem', '--memory', 'mode', flag_value=api.BAND_MODE.MEM)
@click.option('--call', 'mode', flag_value=api.BAND_MODE.CALL)
@click.option('--wx', '--weather', 'mode', flag_value=api.BAND_MODE.WX)
@click.argument('band')
@click.pass_context
def band_mode(ctx, mode, band):
    '''Set selected band to VFO, MEM, call channel, or weather'''

    band = normalize_band(band)
    if mode is None:
        res = ctx.obj.get_band_mode(band)
    else:
        res = ctx.obj.set_band_mode(band, int(mode))

    print(*res)


@main.command()
@click.option('--low', 'power', flag_value=api.TX_POWER.LOW)
@click.option('--medium', '--med', 'power', flag_value=api.TX_POWER.MED)
@click.option('--high', 'power', flag_value=api.TX_POWER.HIGH)
@click.argument('band')
@click.pass_context
def txpower(ctx, power, band):
    '''Set tx power for the selected band'''

    band = normalize_band(band)
    if power is None:
        res = ctx.obj.get_tx_power(band)
    else:
        res = ctx.obj.set_tx_power(band, int(power))

    print(*res)


class EnumType(click.ParamType):
    name = 'enum'

    def __init__(self, _enum, **kwargs):
        super().__init__(**kwargs)
        self._enum = _enum
        self._fwd = {x.name: x for x in _enum}
        self._rev = {x.value: x for x in _enum}

    def convert(self, value, param, ctx):
        if value in self._fwd:
            return self._fwd[value]
        elif value in self._rev:
            return self._rev[value]
        else:
            raise ValueError(value)


def apply_channel_options(f):
    options = [
        click.option('--rx-freq', '--rx', type=float),
        click.option('--tx-freq', '--tx', type=float),
        click.option('--step', type=float),
        click.option('--shift', type=EnumType(schema.ShiftDirection)),
        click.option('--reverse', type=int),
        click.option('--tone-status', type=int),
        click.option('--ctcss-status', type=int),
        click.option('--dcs-status', type=int),
        click.option('--tone-freq', type=float),
        click.option('--ctcss-freq', type=float),
        click.option('--dcs-freq', type=int),
        click.option('--offset', type=float),
        click.option('--mode', type=EnumType(schema.Mode)),
        click.option('--lockout/--no-lockout', is_flag=True, default=None),
    ]

    for option in reversed(options):
        f = option(f)

    return f


@main.command()
@apply_channel_options
@click.pass_context
@click.argument('band')
def tune(ctx, band, **kwargs):
    print('Not implemented')


@main.command()
@apply_channel_options
@click.option('-n', '--name')
@click.argument('channel', type=int)
@click.pass_context
def entry(ctx, channel, name, **kwargs):
    '''View or edit memory channels'''

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
@click.pass_context
def export_channels(ctx, output):
    with output:
        csvout = csv.writer(output)
        for channel in range(1000):
            LOG.info('getting information for channel %d', channel)

            try:
                channel_config = ctx.obj.get_channel_entry(channel)
                channel_name = ctx.obj.get_channel_name(channel)
                csvout.writerow(schema.ME.to_tuple(channel_config)
                                + [channel_name])
            except api.InvalidCommandError:
                LOG.debug('channel %d does not exist', channel)
                continue


@main.command()
@click.option('-i', '--input', type=click.File('r'), default=sys.stdin)
@click.option('-s', '--sync', is_flag=True)
@click.pass_context
def import_channels(ctx, input, sync):
    with input:
        csvin = csv.reader(input)
        channels = {}
        for row in csvin:
            channels[int(row[0])] = row

        for channel in range(1000):
            if channel not in channels:
                if sync:
                    LOG.info('deleting channel %d', channel)
                    ctx.obj.delete_channel_entry(channel)
            else:
                LOG.info('setting information for channel %d', channel)
                channel_config = schema.ME.from_tuple(channels[channel][:-1])
                channel_name = channels[channel][-1]

                ctx.obj.set_channel_entry(channel, channel_config)
                ctx.obj.set_channel_name(channel, channel_name)
