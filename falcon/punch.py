import click
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
        "left": 6,
        "right": 6
    },
    "grid": {
        "beat": 8,
        "pitch": 2,
        "hole": 2
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


def punch(basename, mid, box, dpi, supersampling=2, angle=90, verbose=False):
    echo = click.echo if verbose else lambda x: None

    original_dpi = dpi
    dpi *= supersampling
    ctx = types.SimpleNamespace()
    # FIXME: ctx.dimensions = box.dimensions
    ctx.dimensions = dimensions
    ctx.box = box

    def c(mm):
        """milimeters -> pixels"""
        return (mm * dpi) / 25.4

    def cd(*args, d=dimensions):
        """dimensions -> pixels"""
        return cd(*args[1:], d=d[args[0]]) if len(args) > 1 else c(d[args[0]])

    ctx.c = c
    ctx.cd = cd

    ctx.image = Image.new(
        mode="RGB",
        size=(
            int(cd("card", "width")),
            int(
                cd("margins", "header")
                + beats(mid) * cd("grid", "beat")
                + cd("margins", "footer")
            )
        ),
        color="white"
    )
    ctx.draw = ImageDraw.Draw(ctx.image)

    ctx.font = ImageFont.truetype(pkg_resources.resource_filename(__name__, "OpenSans-CondLight.ttf"), int(c(5)))
    ctx.font_small = ImageFont.truetype(pkg_resources.resource_filename(__name__, "OpenSans-CondLight.ttf"), int(c(2)))

    echo("Generating image...")
    draw_title(ctx, title=basename)  # TODO: Find a title in midi metadata
    draw_labels(ctx)
    draw_labels(ctx, bottom=True)
    draw_arrow(ctx)
    draw_grid(ctx, mid)
    for track in mid.tracks:
        draw_track(ctx, mid, track)

    echo("Post-processing image...")
    (ctx.image
        .resize(
            (ctx.image.size[0] // supersampling, ctx.image.size[1] // supersampling),
            Image.LANCZOS
        )
        .rotate(angle, expand=True)
        .save("%s_%s.png" % (basename, box.symbol), dpi=(original_dpi, original_dpi))
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


def draw_labels(ctx, bottom=False):
    x0 = ctx.cd("margins", "left")
    dx = ctx.cd("grid", "pitch")
    dy0 = ctx.cd("offsets", "lower_pitch_row_to_grid")
    dy1 = ctx.cd("offsets", "upper_pitch_row_to_grid")
    fh = ctx.font.getsize("A")[1]
    y0 = ctx.cd("margins", "header")
    if bottom:
        y0 = ctx.image.size[1] - ctx.cd("margins", "footer") + dy1 * 2

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


def draw_grid(ctx, mid):
    n_beats = beats(mid)
    n_pitches = len(ctx.box.notes)
    margin_top = ctx.cd("margins", "header")
    margin_left = ctx.cd("margins", "left")
    margin_right = ctx.cd("margins", "right")
    beat_height = ctx.cd("grid", "beat")
    pitch_width = ctx.cd("grid", "pitch")
    grid_width = ctx.cd("card", "width") - margin_left - margin_right
    grid_height = n_beats * beat_height
    weight = max(1, int(ctx.c(0.1)))

    # Draw half-beat horizontal lines
    for i in range(n_beats):
        y = beat_height / 2 + margin_top + i * beat_height
        ctx.draw.line(
            xy=[(margin_left, y), (margin_left + grid_width, y)],
            fill="black",
            width=weight
        )

    # Make half-beat lines appear dashed by drawing thick vertical white lines on top
    # Dash length is 2 pitches, and spacing should make
    # the dash perfectly align every 4 dashes, so 0.75
    # Pattern on the original sheet starts from the right side
    weight_white = int(pitch_width * 0.75)
    x = margin_left + grid_width - pitch_width * 2
    x -= weight_white / 2  # Center the whiteout
    n_white_lines = int(n_pitches / 2.75)
    for i in range(n_white_lines + 1):
        ctx.draw.line(
            xy=[
                (x, margin_top),
                (x, margin_top + grid_height)
            ],
            fill="white",
            width=weight_white
        )
        x -= 2.75 * pitch_width

    # Draw vertical lines
    for i in range(n_pitches):
        x = margin_left + i * pitch_width
        ctx.draw.line(
            xy=[
                (x, margin_top),
                (x, margin_top + grid_height)
            ],
            fill="black",
            width=weight
        )

    # Draw beat horizontal lines
    for i in range(n_beats + 1):
        y = margin_top + i * beat_height
        ctx.draw.line(
            xy=[(margin_left, y), (margin_left + grid_width, y)],
            fill="black",
            width=weight
        )
        # Beat numbers
        text = str(i + 1)
        font_size = ctx.font_small.getsize(text)
        xs = (
            margin_left - font_size[0] - pitch_width / 2,
            margin_left + grid_width + pitch_width / 2
        )
        for x in xs:
            ctx.draw.text(
                xy=(x, y - font_size[1] / 2),
                text=text,
                fill="gray",
                font=ctx.font_small
            )


def draw_track(ctx, mid, track):
    pitch_width = ctx.cd("grid", "pitch")
    beat_height = ctx.cd("grid", "beat")
    margin_left = ctx.cd("margins", "left")
    margin_top = ctx.cd("margins", "header")
    radius = ctx.cd("grid", "hole") / 2

    pitch_offsets = {pitch: i * pitch_width for i, pitch in enumerate(ctx.box.notes)}

    t = 0
    for note in track:
        t += note.time
        if note.type == "note_on" and note.velocity > 0:
            x = pitch_offsets[note.note]
            y = beat_height * (t / mid.ticks_per_beat)
            ctx.draw.ellipse(
                xy=[
                    (margin_left - radius + x, margin_top - radius + y),
                    (margin_left + radius + x, margin_top + radius + y)
                ],
                fill="black"
            )
