import os
import click

from .falcon import falcon
from .punch import punch
from .boxes import boxes



@click.command()
@click.option("-d", "--dpi", type=click.IntRange(min=1), default=300)
@click.option("-b", "--box", type=click.Choice(boxes.keys()), required=True)
@click.option("-s", "--supersampling", type=click.IntRange(min=1), default=2)
@click.option("-v", "--verbose", is_flag=True)
@click.option("--no-midi", is_flag=True)
@click.option("--horizontal/--vertical", default=True)
@click.argument("midi_file", type=click.Path(exists=True))
def cli(dpi, box, supersampling, verbose, no_midi, horizontal, midi_file):
    box = boxes[box]
    basename = os.path.basename(os.path.splitext(midi_file)[0])

    modified_mid = falcon(midi_file=midi_file, box=box, verbose=verbose)
    punch(
        basename=basename,
        mid=modified_mid,
        box=box,
        dpi=dpi,
        supersampling=supersampling,
        angle=90 if horizontal else 0
    )

    if not no_midi:
        modified_mid.save("%s_%s.mid" % (basename, box.symbol))
