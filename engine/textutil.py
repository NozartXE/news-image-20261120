"""Small deterministic text helpers built on PIL's ImageFont.

Everything here is a pure function of (text, font, width): no caching
tricks, no randomness, so two runs always agree on line breaks.
"""

from PIL import ImageFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = FONT_DIR + "/DejaVuSerif-Bold.ttf"
SANS_BOLD = FONT_DIR + "/DejaVuSans-Bold.ttf"
SANS = FONT_DIR + "/DejaVuSans.ttf"

_cache = {}


def font(path, size):
    """Load (and memoise) a TrueType font at an integer size."""
    key = (path, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, int(size))
    return _cache[key]


def width_of(text, fnt):
    """Pixel width of a single-line string under the given font."""
    if not text:
        return 0
    left, _top, right, _bottom = fnt.getbbox(text)
    return right - left


def wrap(text, fnt, max_width):
    """Greedy word wrap. Returns a list of lines, each <= max_width wide
    (a single over-long word is returned on its own line, unsplit)."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if width_of(trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


ELLIPSIS = "…"


def fit_to_width(text, path, start_size, max_width, floor_size):
    """Find the largest size in [floor_size, start_size] whose font fits
    the whole text on one line within max_width.

    Returns (font, size, fits). fits is False when even the floor size
    overflows; the caller then knows an ellipsis would be needed and can
    treat that as a legibility failure instead of printing it.
    """
    size = int(start_size)
    while size > floor_size:
        fnt = font(path, size)
        if width_of(text, fnt) <= max_width:
            return fnt, size, True
        size -= 1
    fnt = font(path, floor_size)
    return fnt, floor_size, width_of(text, fnt) <= max_width


def ellipsise(text, fnt, max_width):
    """Shorten text with a trailing ellipsis until it fits max_width.
    Returns the shortened string (detectable: it ends with ELLIPSIS)."""
    if width_of(text, fnt) <= max_width:
        return text
    trimmed = text
    while trimmed and width_of(trimmed + ELLIPSIS, fnt) > max_width:
        trimmed = trimmed[:-1].rstrip()
    return trimmed + ELLIPSIS if trimmed else ELLIPSIS
