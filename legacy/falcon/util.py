# -*- encoding: utf-8 -*-


def length(tracks):
    """
    Return the length of a MIDI file's tracks in ticks
    """
    max_t = 0
    for track in tracks:
        t = 0
        for event in track:
            t += event.tick
        if t > max_t:
            max_t = t
    return max_t


def beats(tracks):
    """
    Return the length of a MIDI file's tracks in beats
    """
    return int(length(tracks) / tracks.resolution)
