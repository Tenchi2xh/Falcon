# -*- encoding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import midi

from .boxes.box import MusicBox
from .util import *


dpi = 300
# 1024 -> 7cm -> 146.286 pixel/cm -> 371.56644 dpi
card_width = int(1024 * (dpi / 371.56644))
ratio = card_width / 1024.


def adjust(n):
    return int(n * ratio)


margin_left = margin_right = adjust(85)
beat_height = adjust(100)
punch_radius = adjust(10)

font = ImageFont.truetype("resources/OpenSans-CondLight.ttf", adjust(64))
font_small = ImageFont.truetype("resources/OpenSans-CondLight.ttf", adjust(36))


def draw_title(draw, basename, box, y0):
    title = "%s.mid" % basename
    subtitle = "Arranged for the %s" % box.name

    size_title = font.getsize(title)
    size_subtitle = font_small.getsize(subtitle)
    x0_title = (card_width - size_title[0]) / 2
    x0_subtitle = (card_width - size_subtitle[0]) / 2

    draw.text((x0_title, y0), title, "black", font)
    draw.text((x0_subtitle, y0 + size_title[1] + adjust(20)), subtitle, "black", font_small)


def draw_labels(draw, box, y0):
    """
    :type param box: MusicBox
    """
    x0 = margin_left - (font.getsize(box.labels[0][0])[0] / 2)
    dy = (adjust(40), adjust(100))
    w = (card_width - margin_left - margin_right) / (len(box.labels) - 1.0)
    for i, label in enumerate(box.labels):
        elements = label if len(label) == 3 else [label[0], "", label[1]] if len(label) == 2 else [label[0], "", ""]
        x = x0 + i * w
        y = dy[0] if (i % 2 == 1 and len(box.labels) > 20) else dy[1]
        draw.text((x, y + y0), elements[0], "black", font)
        letter_width, _ = font.getsize(elements[0])
        draw.text((x + letter_width, y + adjust(30) + y0), elements[2], "black", font_small)
        draw.text((x - adjust(10), y + y0), elements[1], "black", font_small)


def draw_arrow(draw, x0, y0, w, h):
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


def draw_grid(draw, beats, box, y0):
    h = beat_height
    l = len(box.notes)
    w = (card_width - margin_left - margin_right) / float(l - 1)
    y = 0
    # Draw half-beat horizontal lines
    for i in xrange(beats):
        y = y0 + h * i
        draw.line([(margin_left, y + h / 2),
                   (card_width - margin_left, y + h / 2)], fill="black", width=adjust(1))
    # Make half-beat lines dashed by drawing thick vertical white lines over
    for i in xrange(2, l - 1, 3):
        draw.line([(margin_left + i * w + w / 2, y0),
                   (margin_left + i * w + w / 2, y0 + beats * h)], fill="white", width=int(w))
    # Draw vertical lines, first and last thicker
    for i in xrange(l):
        t = 3 if (i == 0 or i == l - 1) else 1
        draw.line([(margin_left + i * w, y0),
                   (margin_left + i * w, y0 + beats * h)], fill="black", width=adjust(t))
    # Draw full-beat lines
    for i in xrange(beats + 1):
        y = y0 + h * i
        size = font_small.getsize(str(i))
        draw.line([(margin_left, y),
                   (card_width - margin_left, y)], fill="black", width=adjust(3))
        # Beat numbers in margin
        draw.text((margin_left - size[0] - adjust(20), y - size[1] / 2 - adjust(8)), str(i), "gray", font_small)
        draw.text((card_width - margin_left + adjust(20), y - size[1] / 2 - adjust(8)), str(i), "gray", font_small)

    return y


def draw_track(draw, track, resolution, box, y0):

    offsets = {pitch: i for i, pitch in enumerate(box.notes)}

    h = beat_height
    w = (card_width - margin_left - margin_right) / float(len(box.notes) - 1)
    r = punch_radius
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
    im = Image.new("RGB", (card_width, adjust(800) + beats(tracks) * beat_height), "white")
    draw = ImageDraw.Draw(im)

    draw_title(draw, filename, box, y0=adjust(250))
    draw_labels(draw, box, y0=adjust(400))
    draw_arrow(draw, y0=adjust(100), x0=adjust(920), w=adjust(48), h=adjust(256))
    y1 = draw_grid(draw, beats(tracks), box, y0=adjust(600))
    draw_labels(draw, box, y0=y1 - adjust(20))

    for track in tracks:
        draw_track(draw, track, float(tracks.resolution), box, y0=adjust(600))

    im.rotate(90, expand=True).save("%s_%s.png" % (filename, box.symbol))

