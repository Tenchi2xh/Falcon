import click
from typing import Any, List, Tuple
from mido import MidiFile, MetaMessage as Note  # type: ignore

from .boxes.box import MusicBox
from .midi import beats


def falcon(midi_file: str, box: MusicBox, verbose=False) -> MidiFile:
    echo: Any = click.echo if verbose else lambda x: None  # type: ignore

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


def get_notes(tracks: List[List[Note]], echo) -> Tuple[List[Note], List[Note]]:
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


def compute_transpose(notes_on: List[Note], box: MusicBox, echo) -> int:
    all_distances = []

    for key in range(-48, 49):
        pitches = [n.note + key for n in notes_on]
        distances = [box.distance(p) for p in pitches]
        average_distance = sum(distances) / len(pitches)
        all_distances.append((average_distance, key))

    best_distance, transpose = min(all_distances, key=lambda t: t[0])
    echo(
        "Best distance %f with transposition key %d, transposing..."
        % (best_distance, transpose)
    )
    return transpose
