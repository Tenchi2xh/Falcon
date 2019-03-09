import types
import pkg_resources
from PIL import Image, ImageDraw, ImageFont

from .midi import beats

dimensions = {
    "card": {
        "width": 70
    },
    "margins": {
        "header": 40,
        "footer": 24,
        "left": 5.5,
        "right": 6
    },
    "grid": {
        "beat": 8,
        "pitch": 2
    },
    "offsets": {
        "top_to_title": 15,
        "title_to_subtitle": 8,
        "lower_pitch_row_to_grid": 1,
        "upper_pitch_row_to_grid": 6,
        "right_to_arrow": 3,
        "top_to_arrow_base": 30,
    },
    "arrow": {
        "stem_width": 2,
        "stem_height": 15,
        "tip_offset": 1,
        "tip_height": 5,
    }
}


def punch(basename, mid, box, dpi):
    ctx = types.SimpleNamespace()
    # ctx.dimensions = box.dimensions
    ctx.dimensions = dimensions
    ctx.box = box

    def c(mm):
        """milimeters -> pixels"""
        return int((mm * dpi) / 25.4)

    def cd(*args, d=dimensions):
        """dimensions -> pixels"""
        return cd(*args[1:], d=d[args[0]]) if len(args) > 1 else c(d[args[0]])

    ctx.c = c
    ctx.cd = cd

    ctx.image = Image.new(
        mode="RGB",
        size=(
            cd("card", "width"),
            cd("margins", "header") + beats(mid) * cd("grid", "beat")
        ),
        color="white"
    )
    ctx.draw = ImageDraw.Draw(ctx.image)

    ctx.font = ImageFont.truetype(pkg_resources.resource_filename(__name__, "OpenSans-CondLight.ttf"), c(5))
    ctx.font_small = ImageFont.truetype(pkg_resources.resource_filename(__name__, "OpenSans-CondLight.ttf"), c(2))

    draw_title(ctx, title=basename)  # TODO: Find a title in midi metadata
    draw_labels(ctx)
    draw_arrow(ctx)

    (ctx.image
        #.rotate(90, expand=True)
        .save("%s_%s.png" % (basename, box.symbol), dpi=(dpi, dpi))
    )


def draw_title(ctx, title):
    title = "%s.mid" % title
    subtitle = "Arranged for the %s" % ctx.box.name

    size_title = ctx.font.getsize(title)
    size_subtitle = ctx.font_small.getsize(subtitle)

    x_title = (ctx.cd("card", "width") - size_title[0]) / 2
    x_subtitle = (ctx.cd("card", "width") - size_subtitle[0]) / 2
    y_title = ctx.cd("offsets", "top_to_title")
    y_subtitle = y_title + ctx.cd("offsets", "title_to_subtitle")

    ctx.draw.text((x_title, y_title), title, "black", ctx.font)
    ctx.draw.text((x_subtitle, y_subtitle), subtitle, "black", ctx.font_small)


def draw_labels(ctx):
    x0 = ctx.cd("margins", "left")
    dx = ctx.cd("grid", "pitch")
    dy0 = ctx.cd("offsets", "lower_pitch_row_to_grid")
    dy1 = ctx.cd("offsets", "upper_pitch_row_to_grid")
    fh = ctx.font.getsize("A")[1]
    y0 = ctx.cd("margins", "header")

    for i, label in enumerate(ctx.box.labels):
        elements = label if len(label) == 3 else [label[0], "", label[1]] if len(label) == 2 else [label[0], "", ""]

        x = x0 + i * dx - (ctx.font.getsize(elements[0])[0] / 2)
        dy = dy0 if (i % 2 == 0 and len(ctx.box.labels) > 20) else dy1  # FIXME: have flag in box for 1 or 2 rows
        y = y0 - dy - fh

        ctx.draw.text((x, y), elements[0], "black", ctx.font)

        letter_width = ctx.font.getsize(elements[0])[0]
        ctx.draw.text((x + letter_width, y + ctx.c(3.5)), elements[2], "black", ctx.font_small)
        ctx.draw.text((x - ctx.c(0.5), y), elements[1], "black", ctx.font_small)


def draw_arrow(ctx):
    sh = ctx.cd("arrow", "stem_height")
    sw = ctx.cd("arrow", "stem_width")
    to = ctx.cd("arrow", "tip_offset")
    th = ctx.cd("arrow", "tip_height")

    # offsets from the right side
    x0 = ctx.cd("card", "width") - ctx.cd("offsets", "right_to_arrow")
    y0 = ctx.cd("offsets", "top_to_arrow_base")

    # order of coordinates:
    #    |      4
    #    |     / \
    #    |    /   \
    #    y   5-6 2-3
    #    0     | |         |
    #    |     | |         |
    #    v     7_1  <-x0-> |

    points = list(map(lambda xy: (xy[0] + x0, xy[1] + y0), [
        (0, 0),               # 1
        (0, -sh),             # 2
        (to, -sh),            # 3
        (-sw / 2, -sh - th),  # 4
        (-sw - to, -sh),      # 5
        (-sw, -sh),           # 6
        (-sw, 0)              # 7
    ]))

    ctx.draw.polygon(points, fill="black")
