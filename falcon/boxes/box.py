from typing import List
from dataclasses import dataclass


@dataclass
class MusicBox:
    symbol: str
    name: str
    notes: List[int]
    labels: List[str]

    @property
    def scale(self):
        """
        Set of the base pitches available on the music box
        """
        return set(map(lambda pitch: pitch % 12, self.notes))

    def distance(self, pitch):
        """
        Returns the distance in octaves from the given pitch
        to the closest matching note in the music box
        """
        closest = self.closest(pitch)
        return abs(closest - pitch) / 12.0

    def closest(self, pitch):
        """
        Returns the closest matching note in the music box
        """
        available = [n for n in self.notes if (n % 12) == (pitch % 12)]
        if not available:
            return self.closest(pitch + 1)
        return min(available, key=lambda n: abs(n - pitch))

    def reproducible(self, pitches):
        """
        Returns true if the given list of pitches
        are reproducible with the music box
        """
        return all(pitch % 12 in self.scale for pitch in pitches)
