"""Page composition for the one-image front page.

The page is a stack of horizontal bands whose heights sum to the
1024 px canvas::

    kicker 26 + date 88 + figure strip 48 + hero row 224
    + timeline 26 + cards 332 + index band 216 + date check 44
    + footer 20 = 1024

Inside the bands, stories are placed by tier: two heroes (a wide
lead and a narrower second), ten cards in two rows, and the rest as
numbered one-paragraph briefs in the index.  Text is drawn with
plain ``draw.text`` calls at the column edge; the y positions below
were chosen so each element's ink lands on its band grid.
"""

import json
import os

from PIL import Image, ImageDraw

from . import palette, scenes
from .textkit import font, wrap

MARGIN = 16
PAGE_W = 1024
CONTENT_W = 992
RIGHT = MARGIN + CONTENT_W  # 1008

KICKER_H = 26
DATE_H = 88
FIGSTRIP_H = 48
HERO_H = 224
TIMELINE_H = 26
CARDS_H = 332
INDEX_H = 216
DATECHECK_H = 44
FOOTER_H = 20

HERO1_W = 655
HERO2_W = 327
HERO_SCENE_H = 134
CARD_SCENE_H = 110
CARD_ROW_H = 166

FIGURE_STRIP = [
    ("300,000", "EVACUATED AHEAD OF AKVAN"),
    ("+0.4%", "UK ECONOMY, EU–UK SUMMIT"),
    ("144→80", "COP31 DRAFT CUT"),
    ("146*", "NICHOLLS, WELLINGTON"),
    ("51–48", "SENATE WAR-POWERS VOTE"),
    ("$92.22", "BRENT, FRIDAY"),
]

DATE_CHECK_LEAD = "DATE CHECK \u2014 NOT TODAY: "
DATE_CHECK_REST = (
    "Voyager 1 light-day (18 Nov) \u00b7 ICJ Myanmar ruling (19 Nov) \u00b7 "
    "Crimea Bridge strike (19 Nov) \u00b7 Pete Rose pardon (19 Nov) \u00b7 "
    "Shenzhen summit (19 Nov) \u00b7 PIF Tower strike (19 Nov) \u00b7 "
    "Dow"
)
DATE_CHECK_L2 = (
    "\u22121,101 close (19 Nov) \u00b7 Anthropic debut (19 Nov) \u00b7 "
    "GTA VI $1.84bn (19 Nov)"
)

FOOTER_SOURCES = (
    "The Hindu · AP · Le Monde · Reuters · Vatican News · NATO PA · "
    "Cricinfo · Geo News · Times Now · Haaretz · NDTV · NST · AFP · "
    "Manila Times · Al Jazeera · Gulf Times · VietnamPlus · PIB · WSJ · "
    "Barron's · AsiaToday · Straits Times"
)


def _regions_in_order(stories):
    order = ["Asia", "Middle East", "Europe", "North America", "Africa",
             "Oceania", "Global"]
    present = {s["region"] for s in stories}
    return [r for r in order if r in present]


def _draw_kicker(draw, data, stats):
    fnt = font(palette.SANS_BOLD, 12)
    draw.text((MARGIN, 6), "ONE DAY OF WORLD NEWS, ONE PICTURE",
              font=fnt, fill=palette.INK)
    scope = "%d STORIES · %d REGIONS · %d ILLUSTRATED" % (
        stats["stories"], stats["regions"], stats["illustrated"])
    bb = draw.textbbox((0, 0), scope, font=fnt)
    draw.text((RIGHT - bb[2], 6), scope, font=fnt, fill=palette.ACCENT)


def _draw_masthead(draw, data):
    fnt = font(palette.SERIF_BOLD, 56)
    y = KICKER_H
    draw.text((MARGIN, y + 14), data["date_line"], font=fnt,
              fill=palette.INK)
    draw.rectangle([MARGIN, y + 82, RIGHT, y + 85], fill=palette.INK)


def _draw_figure_strip(draw, y):
    fig_fnt = font(palette.SERIF_BOLD, 24)
    lab_fnt = font(palette.SANS_BOLD, 9)
    cell_w = 165
    for i, (figure, label) in enumerate(FIGURE_STRIP):
        cx = MARGIN + i * cell_w
        if i:
            draw.line([cx - 1, y + 5, cx - 1, y + 41],
                      fill=palette.FRAME)
        draw.text((cx + 4, y + 3), figure, font=fig_fnt,
                  fill=palette.ACCENT)
        draw.text((cx + 4, y + 32), label, font=lab_fnt,
                  fill=palette.TAG_INK)
    draw.line([MARGIN, y + FIGSTRIP_H - 1, RIGHT, y + FIGSTRIP_H - 1],
              fill=palette.FRAME)


def _hero_text(draw, story, x, w, y_scene_bottom, regions=None):
    kick_fnt = font(palette.SANS_BOLD, 10)
    head_fnt = font(palette.SERIF_BOLD, 19)
    dek_fnt = font(palette.SANS, 13)
    ty = y_scene_bottom + 2
    draw.text((x, ty), "%s · %s" % (story["place"], story["kicker_date"]),
              font=kick_fnt, fill=palette.ACCENT)
    ty += 14
    lines = wrap(draw, story["headline"], head_fnt, w)
    for line in lines:
        draw.text((x, ty), line, font=head_fnt, fill=palette.INK)
        ty += 21
    draw.text((x, ty), story["dek"], font=dek_fnt, fill=palette.SOFT_INK)
    if regions:
        _region_chips(draw, x, ty + 23, regions)
    return ty


def _region_chips(draw, x, y, regions):
    lead_fnt = font(palette.SANS_BOLD, 8)
    chip_fnt = font(palette.SANS_BOLD, 8)
    draw.text((x, y + 2), "REGIONS:", font=lead_fnt, fill=palette.ACCENT)
    cx = x + int(draw.textlength("REGIONS:", font=lead_fnt)) + 7
    for region in regions:
        label = region.upper()
        bb = draw.textbbox((0, 0), label, font=chip_fnt)
        chip_w = (bb[2] - bb[0]) + 10
        draw.rectangle([cx, y, cx + chip_w, y + 13],
                       outline=palette.TAG_INK, width=1)
        draw.text((cx + 5, y + 2), label, font=chip_fnt,
                  fill=palette.TAG_INK)
        cx += chip_w + 5


def _draw_heroes(draw, img, stories, regions, y):
    hero1, hero2 = stories[0], stories[1]
    box1 = (MARGIN, y, HERO1_W, HERO_SCENE_H)
    box2 = (MARGIN + HERO1_W + 10, y, HERO2_W, HERO_SCENE_H)
    scenes.paint_scene(img, draw, box1, hero1)
    scenes.paint_scene(img, draw, box2, hero2)
    bottom = y + HERO_SCENE_H + 2
    _hero_text(draw, hero1, MARGIN, HERO1_W, bottom, regions=regions)
    _hero_text(draw, hero2, MARGIN + HERO1_W + 10, HERO2_W, bottom)


def _draw_timeline(draw, data, y):
    lab_fnt = font(palette.SANS_BOLD, 10)
    txt_fnt = font(palette.SANS, 10)
    chev_fnt = font(palette.SANS_BOLD, 12)
    cell_w = 167
    for i, slot in enumerate(data["timeline"]):
        cx = MARGIN + i * cell_w
        if i:
            draw.text((cx - 8, y + 6), "›", font=chev_fnt,
                      fill=palette.TAG_INK)
        draw.text((cx, y + 1), "%s #%d" % (slot["label"], slot["story_num"]),
                  font=lab_fnt, fill=palette.ACCENT)
        draw.text((cx, y + 13), slot["text"], font=txt_fnt,
                  fill=palette.TAG_INK)
    draw.line([MARGIN, y + TIMELINE_H - 1, RIGHT, y + TIMELINE_H - 1],
              fill=palette.FRAME)


def _number_box(draw, x, y, num):
    """Ink box sized to the numeral, story number in white bold 8."""
    label = str(num)
    fnt = font(palette.SANS_BOLD, 8)
    bb = draw.textbbox((0, 0), label, font=fnt)
    w = bb[2] + 6 + (3 if len(label) == 1 else 0)
    draw.rectangle([x, y, x + w, y + 11], fill=palette.INK)
    draw.text((x + (w - bb[2]) // 2 - bb[0], y + 2),
              label, font=fnt, fill=palette.PAPER)
    return w + 1


def _card_text(draw, story, x, w, y_top):
    head_fnt = font(palette.SANS_BOLD, 13)
    box_w = _number_box(draw, x, y_top, story["num"])
    kicker = "%s · %s" % (story["place"], story["kicker_date"])
    kx = x + box_w + 3
    ksize = 9
    while ksize > 7 and draw.textlength(
            kicker, font=font(palette.SANS_BOLD, ksize)) > w - (kx - x) - 16:
        ksize -= 1
    draw.text((kx, y_top), kicker,
              font=font(palette.SANS_BOLD, ksize), fill=palette.ACCENT)
    ty = y_top + 13
    lines = wrap(draw, story["headline"], head_fnt, w)
    for line in lines:
        draw.text((x, ty), line, font=head_fnt, fill=palette.INK)
        ty += 14
    dsize = 11
    while dsize > 8 and draw.textlength(
            story["dek"], font=font(palette.SANS, dsize)) > w:
        dsize -= 1
    draw.text((x, y_top + 13 + 14 * len(lines)), story["dek"],
              font=font(palette.SANS, dsize), fill=palette.SOFT_INK)


def _draw_cards(draw, img, cards, y):
    row1, row2 = cards[:6], cards[6:]
    for i, story in enumerate(row1):
        cx = MARGIN + i * 167
        box = (cx, y, 157, CARD_SCENE_H)
        scenes.paint_scene(img, draw, box, story)
        _card_text(draw, story, cx, 158, y + CARD_SCENE_H + 3)
    y2 = y + CARD_ROW_H
    for i, story in enumerate(row2):
        cx = MARGIN + i * 250
        w = RIGHT - cx if i == len(row2) - 1 else 241
        scene_w = w if i == len(row2) - 1 else w - 1
        box = (cx, y2, scene_w, CARD_SCENE_H)
        scenes.paint_scene(img, draw, box, story)
        _card_text(draw, story, cx, w, y2 + CARD_SCENE_H + 3)


def _draw_index(draw, briefs, y):
    head_fnt = font(palette.SANS_BOLD, 12)
    draw.text((MARGIN, y + 4), "MORE OF THE DAY — %d STORIES" % len(briefs),
              font=head_fnt, fill=palette.INK)
    note = "%d ILLUSTRATED ABOVE" % 12
    note_fnt = font(palette.SANS, 10)
    bb = draw.textbbox((0, 0), note, font=note_fnt)
    draw.text((RIGHT - bb[2], y + 5), note, font=note_fnt,
              fill=palette.TAG_INK)
    draw.line([MARGIN, y + 18, RIGHT, y + 18], fill=palette.INK)
    brief_fnt = font(palette.SANS_BOLD, 12)
    col_w = CONTENT_W // 4
    row_h = 28
    for idx, story in enumerate(briefs):
        col, row = divmod(idx, 7)
        cx = MARGIN + col * col_w
        cy = y + 22 + row * row_h
        draw.rectangle([cx, cy, cx + 26, cy + 13], fill=palette.INK)
        draw.text((cx + 3, cy + 1), "%d." % story["num"],
                  font=brief_fnt, fill=palette.PAPER)
        lines = wrap(draw, story["brief"], brief_fnt, 211)
        ly = cy
        for line in lines[:2]:
            draw.text((cx + 30, ly), line, font=brief_fnt,
                      fill=palette.INK)
            ly += 14


def _draw_date_check(draw, y):
    draw.rectangle([MARGIN, y, RIGHT, y + DATECHECK_H - 2],
                   outline=palette.ACCENT, width=1)
    lead_fnt = font(palette.SANS_BOLD, 9)
    body_fnt = font(palette.SANS, 9)
    tx = MARGIN + 6
    draw.text((tx, y + 7), DATE_CHECK_LEAD, font=lead_fnt,
              fill=palette.INK)
    # the rest starts its own run (with a leading space) right where the
    # bold lead's advance ends, truncated to whole pixels
    lx = tx + int(draw.textlength(DATE_CHECK_LEAD.rstrip(), font=lead_fnt))
    draw.text((lx, y + 7), " " + DATE_CHECK_REST, font=body_fnt,
              fill=palette.INK)
    draw.text((tx, y + 19), DATE_CHECK_L2, font=body_fnt,
              fill=palette.INK)


def _draw_footer(draw, y):
    fnt = font(palette.SANS, 7)
    draw.text((MARGIN, y + 4), "SOURCES: " + FOOTER_SOURCES +
              " \u00b7 Drawn in code", font=fnt, fill=palette.TAG_INK)


def compute_stats(data):
    stories = data["stories"]
    illustrated = [s for s in stories if s.get("scene")]
    heroes = [s for s in stories if s.get("tier") == "hero"]
    cards = [s for s in stories if s.get("tier") == "card"]
    briefs = [s for s in stories if s.get("tier") == "index"]
    regions = _regions_in_order(stories)
    return {
        "stories": len(stories),
        "illustrated": len(illustrated),
        "heroes": len(heroes),
        "cards": len(cards),
        "index": len(briefs),
        "regions": len(regions),
        "region_names": regions,
    }


def build_image(data):
    """Render the full front page from the content dict."""
    img = Image.new("RGB", (PAGE_W, PAGE_W), palette.PAPER)
    draw = ImageDraw.Draw(img)
    stats = compute_stats(data)
    stories = sorted(data["stories"], key=lambda s: s["num"])
    heroes = [s for s in stories if s["tier"] == "hero"]
    cards = [s for s in stories if s["tier"] == "card"]
    briefs = [s for s in stories if s["tier"] == "index"]

    y = 0
    _draw_kicker(draw, data, stats)
    y += KICKER_H
    _draw_masthead(draw, data)
    y += DATE_H
    _draw_figure_strip(draw, y)
    y += FIGSTRIP_H
    _draw_heroes(draw, img, heroes, stats["region_names"], y)
    y += HERO_H
    _draw_timeline(draw, data, y)
    y += TIMELINE_H
    _draw_cards(draw, img, cards, y)
    y += CARDS_H
    _draw_index(draw, briefs, y)
    y += INDEX_H
    _draw_date_check(draw, y)
    y += DATECHECK_H
    _draw_footer(draw, y)
    y += FOOTER_H
    assert y == PAGE_W, y
    return img


def load_content(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def default_content_path(base_dir):
    return os.path.join(base_dir, "content", "content-20261120.json")
