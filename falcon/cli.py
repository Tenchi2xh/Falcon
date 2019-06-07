import os
import click

from .falcon import falcon
from .punch import punch
from .boxes import boxes

context_settings = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 120
}

@click.command(context_settings=context_settings)
@click.option("-d", "--dpi", type=click.IntRange(min=1), default=300, metavar="DPI", help="Image resolution in dots per inch (default: 300).")
@click.option("-b", "--box", type=click.Choice(boxes.keys()), required=True, help="Model of the music box.")
@click.option("-s", "--supersampling", type=click.IntRange(min=1), default=2, metavar="SS", help="Supersampling factor (anti-aliasing).")
@click.option("-v", "--verbose", is_flag=True, help="Output progress of all steps.")
@click.option("--no-midi", is_flag=True, help="Don't write a MIDI file output.")
@click.option("--horizontal/--vertical", default=True, help="Rendered punch card orientation.")
@click.argument("midi_file", type=click.Path(exists=True))
def cli(dpi, box, supersampling, verbose, no_midi, horizontal, midi_file):
    """
    Music box punch card generator
    """
    box = boxes[box]
    basename = os.path.basename(os.path.splitext(midi_file)[0])

    modified_mid = falcon(midi_file=midi_file, box=box, verbose=verbose)
    punch(
        basename=basename,
        mid=modified_mid,
        box=box,
        dpi=dpi,
        supersampling=supersampling,
        angle=90 if horizontal else 0,
        verbose=verbose
    )

    if not no_midi:
        modified_mid.save("%s_%s.mid" % (basename, box.symbol))
