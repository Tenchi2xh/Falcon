# -*- encoding: utf-8 -*-

from midi.constants import *

from box import MusicBox


class GrandIllusions30Notes(MusicBox):
    """
    http://www.grand-illusions.com/acatalog/30-Note-Music-Box-Set-554.html
    """
    @property
    def name(self):
        return "GI30"

    @property
    def notes(self):
        # Notes reported on punch card
        box = [
            C_0, D_0, G_0, A_0, B_0,
            C_1, D_1, E_1, F_1, Fs_1, G_1, Gs_1, A_1, As_1, B_1,
            C_2, Cs_2, D_2, Ds_2, E_2, F_2, Fs_2, G_2, Gs_2, A_2, As_2, B_2,
            C_3, D_3, E_3
        ]
        # C1 on the music box is actually an F4, so +53
        return list(map(lambda n: n + 53, box))

    @property
    def labels(self):
        return [
            "C", "D", "G", "A", "B",
            "C1", "D1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
            "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
            "C3", "D3", "E3"
        ]


class GrandIllusionsLarge(MusicBox):
    """
    http://www.grand-illusions.com/acatalog/Large_Music_Box_Set.html
    """
    @property
    def name(self):
        return "GI20"

    @property
    def notes(self):
        # Notes reported on punch card
        return [
            C_4, D_4, E_4, F_4, G_4, A_4, B_4,
            C_5, D_5, E_5, F_5, G_5, A_5, B_5,
            C_6, D_6, E_6, F_6, G_6, A_6
        ]

    @property
    def labels(self):
        return (["C", "D", "E", "F", "G", "A", "B"] * 3)[:-1]


class GrandIllusionsSmall(MusicBox):
    """
    http://www.grand-illusions.com/acatalog/Music_Box_Set.html
    """
    @property
    def name(self):
        return "GI15"

    @property
    def notes(self):
        # Notes reported on punch card
        return [
            C_4, D_4, E_4, F_4, G_4, A_4, B_4,
            C_5, D_5, E_5, F_5, G_5, A_5, B_5,
            C_6
        ]

    @property
    def labels(self):
        return (["C", "D", "E", "F", "G", "A", "B"] * 2) + ["C"]
