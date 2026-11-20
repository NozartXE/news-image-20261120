"""Command-line wrapper around ``main.build``.

Kept as a separate, tiny module so the build can be invoked as
``python3 build_image.py`` from scripts that predate the entrypoint
name; all of the work lives in ``main`` and ``engine``.
"""

import main as _main


def build(base_dir=None):
    return _main.build(base_dir)


if __name__ == "__main__":
    build()
