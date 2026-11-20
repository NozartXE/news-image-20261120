# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/NozartXE/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/NozartXE/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image that sums up the world news of Friday 20 November 2026: a
date-as-masthead front page with a day-arc timeline, one dominant hero
(Tropical Storm Akvan, drawn large enough to fill its frame), a figure
strip of the day's key numbers — each figure appearing exactly once on
the page — ten more stories as drawn scene-cards, and the rest of the
day as one-line briefs. 40 stories, every illustrated story pure
20-November news; a DATE CHECK panel lists the 19-November items that
were deliberately excluded, and the validator fails the build if any
excluded story is printed anywhere on the page.

The picture is drawn by a deterministic engine (`engine/`, Pillow): a
validated content file goes in, a byte-identical 1024×1024 PNG comes
out. The validator refuses to draw a page whose accounting breaks —
story counts, scene counts, region counts, or a figure repeated outside
its one allowed place.

## Run it

```sh
python3 build_image.py            # draws entry.png from the edition content
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — a whole PNG, 1024x1024, under the 1 MiB gate
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=b9zyas72&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
