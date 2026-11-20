"""Platform entry point (standard library only).

Copies the committed entry.png next to this file into
$MAKEFUN_OUTPUT_DIR/entry.png, creating the directory if needed.
"""

import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set")
        return 1
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
