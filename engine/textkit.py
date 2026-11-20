"""Text helpers: cached fonts, wrapping, and ink-anchored drawing.

``draw_ink`` places a string so that the top-left corner of its
*rendered ink* (not its em box) lands exactly on the requested point.
Newspaper columns are aligned by what the reader sees, so every text
element on the page is positioned by its ink box.
"""

from PIL import ImageFont

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def ink_box(draw, text, fnt):
    """Bounding box (x0, y0, x1, y1) of the ink if drawn at (0, 0)."""
    return draw.textbbox((0, 0), text, font=fnt)


def ink_size(draw, text, fnt):
    box = ink_box(draw, text, fnt)
    return box[2] - box[0], box[3] - box[1]


def text_width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def draw_ink(draw, x, y, text, fnt, fill):
    """Draw ``text`` with its ink top-left at (x, y)."""
    box = ink_box(draw, text, fnt)
    draw.text((x - box[0], y - box[1]), text, font=fnt, fill=fill)
    return box[2] - box[0], box[3] - box[1]


def draw_ink_right(draw, right, y, text, fnt, fill):
    """Draw ``text`` with its ink top-right at (right, y)."""
    box = ink_box(draw, text, fnt)
    draw.text((right - box[2], y - box[1]), text, font=fnt, fill=fill)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns the list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
