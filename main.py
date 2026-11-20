"""Deliver the committed front-page image to the output directory.

The page itself is rendered during development by build_image.py
and the engine package. This shipped entrypoint only copies the
committed PNG files into MAKEFUN_OUTPUT_DIR using the standard
library — the simple delivery pattern the competition rules describe.
"""
import os
import shutil
import sys

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or base
    os.makedirs(out_dir, exist_ok=True)
    for name in ("entry.png", "entry-480.png"):
        src = os.path.join(base, name)
        if not os.path.isfile(src):
            if name == "entry.png":
                print(f"missing {src}", file=sys.stderr)
                return 1
            continue
        dst = os.path.join(out_dir, name)
        same = os.path.abspath(src) == os.path.abspath(dst)
        if not same and os.path.exists(dst):
            same = os.path.samefile(src, dst)
        if not same:
            shutil.copyfile(src, dst)
        print(f"wrote {dst} {os.path.getsize(dst)} bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main())
