from typing import List, Tuple
from mido import MetaMessage as Note  # type: ignore


def length(mid) -> int:
    """
    Return the length of a MIDI file's tracks in ticks
    """
    return max(sum(msg.time for msg in track) for track in mid.tracks)


def beats(mid) -> int:
    """
    Return the length of a MIDI file's tracks in beats
    """
    return int(length(mid) / mid.ticks_per_beat)


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
