# -*- encoding: utf-8 -*-

import midi
from midi.constants import *

from puncher import punch

# Notes reported on punch card
box = [
    C_0, D_0, G_0, A_0, B_0,
    C_1, D_1, E_1, F_1, Fs_1, G_1, Gs_1, A_1, As_1, B_1,
    C_2, Cs_2, D_2, Ds_2, E_2, F_2, Fs_2, G_2, Gs_2, A_2, As_2, B_2,
    C_3, D_3, E_3
]
# C1 on the music box is an F4
box = map(lambda n: n + 53, box)
scale = set(map(lambda pitch: pitch % 12, box))


# Distance in octave to closest available on box
def distance_to_box(pitch):
    closest = closest_to_box(pitch)
    return abs(closest - pitch) / 12.0


def closest_to_box(pitch):
    available = filter(lambda n: (n % 12) == (pitch % 12), box)
    return min(available, key=lambda n: abs(n - pitch))


def reproducible(pitches):
    return all(pitch % 12 in scale for pitch in pitches)


def length(tracks):
    max_t = 0
    for track in tracks:
        t = 0
        for event in track:
            t += event.tick
        if t > max_t:
            max_t = t
    return max_t

basename = "secret"


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

    transpose = 0
    best_distance = 1000

    for key in xrange(-48, 49):
        pitches = map(lambda note: note.pitch + key, all_notes_on)
        distances = map(distance_to_box, pitches)
        average_distance = sum(distances) / len(pitches)
        if average_distance < best_distance:
            best_distance = average_distance
            transpose = key

    print "Best distance %f with transpose key %d" % (best_distance, transpose)
    print "Transposing..."

    for note in all_notes_on + all_notes_off:
        closest = closest_to_box(note.pitch + transpose)
        note.set_pitch(closest)

    midi.write_midifile("%s_transposed.mid" % basename, tracks)
    print tracks

    l = length(tracks)
    beats = l / tracks.resolution
    if beats > 75:
        print "Song too long for punching on only one card (%d beats)" % beats
    else:
        print "Song has %d beats, fits on one card" % beats
    punch(basename, tracks, length(tracks), tracks.resolution)
