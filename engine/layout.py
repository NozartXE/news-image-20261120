"""The C2 date-as-masthead + day-arc assembler (news-image-20261120).

Canvas 1024x1024, off-white paper, near-black ink, one muted red
accent. The vertical budget is fixed by named constants and sums to
the full canvas height:

    kicker 26 + date masthead 96 + timeline 26 + hero row 228
    + card rows 320 (2 x 160) + map/index band 264
    + DATE CHECK 44 + footer 20 = 1024

The 20 px the timeline gives back against the C2 spec (46 -> 26)
fund the card rows (300 -> 320), so card scenes are 157x96 instead
of 170x84: the panel's defect-1 fix. Card width is 157, not the
spec's 170, because six cards must fit the 992 px content width
after 16 px margins; scene height 96 is kept as specified.

Stories are numbered continuously 1..46 in page order (4 heroes,
12 cards, 30 index). The map carries pins 1-16 for the illustrated
stories only, at the re-derived NI20 positions in scenes.py.
The DATE CHECK names only stories NOT printed on the page
(Voyager 18 Nov, ICJ 19 Nov, Crimea Bridge 19 Nov, Pete Rose
19 Nov, plus - R3 - the five displaced 19-Nov items: Shenzhen
summit, PIF Tower strike, Dow close, Anthropic debut, GTA VI).
The 20-Nov day-two Anthropic verdict still prints in the index,
so the check names the debut, not the company.
"""

from PIL import Image, ImageDraw

from . import textutil as tu
from .scenes import PAINTERS
from .validate import numbering, region_counts, scope_line

CANVAS = 1024
MARGIN = 16
CONTENT_W = CANVAS - 2 * MARGIN  # 992
GUTTER = 10

KICKER_H = 26
DATE_H = 96
TIMELINE_H = 26
HERO_H = 228
HERO_SCENE_H = 140
CARD_ROWS = 2
CARD_COLS = 6
CARD_ROW_H = 160
CARD_SCENE_H = 96
BAND_H = 264
BAND_HEAD_H = 20
MAP_W = 340
DATECHECK_H = 44
FOOTER_H = 20

PAPER = (247, 243, 234)
INK = (26, 24, 22)
ACCENT = (168, 38, 32)
GREY = (74, 70, 64)
DEK_INK = (34, 32, 29)
HAIRLINE = (40, 38, 34)

DATE_CHECK_LABEL = "DATE CHECK \u2014 NOT TODAY:"
# R3: the five displaced 19-Nov items join the check (Shenzhen
# summit, PIF Tower strike, Dow close, Anthropic debut, GTA VI).
# The strip wraps to two lines at 9 px; verified in-render.
DATE_CHECK_REST = ("Voyager 1 light-day (18 Nov) \u00b7 ICJ Myanmar ruling "
                   "(19 Nov) \u00b7 Crimea Bridge strike (19 Nov) \u00b7 "
                   "Pete Rose pardon (19 Nov) \u00b7 Shenzhen summit "
                   "(19 Nov) \u00b7 PIF Tower strike (19 Nov) \u00b7 "
                   "Dow \u22121,101 close (19 Nov) \u00b7 Anthropic debut "
                   "(19 Nov) \u00b7 GTA VI $1.84bn (19 Nov)")


def _text(draw, xy, text, fnt, fill=INK):
    draw.text(xy, text, font=fnt, fill=fill)


def _number_badge(draw, x, y, num, size=9, height=13):
    fnt = tu.font(tu.SANS_BOLD, size)
    label = str(num)
    bw = max(15, tu.width_of(label, fnt) + 6)
    draw.rectangle([x, y, x + bw, y + height], fill=INK)
    _text(draw, (x + (bw - tu.width_of(label, fnt)) // 2, y + 2), label,
          fnt, fill=PAPER)
    return bw


def _fit_one_line(draw, x, y, text, path, start, floor, width, fill=INK):
    """Draw text on one line, shrinking to floor; returns (size, fits)."""
    fnt, size, fits = tu.fit_to_width(text, path, start, width, floor)
    _text(draw, (x, y), text, fnt, fill=fill)
    return size, fits


def render(content, stats):
    """Draw the whole page. Returns (PIL image, legibility warnings)."""
    warnings = []
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    draw = ImageDraw.Draw(img)
    stories = content["stories"]
    heroes = [s for s in stories if s["tier"] == "hero"]
    cards = [s for s in stories if s["tier"] == "card"]
    index = [s for s in stories if s["tier"] not in ("hero", "card")]
    nums = numbering(stories)

    y = 0
    # ---- kicker line ---------------------------------------------------
    kfnt = tu.font(tu.SANS_BOLD, 12)
    _text(draw, (MARGIN, y + 6), "ONE DAY OF WORLD NEWS, ONE PICTURE", kfnt)
    scope = scope_line(stats)
    sfnt = tu.font(tu.SANS_BOLD, 12)
    _text(draw, (CANVAS - MARGIN - tu.width_of(scope, sfnt), y + 6),
          scope, sfnt, fill=ACCENT)
    y += KICKER_H

    # ---- giant date masthead -------------------------------------------
    date_fnt, _dsize, fits = tu.fit_to_width(content["date_line"],
                                            tu.SERIF_BOLD, 56, CONTENT_W, 40)
    if not fits:
        warnings.append("date masthead does not fit at 40 px serif")
    _text(draw, (MARGIN, y + 14), content["date_line"], date_fnt)
    draw.rectangle([MARGIN, y + DATE_H - 6, CANVAS - MARGIN, y + DATE_H - 3],
                   fill=INK)
    y += DATE_H

    # ---- day-arc timeline: sequence labels only ------------------------
    # Each slot is two lines in the 26 px strip: bold sequence label
    # + story number, then a short phrase. The only time word on the
    # strip is "noon" (Akvan, wire-sourced); the validator enforces
    # that no other slot carries a clock time.
    timeline = content["timeline"]
    slot_w = CONTENT_W // len(timeline)
    for i, slot in enumerate(timeline):
        sx = MARGIN + i * slot_w
        label = slot["label"]
        phrase = slot["text"]
        num = slot["story_num"]
        lfnt = tu.font(tu.SANS_BOLD, 10)
        _text(draw, (sx, y + 1), "%s #%d" % (label, num), lfnt, fill=ACCENT)
        rfnt, _rsize, rfits = tu.fit_to_width(phrase, tu.SANS, 10,
                                              slot_w - 6, 8)
        if not rfits:
            warnings.append("timeline slot %r phrase does not fit at 8 px"
                            % label)
        _text(draw, (sx, y + 13), phrase, rfnt, fill=GREY)
        if i:
            _text(draw, (sx - 8, y + 6), "\u203a",
                  tu.font(tu.SANS_BOLD, 12), fill=GREY)
    draw.line([MARGIN, y + TIMELINE_H - 1, CANVAS - MARGIN, y + TIMELINE_H - 1],
              fill=HAIRLINE, width=1)
    y += TIMELINE_H

    # ---- hero row: 4 heroes --------------------------------------------
    hero_cell = (CONTENT_W - 3 * GUTTER) // 4
    for i, story in enumerate(heroes):
        cx = MARGIN + i * (hero_cell + GUTTER)
        cw = hero_cell if i < 3 else CONTENT_W - 3 * (hero_cell + GUTTER)
        PAINTERS[story["scene"]](draw, cx, y, cw, HERO_SCENE_H,
                                 story.get("scene_spec") or {})
        draw.rectangle([cx, y, cx + cw, y + HERO_SCENE_H], outline=HAIRLINE)
        _number_badge(draw, cx + 5, y + 5, nums[story["id"]])
        ty = y + HERO_SCENE_H + 4
        kicker = "%s \u00b7 %s" % (story["place"], story["kicker_date"])
        kfnt2, _ks, kfits = tu.fit_to_width(kicker, tu.SANS_BOLD, 10, cw, 8)
        if not kfits:
            warnings.append("hero %s kicker does not fit" % story["id"])
        _text(draw, (cx, ty), kicker, kfnt2, fill=ACCENT)
        ty += 14
        hfnt = tu.font(tu.SERIF_BOLD, 17)
        hlines = tu.wrap(story["headline"], hfnt, cw)
        for line in hlines[:2]:
            _text(draw, (cx, ty), line, hfnt)
            ty += 19
        dfnt = tu.font(tu.SANS, 12)
        dlines = tu.wrap(story["dek"], dfnt, cw)
        for line in dlines[:2]:
            _text(draw, (cx, ty), line, dfnt, fill=DEK_INK)
            ty += 14
    y += HERO_H

    # ---- card rows: 2 rows x 6 cards ------------------------------------
    cell_w = (CONTENT_W - (CARD_COLS - 1) * GUTTER) // CARD_COLS
    for row in range(CARD_ROWS):
        for col in range(CARD_COLS):
            story = cards[row * CARD_COLS + col]
            cx = MARGIN + col * (cell_w + GUTTER)
            cw = cell_w if col < CARD_COLS - 1 else CONTENT_W - col * (cell_w + GUTTER)
            PAINTERS[story["scene"]](draw, cx, y, cw, CARD_SCENE_H,
                                     story.get("scene_spec") or {})
            draw.rectangle([cx, y, cx + cw, y + CARD_SCENE_H], outline=HAIRLINE)
            ty = y + CARD_SCENE_H + 3
            bw = _number_badge(draw, cx, ty, nums[story["id"]], size=8, height=11)
            kicker = "%s \u00b7 %s" % (story["place"], story["kicker_date"])
            kfnt3, _k3, k3fits = tu.fit_to_width(kicker, tu.SANS_BOLD, 9,
                                                 cw - bw - 4, 7)
            if not k3fits:
                warnings.append("card %s kicker does not fit at 7 px"
                                % story["id"])
            _text(draw, (cx + bw + 4, ty), kicker, kfnt3, fill=ACCENT)
            ty += 13
            hfnt2 = tu.font(tu.SANS_BOLD, 13)
            hlines = tu.wrap(story["headline"], hfnt2, cw)
            for line in hlines[:2]:
                _text(draw, (cx, ty), line, hfnt2)
                ty += 14
            dsize, dfits = _fit_one_line(draw, cx, ty, story["dek"],
                                         tu.SANS, 11, 9, cw, fill=DEK_INK)
            if dsize < 10:
                warnings.append("card %s dek shrunk to %d px"
                                % (story["id"], dsize))
        y += CARD_ROW_H

    # ---- map + index band ------------------------------------------------
    head_fnt = tu.font(tu.SANS_BOLD, 12)
    _text(draw, (MARGIN, y + 4),
          "MORE OF THE DAY \u2014 %d STORIES" % len(index), head_fnt)
    note = "PINS = THE 16 ILLUSTRATED STORIES"
    note_fnt = tu.font(tu.SANS, 10)
    _text(draw, (CANVAS - MARGIN - tu.width_of(note, note_fnt), y + 5),
          note, note_fnt, fill=GREY)
    draw.line([MARGIN, y + BAND_HEAD_H - 2, CANVAS - MARGIN, y + BAND_HEAD_H - 2],
              fill=INK, width=1)
    y += BAND_HEAD_H
    body_h = BAND_H - BAND_HEAD_H
    map_spec = {
        "pins": [(nums[s["id"]], s["region"]) for s in heroes + cards],
        "dots": [],
    }
    PAINTERS["worldmap"](draw, MARGIN, y, MAP_W, body_h, map_spec)
    draw.rectangle([MARGIN, y, MARGIN + MAP_W, y + body_h], outline=HAIRLINE)
    cap_fnt = tu.font(tu.SANS_BOLD, 9)
    _text(draw, (MARGIN + 5, y + body_h - 14),
          "WHERE THE DAY HAPPENED \u00b7 APPROXIMATE", cap_fnt, fill=GREY)

    idx_x = MARGIN + MAP_W + GUTTER
    idx_w = CONTENT_W - MAP_W - GUTTER
    col_w = idx_w // 3
    rows = 10
    row_h = body_h // rows
    bfnt = tu.font(tu.SANS_BOLD, 10)
    nfnt = tu.font(tu.SANS_BOLD, 10)
    for pos, story in enumerate(index):
        col, row = divmod(pos, rows)
        ix = idx_x + col * col_w
        iy = y + row * row_h + 2
        cw2 = col_w - 6 if col < 2 else idx_w - 2 * col_w - 6
        num = "%d." % nums[story["id"]]
        nw = tu.width_of(num, nfnt)
        draw.rectangle([ix, iy, ix + nw + 5, iy + 11], fill=INK)
        _text(draw, (ix + 3, iy + 1), num, nfnt, fill=PAPER)
        blines = tu.wrap(story["brief"], bfnt, cw2 - nw - 10)
        ly = iy
        for line in blines[:2]:
            _text(draw, (ix + nw + 9, ly), line, bfnt)
            ly += 11
    y += body_h

    # ---- DATE CHECK ------------------------------------------------------
    draw.rectangle([MARGIN, y, CANVAS - MARGIN, y + DATECHECK_H - 2],
                   outline=ACCENT)
    dc_size = 11
    for _try in (11, 10, 9):
        dc_size = _try
        lab_f = tu.font(tu.SANS_BOLD, _try)
        rest_f = tu.font(tu.SANS, _try)
        full = DATE_CHECK_LABEL + " " + DATE_CHECK_REST
        if tu.width_of(full, rest_f) + tu.width_of(DATE_CHECK_LABEL, lab_f) \
                - tu.width_of(DATE_CHECK_LABEL, rest_f) <= CONTENT_W - 16:
            break
    dcl_fnt = tu.font(tu.SANS_BOLD, dc_size)
    dcr_fnt = tu.font(tu.SANS, dc_size)
    # Wrap label + rest together across at most two lines.
    words = (DATE_CHECK_LABEL + " " + DATE_CHECK_REST).split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        w_lab = tu.width_of(DATE_CHECK_LABEL, dcl_fnt) \
            + tu.width_of(trial[len(DATE_CHECK_LABEL):], dcr_fnt) \
            if trial.startswith(DATE_CHECK_LABEL) else tu.width_of(trial, dcr_fnt)
        if w_lab <= CONTENT_W - 16 or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    ly = y + 7
    for li, line in enumerate(lines[:2]):
        if line.startswith(DATE_CHECK_LABEL):
            _text(draw, (MARGIN + 6, ly), DATE_CHECK_LABEL, dcl_fnt)
            rest = line[len(DATE_CHECK_LABEL):]
            _text(draw, (MARGIN + 6 + tu.width_of(DATE_CHECK_LABEL, dcl_fnt), ly),
                  rest, dcr_fnt)
        else:
            _text(draw, (MARGIN + 6, ly), line, dcr_fnt)
        ly += dc_size + 3
    if len(lines) > 2:
        warnings.append("DATE CHECK wraps past 2 lines")
    y += DATECHECK_H

    # ---- sources footer --------------------------------------------------
    sources = []
    for story in stories:
        for src in story.get("sources") or []:
            if src not in sources:
                sources.append(src)
    src_line = "SOURCES: " + " \u00b7 ".join(sources) + " \u00b7 Drawn in code"
    sfnt2, _ss, _ = tu.fit_to_width(src_line, tu.SANS, 9, CONTENT_W, 7)
    _text(draw, (MARGIN, y + 4), src_line, sfnt2, fill=GREY)
    y += FOOTER_H

    assert y == CANVAS, "height budget sums to %d, not %d" % (y, CANVAS)
    return img, warnings
