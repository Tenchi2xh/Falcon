# -*- encoding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import midi
from midi.constants import *

labels = [
    ("C", "", ""),
    ("D", "", ""),
    ("G", "", ""),
    ("A", "", ""),
    ("B", "", ""),
    ("C", "", "1"),
    ("D", "", "1"),
    ("E", "", "1"),
    ("F", "", "1"),
    ("F", "#", "1"),
    ("G", "", "1"),
    ("G", "#", "1"),
    ("A", "", "1"),
    ("A", "#", "1"),
    ("B", "", "1"),
    ("C", "", "2"),
    ("C", "#", "2"),
    ("D", "", "2"),
    ("D", "#", "2"),
    ("E", "", "2"),
    ("F", "", "2"),
    ("F", "#", "2"),
    ("G", "", "2"),
    ("G", "#", "2"),
    ("A", "", "2"),
    ("A", "#", "2"),
    ("B", "", "2"),
    ("C", "", "3"),
    ("D", "", "3"),
    ("E", "", "3")
]

# Notes reported on punch card
box = [
    C_0, D_0, G_0, A_0, B_0,
    C_1, D_1, E_1, F_1, Fs_1, G_1, Gs_1, A_1, As_1, B_1,
    C_2, Cs_2, D_2, Ds_2, E_2, F_2, Fs_2, G_2, Gs_2, A_2, As_2, B_2,
    C_3, D_3, E_3
]
# C1 on the music box is an F4
box = map(lambda n: n + 53, box)
offsets = {pitch: i for i, pitch in enumerate(box)}

print box

font = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 64)
font_small = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 36)


def draw_labels(draw, y0=0):
    for i, label in enumerate(labels):
        x = 60 + i * 30
        y = 40 if (i % 2 == 1) else 100
        draw.text((x, y + y0), label[0], "black", font)
        letter_width, _ = font.getsize(label[0])
        draw.text((x + letter_width, y + 30 + y0), label[2], "black", font_small)
        draw.text((x - 10, y + y0), label[1], "black", font_small)


def draw_arrow(draw, x0=0, y0=0, w=100, h=400):
    points = map(lambda xy: (xy[0] + x0, xy[1] + y0),
                 [(w / 2, 0), (w, 0.2 * h), (w * 0.8, 0.2 * h), (w * 0.8, h), (w * 0.2, h), (w * 0.2, 0.2 * h), (0, 0.2 * h)]
                 )
    draw.polygon(points, fill="black")

beat_height = 100


def draw_grid(draw, beats, y0=0):
    h = beat_height
    w = (1024 - 150) / 29.
    for i in xrange(30):
        t = 3 if (i == 0 or i == 29) else 1
        draw.line([(75 + i * w, y0), (75 + i * w, y0 + beats * h)], fill="black", width=t)
    y = 0

    for i in xrange(beats):
        y = y0 + h * i
        draw.line([(75, y + h / 2), (1024 - 75, y + h / 2)], fill="black", width=1)
    for i in xrange(29):
        draw.line([(75 + i * w + w / 2, y0), (75 + i * w + w / 2, y0 + beats * h)], fill="white", width=10)

    for i in xrange(beats + 1):
        y = y0 + h * i
        draw.line([(75, y), (1024 - 75, y)], fill="black", width=3)

    return y


def draw_track(draw, track, resolution, y0=0):
    h = beat_height
    w = (1024 - 150) / 29.
    r = 10
    t = 0

    for event in track:
        t += event.tick
        if event.is_event(midi.events.NoteOnEvent.statusmsg):
            y = h * (t / resolution)
            x = offsets[event.pitch] * w
            draw.ellipse([(75 - r + x, y0 + y - r), (75 + r + x, y0 + y + r)], fill="black")


def punch(filename, tracks, length, resolution):
    beats = int(length / resolution)

    im = Image.new("RGB", (1024, 800 + beats * beat_height), "white")
    draw = ImageDraw.Draw(im)

    draw_labels(draw, y0=400)
    draw_arrow(draw, y0=100, x0=920, w=48, h=256)
    y1 = draw_grid(draw, beats, y0=600)
    draw_labels(draw, y0=y1 - 20)

    for track in tracks:
        draw_track(draw, track, float(resolution), y0=600)

    im.rotate(90, expand=True).save("%s.png" % filename)

