"""The accounting gate for the C2 front page (news-image-20261120).

validate(content) raises ValueError on the first broken rule and
otherwise returns the stats dict the layout prints from. The rules
encode the C2 standard as judged for this edition:

- the printed total is set by the VERIFIED list, never the reverse:
  stories == printed_total, >= 43, exactly 4 heroes + 12 cards = 16
  illustrated, the rest index;
- numbering continuous 1..N in page order (heroes, cards, index);
- timeline slots carry clock times ONLY where a time is wire-sourced
  (Akvan noon landfall); every other slot is a sequence label;
- index stories come from Section A only (20-Nov news); Section B
  stories appear only as heroes/cards with a "19 NOV" kicker, and
  Section C never appears anywhere;
- every hero/card dek carries its date; key figures are printed once
  and on one stated basis (Akvan ~298,676 evacuated, Dow -1,101 close,
  Anthropic ~$1.3tn close basis, GTA VI ~$1.84bn ESTIMATE);
- the DATE CHECK names only stories NOT printed on the page, so it
  can never contradict a hero or card kicker.
"""

import re

REGION_ORDER = ["Asia", "Middle East", "Europe", "North America",
                "South America", "Africa", "Oceania", "Global"]

MIN_STORIES = 43
HEROES = 4
CARDS = 12
ILLUSTRATED = 16

# Clock-time patterns a timeline slot may never carry unless the slot
# is flagged sourced_time (the only sourced time is Akvan's noon).
CLOCK_RE = re.compile(r"\d{1,2}:\d{2}|~\d{1,2}\b|\b\d{1,2}\s?(?:AM|PM)\b", re.I)
DATE_TOKEN_RE = re.compile(r"\b(?:19|20) NOV\b|REPORTED 20 NOV", re.I)

# Figures that must appear exactly once on the page (and never twice).
SINGLE_FIGURES = ("298,676", "1,101", "$1.3tn", "$1.84bn", "146*", "317/6", "51\u201348", "1,070")
# Figures that must appear NOWHERE on the page (wrong measure/basis).
BANNED_FIGURES = ("105,304", "1,084", "$1.5tn", "$1.75tn", "$1.8tn")
# Stories the DATE CHECK excludes: none of these names may appear in
# any story's printed text, or the check would contradict the page.
DATECHECK_EXCLUDED = ("Voyager", "ICJ", "Crimea", "Pete Rose")
# Card deks whose story has no numeric key fact (date alone carries it).
NO_DIGIT_DEKS = {"A14", "A22", "A29", "A55"}

# Index brief geometry: 3 cols in the 642 px index width, 24 px rows.
INDEX_TEXT_W = 186


def _printed_texts(story):
    texts = [story.get("headline", "") or "", story.get("dek", "") or "",
             story.get("brief", "") or "", story.get("place", "") or ""]
    spec = story.get("scene_spec") or {}
    if spec.get("label"):
        texts.append(spec["label"])
    return texts


def story_order(stories):
    heroes = [s for s in stories if s.get("tier") == "hero"]
    cards = [s for s in stories if s.get("tier") == "card"]
    index = [s for s in stories if s.get("tier") not in ("hero", "card")]
    return heroes + cards + index


def numbering(stories):
    return {s["id"]: n for n, s in enumerate(story_order(stories), start=1)}


def region_counts(stories):
    counts = {region: 0 for region in REGION_ORDER}
    for story in stories:
        counts[story["region"]] += 1
    return counts


def scope_line(stats):
    return "%d STORIES \u00b7 %d REGIONS \u00b7 %d ILLUSTRATED" % (
        stats["stories"], stats["regions"], stats["illustrated"])


def validate(content):
    stories = content.get("stories")
    if not isinstance(stories, list):
        raise ValueError("content has no stories list")
    if content.get("printed_total") != len(stories):
        raise ValueError("printed total %r != enumerated stories %d"
                         % (content.get("printed_total"), len(stories)))
    if len(stories) < MIN_STORIES:
        raise ValueError("fewer than %d stories: %d"
                         % (MIN_STORIES, len(stories)))

    ids = [s.get("id") for s in stories]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate story ids")

    heroes = [s for s in stories if s.get("tier") == "hero"]
    cards = [s for s in stories if s.get("tier") == "card"]
    index = [s for s in stories if s.get("tier") not in ("hero", "card")]
    if len(heroes) != HEROES:
        raise ValueError("expected %d heroes, found %d" % (HEROES, len(heroes)))
    if len(cards) != CARDS:
        raise ValueError("expected %d cards, found %d" % (CARDS, len(cards)))
    illustrated = [s for s in stories if s.get("scene")]
    if len(illustrated) != ILLUSTRATED:
        raise ValueError("illustrated count %d != %d"
                         % (len(illustrated), ILLUSTRATED))
    if len(index) != len(stories) - ILLUSTRATED:
        raise ValueError("index count %d != stories - illustrated"
                         % len(index))

    from .scenes import PAINTERS
    from . import textutil as tu

    for story in stories:
        for field in ("region", "place"):
            if not (story.get(field) or "").strip():
                raise ValueError("story %s: empty %s" % (story.get("id"), field))
        if story.get("region") not in REGION_ORDER:
            raise ValueError("story %s: unknown region %r"
                             % (story.get("id"), story.get("region")))
        if story.get("source_section") not in ("A", "B"):
            raise ValueError("story %s: source_section %r is not A or B "
                             "(Section C is never printed)"
                             % (story.get("id"), story.get("source_section")))
        if story.get("tier") == "index" and story.get("source_section") != "A":
            raise ValueError("story %s: index item from Section %s - "
                             "index holds Section A only"
                             % (story.get("id"), story.get("source_section")))
        if story.get("tier") in ("hero", "card"):
            if story.get("source_section") == "B":
                kd = story.get("kicker_date") or ""
                if "19 NOV" not in kd:
                    raise ValueError("story %s: Section B hero/card without "
                                     "'19 NOV' kicker date" % story.get("id"))
            if story["scene"] not in PAINTERS:
                raise ValueError("story %s: unknown painter %r"
                                 % (story.get("id"), story["scene"]))
            if not story.get("kicker_date"):
                raise ValueError("story %s: hero/card without kicker_date"
                                 % story.get("id"))
            dek = story.get("dek") or ""
            if not DATE_TOKEN_RE.search(dek):
                raise ValueError("story %s: dek %r carries no date token"
                                 % (story.get("id"), dek))
            if story.get("id") not in NO_DIGIT_DEKS:
                if not any(ch.isdigit() for ch in dek):
                    raise ValueError("story %s: card/hero dek carries no figure"
                                     % story.get("id"))
            # Headline/dek fit: hero 240 px, card 157 px.
            w = 240 if story["tier"] == "hero" else 157
            hfnt = tu.font(tu.SERIF_BOLD if story["tier"] == "hero" else tu.SANS_BOLD,
                           17 if story["tier"] == "hero" else 13)
            if len(tu.wrap(story["headline"], hfnt, w)) > 2:
                raise ValueError("story %s: headline wraps past 2 lines"
                                 % story.get("id"))
            dfnt = tu.font(tu.SANS, 12 if story["tier"] == "hero" else 11)
            dlines = tu.wrap(dek, dfnt, w)
            if len(dlines) > (2 if story["tier"] == "hero" else 1):
                # Card deks may shrink to 9 px; re-check at the floor.
                if story["tier"] == "card":
                    dfnt9 = tu.font(tu.SANS, 9)
                    if len(tu.wrap(dek, dfnt9, w)) > 1:
                        raise ValueError("story %s: card dek does not fit "
                                         "one line even at 9 px" % story.get("id"))
                else:
                    raise ValueError("story %s: hero dek wraps past 2 lines"
                                     % story.get("id"))
        else:
            brief = story.get("brief") or ""
            if not brief:
                raise ValueError("story %s: index item without brief"
                                 % story.get("id"))
            if brief[-1] not in ".!?":
                raise ValueError("story %s: brief %r does not end with "
                                 "terminal punctuation" % (story.get("id"), brief))
            bfnt = tu.font(tu.SANS_BOLD, 10)
            if len(tu.wrap(brief, bfnt, INDEX_TEXT_W)) > 2:
                raise ValueError("story %s: index brief wraps past 2 lines "
                                 "at 10 px" % story.get("id"))

    expected = numbering(stories)
    printed = [s.get("num") for s in stories]
    if any(not isinstance(n, int) for n in printed):
        raise ValueError("every story must carry an integer num")
    if sorted(printed) != list(range(1, len(stories) + 1)):
        raise ValueError("numbering is not continuous 1-%d" % len(stories))
    for story in stories:
        if story["num"] != expected[story["id"]]:
            raise ValueError("story %s: num %r != page position %d"
                             % (story.get("id"), story["num"],
                                expected[story["id"]]))

    # Timeline: sequence labels only, unless the slot's time is sourced.
    timeline = content.get("timeline") or []
    if len(timeline) != 6:
        raise ValueError("timeline must have 6 slots, found %d" % len(timeline))
    nums = {s["num"] for s in stories}
    for slot in timeline:
        if slot.get("story_num") not in nums:
            raise ValueError("timeline slot %r points at no story"
                             % (slot.get("label"),))
        text = (slot.get("label", "") + " " + slot.get("text", ""))
        if not slot.get("sourced_time") and CLOCK_RE.search(text):
            raise ValueError("timeline slot %r carries a clock time without "
                             "a sourced time" % (slot.get("label"),))
        if re.search(r"\bnoon\b", text, re.I) and not slot.get("sourced_time"):
            raise ValueError("timeline slot %r uses 'noon' without a sourced "
                             "time" % (slot.get("label"),))

    # Figures: each single-use figure exactly once; banned figures never.
    all_text = "\n".join(t for s in stories for t in _printed_texts(s))
    for fig in SINGLE_FIGURES:
        if all_text.count(fig) != 1:
            raise ValueError("figure %r appears %d times, must appear once"
                             % (fig, all_text.count(fig)))
    for fig in BANNED_FIGURES:
        if fig in all_text:
            raise ValueError("banned figure %r in printed text (wrong "
                             "measure/basis)" % fig)
    if "$1.84bn" in all_text:
        holder = [s for s in stories
                  if "$1.84bn" in (s.get("dek", "") or "")]
        if not holder or "EST" not in (holder[0].get("dek", "") or ""):
            raise ValueError("GTA VI $1.84bn printed without ESTIMATE label")

    # DATE CHECK consistency: excluded names appear nowhere on the page.
    for name in DATECHECK_EXCLUDED:
        if name.lower() in all_text.lower():
            raise ValueError("DATE CHECK excluded story %r is printed on the "
                             "page - contradiction" % name)

    counts = region_counts(stories)
    if sum(counts.values()) != len(stories):
        raise ValueError("region counts sum to %d, not %d"
                         % (sum(counts.values()), len(stories)))
    regions = {s["region"] for s in stories}
    return {
        "stories": len(stories),
        "illustrated": len(illustrated),
        "heroes": len(heroes),
        "cards": len(cards),
        "index": len(index),
        "regions": len(regions),
        "region_counts": counts,
    }


def scope_line(stats):
    return "%d STORIES \u00b7 %d REGIONS \u00b7 %d ILLUSTRATED" % (
        stats["stories"], stats["regions"], stats["illustrated"])
