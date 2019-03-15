import os
import mido
import click
from mido import MidiFile

from .boxes import GI15, GI20, GI30
from .midi import length, beats
from .punch import punch


def falcon(midi_file, box, verbose=False):
    echo = click.echo if verbose else lambda x: None

    echo("Reading MIDI file %s" % midi_file)
    mid = MidiFile(midi_file)
    tracks = mid.tracks

    notes_on, notes_off = get_notes(tracks, echo)

    echo("Total of %d notes" % len(notes_on))
    echo("Song is %d beats long" % beats(mid))

    transpose = compute_transpose(notes_on, box, echo)

    for note in notes_on + notes_off:
        closest = box.closest(note.note + transpose)
        note.note = closest

    return mid


def get_notes(tracks, echo):
    notes_on = []
    notes_off = []

    echo("Found %d tracks:" % len(tracks))
    for i, track in enumerate(tracks):
        track_notes_on = [n for n in track if n.type == "note_on"]
        track_notes_off = [n for n in track if n.type == "note_off"]
        echo("- Track #%d: %d notes" % (i, len(track_notes_on)))
        notes_on.extend(track_notes_on)
        notes_off.extend(track_notes_off)

    return notes_on, notes_off


def compute_transpose(notes_on, box, echo):
    all_distances = []

    for key in range(-48, 49):
        pitches = [n.note + key for n in notes_on]
        distances = [box.distance(p) for p in pitches]
        average_distance = sum(distances) / len(pitches)
        all_distances.append((average_distance, key))

    best_distance, transpose = min(all_distances, key=lambda t: t[0])
    echo("Best distance %f with transposition key %d, transposing..." % (best_distance, transpose))
    return transpose
