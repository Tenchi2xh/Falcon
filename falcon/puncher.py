# -*- encoding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import midi

from .boxes.box import MusicBox
from .util import *

font = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 64)
font_small = ImageFont.truetype("resources/OpenSans-CondLight.ttf", 36)

margin_left = 75
margin_right = 75
card_width = 1024
beat_height = 100


def draw_labels(draw, box, y0=0):
    """
    :type param box: MusicBox
    """
    x0 = margin_left - (font.getsize(box.labels[0][0])[0] / 2)
    w = (card_width - margin_left - margin_right) / (len(box.labels) - 1.0)
    print x0
    for i, label in enumerate(box.labels):
        elements = label if len(label) == 3 else [label[0], "", label[1]] if len(label) == 2 else [label[0], "", ""]
        x = x0 + i * w
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


def draw_grid(draw, beats, box, y0=0):
    h = beat_height
    l = len(box.notes)
    w = (card_width - margin_left - margin_right) / float(l - 1)
    # Draw vertical lines, first and last thicker
    for i in xrange(l):
        t = 3 if (i == 0 or i == l - 1) else 1
        draw.line([(margin_left + i * w, y0),
                   (margin_left + i * w, y0 + beats * h)], fill="black", width=t)
    y = 0
    # Draw half-beat horizontal lines
    for i in xrange(beats):
        y = y0 + h * i
        draw.line([(margin_left, y + h / 2),
                   (card_width - margin_left, y + h / 2)], fill="black", width=1)
    # Make half-beat lines dashed by drawing thick vertical white lines over
    for i in xrange(l - 1):
        draw.line([(margin_left + i * w + w / 2, y0),
                   (margin_left + i * w + w / 2, y0 + beats * h)], fill="white", width=10)
    # Draw full-beat lines
    for i in xrange(beats + 1):
        y = y0 + h * i
        draw.line([(margin_left, y),
                   (card_width - margin_left, y)], fill="black", width=3)

    return y


def draw_track(draw, track, resolution, box, y0=0):

    offsets = {pitch: i for i, pitch in enumerate(box.notes)}

    h = beat_height
    w = (card_width - margin_left - margin_right) / float(len(box.notes) - 1)
    r = 10
    t = 0

    for event in track:
        t += event.tick
        if event.is_event(midi.events.NoteOnEvent.statusmsg):
            y = h * (t / resolution)
            x = offsets[event.pitch] * w
            draw.ellipse([(margin_left - r + x, y0 + y - r), (margin_left + r + x, y0 + y + r)], fill="black")


def punch(filename, tracks, box):
    """
    :type param box: MusicBox
    """
    im = Image.new("RGB", (card_width, 800 + beats(tracks) * beat_height), "white")
    draw = ImageDraw.Draw(im)

    draw_labels(draw, box, y0=400)
    draw_arrow(draw, y0=100, x0=920, w=48, h=256)
    y1 = draw_grid(draw, beats(tracks), box, y0=600)
    draw_labels(draw, box, y0=y1 - 20)

    for track in tracks:
        draw_track(draw, track, float(tracks.resolution), box, y0=600)

    im.rotate(90, expand=True).save("%s.png" % filename)

