"""Entrypoint: build the front-page image and its 480 px version.

Reads the day's content file, runs the editorial validator, renders
``entry.png`` (1024x1024) and ``entry-480.png`` (a bicubic downscale,
the size the picture desk proofs at) next to this file.
"""

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import layout, validate


def build(base_dir=None):
    base = base_dir or os.path.dirname(os.path.abspath(__file__))
    data = layout.load_content(layout.default_content_path(base))
    message, ok = validate.report(data)
    print("validator:", message)
    if not ok:
        raise SystemExit(1)
    img = layout.build_image(data)
    out = os.path.join(base, "entry.png")
    img.save(out, optimize=True)
    small = img.resize((480, 480), Image.BICUBIC)
    small.save(os.path.join(base, "entry-480.png"), optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")
    return out


if __name__ == "__main__":
    build()
