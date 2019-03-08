import os
import mido
import click
from mido import MidiFile

from .boxes import GI15, GI20, GI30
from .midi import length, beats


# TODO:
# - separate in functions
# - add a debug param


def falcon(midi_file_path):
    box = GI30  # FIXME
    basename = os.path.basename(os.path.splitext(midi_file_path)[0])

    click.echo("Reading MIDI file %s" % midi_file_path)
    mid = MidiFile(midi_file_path)
    tracks = mid.tracks
    click.echo("Found %d tracks:" % len(tracks))

    all_notes_on = []
    all_notes_off = []

    for i, track in enumerate(tracks):
        notes_on = [n for n in track if n.type == "note_on"]
        notes_off = [n for n in track if n.type == "note_off"]
        click.echo("- Track #%d: %d notes" % (i, len(notes_on)))
        all_notes_on.extend(notes_on)
        all_notes_off.extend(notes_off)

    click.echo("Total of %d notes" % len(all_notes_on))
    click.echo("Song is %d beats long" % beats(mid))

    all_distances = []

    for key in range(-48, 49):
        pitches = [n.note + key for n in all_notes_on]
        distances = [box.distance(p) for p in pitches]
        average_distance = sum(distances) / len(pitches)
        all_distances.append((average_distance, key))

    best_distance, transpose = min(all_distances, key=lambda t: t[0])

    click.echo("Best distance %f with transposition key %d, transposing..." % (best_distance, transpose))
    for note in all_notes_on + all_notes_off:
        closest = box.closest(note.note + transpose)
        note.note = closest

    mid.save("%s_%s.mid" % (basename, box.symbol))
