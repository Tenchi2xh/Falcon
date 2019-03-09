import click

from .falcon import falcon
from .punch import punch
from .boxes import GI30


@click.command()
def cli():
    falcon("./legacy/to_good_friends_music_box.mid", GI30)
