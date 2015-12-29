# -*- encoding: utf-8 -*-

import midi
from midi.constants import *

from util import *
from puncher import punch
from boxes import *

basename = "lullaby"
box = grand_illusion_30_notes


def main(midi_file="%s.mid" % basename):
    print "Reading MIDI file %s" % midi_file
    tracks = midi.read_midifile(midi_file)
    print "Found %d tracks:" % len(tracks)

    all_notes_on = []
    all_notes_off = []
    for i, track in enumerate(tracks):
        notes_on = filter(lambda note: note.is_event(midi.events.NoteOnEvent.statusmsg), track)
        notes_off = filter(lambda note: note.is_event(midi.events.NoteOffEvent.statusmsg), track)
        print "- Track #%d: %d notes" % (i, len(notes_on))
        all_notes_on.extend(notes_on)
        all_notes_off.extend(notes_off)

    print "Total of %d notes" % len(all_notes_on)
    print "Song is %d beats long" % beats(tracks)

    transpose = 0
    best_distance = 1000

    for key in xrange(-48, 49):
        pitches = map(lambda note: note.pitch + key, all_notes_on)
        distances = map(box.distance, pitches)
        average_distance = sum(distances) / len(pitches)
        if average_distance < best_distance:
            best_distance = average_distance
            transpose = key

    print "Best distance %f with transpose key %d, transposing" % (best_distance, transpose)
    for note in all_notes_on + all_notes_off:
        closest = box.closest(note.pitch + transpose)
        note.set_pitch(closest)

    midi.write_midifile("%s_transposed.mid" % basename, tracks)

    punch(basename, tracks, box)
