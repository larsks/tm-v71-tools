import click
import logging
import os
import sys

from tmv71 import device

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-p', '--port', default='/dev/ttyS0')
@click.option('-s', '--speed', default=9600)
@click.option('-v', '--verbose', count=True)
@click.pass_context
def main(ctx, port, speed, verbose):
    try:
        loglevel = ['WARNING', 'INFO', 'DEBUG'][verbose]
    except IndexError:
        loglevel = 'DEBUG'

    logging.basicConfig(level=loglevel)

    ctx.obj = device.TMV71(port, speed=speed)


@main.command()
@click.option('-o', '--output', type=click.File('wb'), default=sys.stdout)
@click.pass_context
def read(ctx, output):
    ctx.obj.check_id()
    LOG.info('read from radio to file "%s"', output.name)
    try:
        with output:
            try:
                ctx.obj.read_memory(output)
            except device.CommunicationError as err:
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
    ctx.obj.check_id()
    LOG.info('write to radio from file "%s"', input.name)
    with input:
        try:
            ctx.obj.write_memory(input)
        except device.CommunicationError as err:
            raise click.ClickException(str(err))
