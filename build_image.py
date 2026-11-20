"""Build the C2 front page: content JSON in, entry.png out.

Fails hard on any validator violation or on an output over 1 MiB.
Prints the stats line, the byte size, the sha256 and every
legibility warning.
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.layout import render
from engine.validate import validate

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BYTES = 1024 * 1024


def main():
    with open(os.path.join(HERE, "content", "content-20261120.json"),
              encoding="utf-8") as fh:
        content = json.load(fh)

    stats = validate(content)
    img, warnings = render(content, stats)

    out_path = os.path.join(HERE, "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    if size > MAX_BYTES:
        print("REFUSED: entry.png is %d bytes, over the 1 MiB cap" % size)
        return 1

    small = img.resize((480, 480))
    small.save(os.path.join(HERE, "entry-480.png"), format="PNG", optimize=True)

    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()

    print("stories=%(stories)d illustrated=%(illustrated)d "
          "heroes=%(heroes)d cards=%(cards)d index=%(index)d "
          "regions=%(regions)d" % stats)
    print("entry.png bytes=%d sha256=%s" % (size, digest))
    if warnings:
        print("legibility warnings: %d" % len(warnings))
        for warning in warnings:
            print("  WARNING: " + warning)
    else:
        print("legibility warnings: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
