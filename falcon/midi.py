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
