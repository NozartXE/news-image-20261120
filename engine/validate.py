"""Editorial gate checks for the front page.

The validator re-derives every number the page prints from the
content file and fails the build if any of them disagree:

- story / illustration / hero / card / index counts and region count;
- numbering runs 1..N with no gaps;
- every illustrated story is dated 20 NOV (the masthead's own day);
- the DATE CHECK exclusions are genuinely absent from printed text;
- each key figure is printed exactly once in story text
  (the figure strip is layout furniture and is not counted);
- legibility: no index brief wraps past two lines at its printed
  width, and hero headlines / deks fit the narrower hero column.
"""

from PIL import Image, ImageDraw

from . import palette
from .textkit import font, wrap

MIN_STORIES = 40
ILLUSTRATED = 12
HEROES = 2
CARDS = 10
INDEX_COUNT = 28
REGIONS = 7
INDEX_TEXT_W = 211
HERO_FIT_W = 327

# Figures that must appear exactly once across all story text.
SINGLE_FIGURES = [
    "300,000", "+0.4%", "144→80", "146*", "317/6", "51–48",
    "72nd", "1,070", "$92.22",
]

# Names/figures belonging to the excluded off-date items; none may
# appear in any printed story text.
DATECHECK_EXCLUDED = [
    "Voyager", "ICJ", "Crimea", "Pete Rose", "Shenzhen", "PIF Tower",
    "Dow", "Anthropic debut", "GTA VI",
]

# Figures that must never print at all (off-date or unverified).
BANNED_FIGURES = ["298,676", "1,101", "$1.84bn", "$1.3tn"]


def _printed_story_text(data):
    parts = []
    for story in data["stories"]:
        for key in ("headline", "dek", "brief"):
            if story.get(key):
                parts.append(story[key])
    return "\n".join(parts)


def validate(data):
    """Return a list of failure strings; empty means PASS."""
    failures = []
    stories = sorted(data["stories"], key=lambda s: s["num"])
    illustrated = [s for s in stories if s.get("scene")]
    heroes = [s for s in stories if s.get("tier") == "hero"]
    cards = [s for s in stories if s.get("tier") == "card"]
    briefs = [s for s in stories if s.get("tier") == "index"]
    regions = {s["region"] for s in stories}

    if len(stories) != MIN_STORIES:
        failures.append("stories=%d, want %d" % (len(stories), MIN_STORIES))
    if len(illustrated) != ILLUSTRATED:
        failures.append("illustrated=%d, want %d"
                        % (len(illustrated), ILLUSTRATED))
    if len(heroes) != HEROES:
        failures.append("heroes=%d, want %d" % (len(heroes), HEROES))
    if len(cards) != CARDS:
        failures.append("cards=%d, want %d" % (len(cards), CARDS))
    if len(briefs) != INDEX_COUNT:
        failures.append("index=%d, want %d" % (len(briefs), INDEX_COUNT))
    if len(regions) != REGIONS:
        failures.append("regions=%d, want %d" % (len(regions), REGIONS))
    if data.get("printed_total") != len(stories):
        failures.append("printed_total=%r but %d stories"
                        % (data.get("printed_total"), len(stories)))

    nums = [s["num"] for s in stories]
    if nums != list(range(1, len(stories) + 1)):
        failures.append("numbering is not 1..%d" % len(stories))

    for story in illustrated:
        if "20 NOV" not in (story.get("kicker_date") or ""):
            failures.append("illustrated story %d not dated 20 NOV"
                            % story["num"])
        if story.get("source_section") != "A":
            failures.append("illustrated story %d not Section A"
                            % story["num"])
    for story in briefs:
        if story.get("source_section") != "A":
            failures.append("index story %d not Section A" % story["num"])

    text = _printed_story_text(data)
    for token in SINGLE_FIGURES:
        count = text.count(token)
        if count != 1:
            failures.append("figure %r printed %d times, want 1"
                            % (token, count))
    for token in DATECHECK_EXCLUDED:
        if token in text:
            failures.append("DATE CHECK exclusion %r appears in text"
                            % token)
    for token in BANNED_FIGURES:
        if token in text:
            failures.append("banned figure %r appears in text" % token)

    # timeline slots must name card row 1's stories in order
    row1 = [s["num"] for s in cards[:6]]
    slots = [slot["story_num"] for slot in data["timeline"]]
    if slots != row1:
        failures.append("timeline slots %r != card row 1 %r"
                        % (slots, row1))
    for slot in data["timeline"]:
        if slot.get("sourced_time"):
            failures.append("timeline slot %r claims a sourced time"
                            % slot["label"])

    # legibility: measured wraps at printed widths
    probe = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(probe)
    brief_fnt = font(palette.SANS_BOLD, 12)
    warnings = 0
    for story in briefs:
        if len(wrap(draw, story["brief"], brief_fnt, INDEX_TEXT_W)) > 2:
            failures.append("brief %d wraps past 2 lines" % story["num"])
            warnings += 1
    head_fnt = font(palette.SERIF_BOLD, 19)
    dek_fnt = font(palette.SANS, 13)
    for story in heroes:
        for line in wrap(draw, story["headline"], head_fnt, HERO_FIT_W):
            if draw.textlength(line, font=head_fnt) > HERO_FIT_W:
                failures.append("hero headline line too wide: %r" % line)
                warnings += 1
        if draw.textlength(story["dek"], font=dek_fnt) > 655:
            failures.append("hero dek too wide for its column")
            warnings += 1
    return failures, warnings, {
        "stories": len(stories), "illustrated": len(illustrated),
        "heroes": len(heroes), "cards": len(cards),
        "index": len(briefs), "regions": len(regions),
    }


def report(data):
    failures, warnings, stats = validate(data)
    line = ("stories=%d, illustrated=%d, heroes=%d, cards=%d, "
            "index=%d, regions=%d, warnings=%d"
            % (stats["stories"], stats["illustrated"], stats["heroes"],
               stats["cards"], stats["index"], stats["regions"], warnings))
    if failures:
        return "FAIL: " + "; ".join(failures), False
    return "PASS (%s)" % line, True
