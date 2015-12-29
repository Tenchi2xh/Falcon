# -*- encoding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import midi

from .boxes.box import MusicBox
from .util import *

font = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 64)
font_small = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 36)


def draw_labels(draw, box, y0=0):
    """
    :type param box: MusicBox
    """
    for i, label in enumerate(box.labels):
        elements = label if len(label) == 3 else [label[0], "", label[1]] if len(label) == 2 else [label[0], "", ""]
        x = 60 + i * 30
        y = 40 if (i % 2 == 1) else 100
        draw.text((x, y + y0), elements[0], "black", font)
        letter_width, _ = font.getsize(elements[0])
        draw.text((x + letter_width, y + 30 + y0), elements[2], "black", font_small)
        draw.text((x - 10, y + y0), elements[1], "black", font_small)


def draw_arrow(draw, x0=0, y0=0, w=100, h=400):
    points = map(lambda xy: (xy[0] + x0, xy[1] + y0), [
        (w / 2, 0),
        (w, 0.2 * h),
        (w * 0.8, 0.2 * h),
        (w * 0.8, h),
        (w * 0.2, h),
        (w * 0.2, 0.2 * h),
        (0, 0.2 * h)
    ])

    draw.polygon(points, fill="black")

beat_height = 100


def draw_grid(draw, beats, box, y0=0):
    h = beat_height
    l = len(box.notes)
    w = (1024 - 150) / float(l - 1)
    for i in xrange(l):
        t = 3 if (i == 0 or i == l - 1) else 1
        draw.line([(75 + i * w, y0), (75 + i * w, y0 + beats * h)], fill="black", width=t)
    y = 0

    for i in xrange(beats):
        y = y0 + h * i
        draw.line([(75, y + h / 2), (1024 - 75, y + h / 2)], fill="black", width=1)
    for i in xrange(l - 1):
        draw.line([(75 + i * w + w / 2, y0), (75 + i * w + w / 2, y0 + beats * h)], fill="white", width=10)

    for i in xrange(beats + 1):
        y = y0 + h * i
        draw.line([(75, y), (1024 - 75, y)], fill="black", width=3)

    return y


def draw_track(draw, track, resolution, box, y0=0):

    offsets = {pitch: i for i, pitch in enumerate(box.notes)}

    h = beat_height
    w = (1024 - 150) / float(len(box.notes) - 1)
    r = 10
    t = 0

    for event in track:
        t += event.tick
        if event.is_event(midi.events.NoteOnEvent.statusmsg):
            y = h * (t / resolution)
            x = offsets[event.pitch] * w
            draw.ellipse([(75 - r + x, y0 + y - r), (75 + r + x, y0 + y + r)], fill="black")


def punch(filename, tracks, box):
    """
    :type param box: MusicBox
    """
    im = Image.new("RGB", (1024, 800 + beats(tracks) * beat_height), "white")
    draw = ImageDraw.Draw(im)

    draw_labels(draw, box, y0=400)
    draw_arrow(draw, y0=100, x0=920, w=48, h=256)
    y1 = draw_grid(draw, beats(tracks), box, y0=600)
    draw_labels(draw, box, y0=y1 - 20)

    for track in tracks:
        draw_track(draw, track, float(tracks.resolution), box, y0=600)

    im.rotate(90, expand=True).save("%s.png" % filename)

