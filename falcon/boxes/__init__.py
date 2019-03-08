from .box import MusicBox

NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]

for n in range(128):
    octave = n // 12
    name = NOTE_NAMES[n % 12]
    globals()["%s_%d" % (name, octave)] = n


GrandIllusions30Notes = MusicBox(
    symbol="GI30",
    name="Grand Illusions 30 Notes Music Box",
    notes=[n + 53 for n in [  # C1 on the music box is actually an F4, so we add 53
        C_0, D_0, G_0, A_0, B_0,
        C_1, D_1, E_1, F_1, Fs_1, G_1, Gs_1, A_1, As_1, B_1,
        C_2, Cs_2, D_2, Ds_2, E_2, F_2, Fs_2, G_2, Gs_2, A_2, As_2, B_2,
        C_3, D_3, E_3
    ]],
    labels=[
        "C", "D", "G", "A", "B",
        "C1", "D1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
        "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
        "C3", "D3", "E3"
    ]
)

GrandIllusionsLarge = MusicBox(
    symbol="GI20",
    name="Grand Illusions Large Music Box",
    notes=[
        C_4, D_4, E_4, F_4, G_4, A_4, B_4,
        C_5, D_5, E_5, F_5, G_5, A_5, B_5,
        C_6, D_6, E_6, F_6, G_6, A_6
    ],
    labels=(["C", "D", "E", "F", "G", "A", "B"] * 3)[:-1]
)

GrandIllusionsSmall = MusicBox(
    symbol="GI15",
    name="Grand Illusions Music Box",
    notes=[
        C_4, D_4, E_4, F_4, G_4, A_4, B_4,
        C_5, D_5, E_5, F_5, G_5, A_5, B_5,
        C_6
    ],
    labels=(["C", "D", "E", "F", "G", "A", "B"] * 2) + ["C"]
)
