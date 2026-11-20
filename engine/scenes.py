"""Scene painters: one small flat-colour illustration per story.

Every painter receives the page image, a draw handle, its box
``(x, y, w, h)`` (the box corners are ``(x, y)`` and ``(x + w, y + h)``
in PIL rectangle terms), the story dict and its 1-based number.  Each
painter fills its own background, draws the scene, and the shared
frame / number badge / label chip furniture is applied by
``paint_scene`` so no painter can spill outside its box.
"""

import math

from . import palette
from .textkit import font, ink_box

CHIP_SIDE = {
    "cyclone": "right",
    "rescue": "right",
    "nato": "right",
    "cricket": "left",
    "chip": "left",
    "football": "left",
    "hippo": "right",
    "factory": "left",
}

SEA = (44, 92, 128)
SEA_PALE = (170, 196, 214)
CLOUD = (226, 232, 236)
COAST = (62, 104, 70)
SURF = (200, 225, 235)


def _rect(draw, box, fill=None, outline=None, width=1):
    draw.rectangle(box, fill=fill, outline=outline, width=width)


def paint_cyclone(img, draw, box, story, num):
    """Cyclone Akvan: concentric elliptical spiral arms over a coast."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    cx = x + 301
    cy = y + 69
    # twelve spiral arms, 20 px apart, each a 210-degree arc whose
    # start rotates 65 degrees per arm; colours alternate cloud/pale
    for k in range(12):
        rx = 235 - 20 * k
        ry = min(max(int(rx * 0.26), 4), 60)
        start = (65 * k) % 360
        draw.arc([cx - rx, cy - ry, cx + rx, cy + ry], start,
                 start + 210, fill=CLOUD if k % 2 == 0 else SEA_PALE,
                 width=6)
    # dark eye inside a thin cloud ring
    draw.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=(30, 60, 92))
    draw.ellipse([cx - 9, cy - 7, cx + 9, cy + 7],
                 outline=CLOUD, width=2)
    # three rain streaks upper right, slanting down towards the eye
    for i in range(3):
        sx = x + 471 + 46 * i
        draw.line([sx, y + 6, sx + 20, y + 40], fill=(190, 210, 226),
                  width=2)
    # coastline: the green land band follows a stepped shore profile
    # (each vertex starts a plateau of that height), with a pale surf
    # line one pixel above the land in every column
    shore = [(1, 115), (14, 116), (27, 117), (41, 118), (54, 119),
             (68, 120), (81, 121), (82, 120), (94, 119), (105, 118),
             (117, 117), (129, 116), (141, 115), (152, 114),
             (164, 113), (184, 112), (205, 111), (225, 110),
             (255, 111), (266, 112), (276, 113), (286, 114),
             (296, 115), (307, 116), (317, 117), (327, 118),
             (368, 119), (409, 120), (410, 119), (420, 118),
             (430, 117), (441, 116), (451, 115), (461, 114),
             (471, 113), (482, 112), (583, 113), (594, 114),
             (604, 115), (614, 116), (624, 117), (635, 118),
             (645, 119), (654, 119)]
    tops = {}
    for i, (vx, vy) in enumerate(shore):
        nxt = shore[i + 1][0] if i + 1 < len(shore) else w
        for lx in range(vx, nxt):
            tops[lx] = vy
    pts = [(x, y + h), (x, y + tops[1])]
    pts += [(x + lx, y + tops[lx]) for lx in range(1, w)]
    pts.append((x + w, y + h))
    draw.polygon(pts, fill=COAST)
    for lx in range(1, w):
        draw.point((x + lx, y + tops[lx] - 1), fill=CLOUD)
    # the surf wash spills one pixel past the left edge of the box,
    # a short pale column where the shore profile starts
    draw.rectangle([x - 1, y + 113, x - 1, y + 117], fill=CLOUD)
    # a second, fainter foam line breaks above the surf where the
    # swell peaks (measured runs, one pixel above the surf line)
    foam = [
        (108, [(245, 245)]), (109, [(255, 255)]),
        (110, [(204, 204), (491, 563), (567, 573)]),
        (111, [(276, 276), (481, 481), (583, 583)]),
        (112, [(163, 163), (286, 286)]),
        (113, [(296, 296), (604, 604)]),
        (114, [(140, 140), (614, 614)]),
        (115, [(27, 27), (128, 128), (317, 317), (624, 624)]),
        (116, [(116, 116), (327, 327)]),
        (117, [(54, 54), (104, 104), (368, 368), (645, 645),
               (654, 654)]),
        (118, [(93, 93)]), (119, [(81, 81)]),
    ]
    for ry, runs in foam:
        for rx0, rx1 in runs:
            draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                           fill=CLOUD)
    # three wave arcs offshore
    for wx in (x + 103, x + 248, x + 392):
        draw.arc([wx, y + 103, wx + 28, y + 113], 180, 360, fill=SURF,
                 width=2)
    # one palm at lower right: fronds and a leftward-drifting trunk,
    # as measured row runs
    palm = [
        (91, [(561, 561, "F"), (569, 570, "F")]),
        (92, [(560, 562, "F"), (569, 570, "F")]),
        (93, [(561, 563, "F"), (568, 569, "F")]),
        (94, [(562, 564, "F"), (568, 569, "F"), (578, 578, "F")]),
        (95, [(555, 555, "F"), (563, 565, "F"), (567, 568, "F"),
              (575, 578, "F")]),
        (96, [(555, 561, "F"), (564, 568, "F"), (573, 575, "F")]),
        (97, [(561, 567, "F"), (570, 572, "F")]),
        (98, [(566, 570, "F")]),
        (99, [(566, 566, "T"), (567, 567, "F"), (568, 568, "T")]),
        (100, [(566, 568, "T")]), (101, [(566, 568, "T")]),
        (102, [(565, 567, "T")]), (103, [(565, 567, "T")]),
        (104, [(565, 567, "T")]), (105, [(565, 567, "T")]),
        (106, [(565, 567, "T")]), (107, [(565, 567, "T")]),
        (108, [(564, 566, "T")]), (109, [(564, 566, "T")]),
        (110, [(564, 566, "T")]), (111, [(564, 566, "T")]),
        (112, [(564, 566, "T")]), (113, [(564, 566, "T")]),
        (114, [(564, 566, "T")]), (115, [(563, 565, "T")]),
        (116, [(563, 565, "T")]), (117, [(563, 565, "T")]),
        (118, [(563, 565, "T")]), (119, [(563, 565, "T")]),
        (120, [(563, 565, "T")]), (121, [(562, 564, "T")]),
        (122, [(562, 564, "T")]), (123, [(562, 564, "T")]),
        (124, [(562, 564, "T")]),
    ]
    for ry, runs in palm:
        for rx0, rx1, code in runs:
            draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                           fill=(90, 64, 40) if code == "T"
                           else (52, 116, 56))


def paint_summit_side(img, draw, box, story, num):
    """Summit signing: three delegates at a long desk under their
    flags, nameplates on the desk front, papers and hands between
    the first two as the deal is signed."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(104, 110, 128))
    draw.rectangle([x, y + 80, x + w, y + 83], fill=(84, 90, 106))
    # the long desk
    draw.rectangle([x + 9, y + 83, x + 317, y + 86], fill=(140, 104, 62))
    draw.rectangle([x + 9, y + 87, x + 317, y + 133], fill=(96, 66, 40))
    spec = story.get("scene_spec") or {}
    # flags: two EU blue with gold star circles, one Union Jack
    for fx in (34, 139):
        draw.rectangle([x + fx, y + 6, x + fx + 49, y + 32],
                       fill=(0, 51, 153))
        for k in range(12):
            ang = math.radians(30 * k)
            sx = int(fx + 24 + 8 * math.cos(ang))
            sy = int(19 + 7.5 * math.sin(ang))
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                draw.point((x + sx + dx, y + sy + dy), fill=(255, 204, 0))
    ux, uy = x + 244, y + 6
    draw.rectangle([ux, uy, ux + 49, uy + 26], fill=(0, 36, 125))
    diag_tl = [(0, 0), (2, 0), (4, 1), (6, 2), (8, 3), (9, 4), (11, 5),
               (13, 6), (15, 7), (17, 8), (19, 9), (21, 10), (17, 10),
               (15, 9), (13, 8), (11, 7), (9, 6), (8, 5), (6, 4),
               (4, 3), (2, 2), (0, 1)]
    for sx, sy in ((0, 0), (49, 0), (0, 26), (49, 26)):
        pts = []
        for px, py in diag_tl:
            qx = px if sx == 0 else 49 - px
            qy = py if sy == 0 else 26 - py
            pts.append((ux + qx, uy + qy))
        draw.polygon(pts, fill=(240, 240, 240))
    draw.rectangle([ux + 22, uy, ux + 27, uy + 26], fill=(240, 240, 240))
    draw.rectangle([ux, uy + 11, ux + 49, uy + 16], fill=(240, 240, 240))
    draw.rectangle([ux + 24, uy, ux + 25, uy + 26], fill=(200, 16, 46))
    draw.rectangle([ux, uy + 13, ux + 49, uy + 14], fill=(200, 16, 46))
    for px, py in ((0, -1), (49, -1), (0, 27), (49, 27)):
        draw.point((ux + px, uy + py), fill=(240, 240, 240))
    # delegation chips under the flags
    for cx, tag in ((38, "EU"), (143, "EU"), (248, "UK")):
        tw = 23 if tag == "EU" else 25
        draw.rectangle([x + cx, y + 35, x + cx + tw, y + 51],
                       fill=(20, 20, 24))
        draw.text((x + cx + 5, y + 38), tag,
                  font=font(palette.SANS_BOLD, 9), fill=(245, 242, 235))
    # three delegates: same hair and face shapes, palette swapped
    hair_poly = [(55, 49), (61, 49), (63, 50), (64, 51), (70, 52),
                 (70, 65), (66, 65), (66, 60), (47, 60), (47, 58),
                 (48, 57), (48, 55), (49, 54), (50, 53), (51, 52),
                 (52, 51), (53, 50)]
    face_poly = [(47, 61), (65, 61), (65, 65), (68, 66), (67, 67),
                 (66, 68), (66, 69), (63, 70), (52, 70), (50, 69),
                 (50, 68), (49, 67), (47, 66), (45, 65), (43, 64),
                 (44, 63), (46, 62)]
    hairs = spec.get("hair") or [(212, 192, 132), (178, 178, 178),
                                 (96, 90, 84)]
    suits = [(30, 34, 52), (52, 40, 40), (28, 44, 84)]
    for i in range(3):
        ox = i * 105
        draw.polygon([(x + ox + px, y + py) for px, py in hair_poly],
                     fill=tuple(hairs[i]))
        draw.polygon([(x + ox + px, y + py) for px, py in face_poly],
                     fill=(232, 192, 158))
        draw.rectangle([x + ox + 41, y + 71, x + ox + 75, y + 83],
                       fill=suits[i])
        shirt_bot = 77 if i == 1 else 79
        draw.rectangle([x + ox + 54, y + 71, x + ox + 62, y + shirt_bot],
                       fill=(240, 238, 230))
    # the first delegate's arm reaches across to the papers
    draw.rectangle([x + 71, y + 78, x + 118, y + 81], fill=suits[0])
    # gooseneck microphones for the outer two (row runs, measured)
    mic1 = [(70, 64, 66), (71, 63, 67), (72, 62, 68), (73, 62, 68),
            (74, 62, 68), (75, 63, 67), (76, 64, 68), (77, 67, 69),
            (78, 68, 70), (79, 69, 71), (80, 70, 71), (81, 71, 71),
            (82, 73, 74), (83, 73, 73)]
    mic3 = [(70, 274, 276), (71, 273, 277), (72, 272, 278),
            (73, 272, 278), (74, 272, 278), (75, 273, 277),
            (76, 274, 278), (77, 277, 279), (78, 278, 280),
            (79, 279, 281), (80, 280, 282), (81, 281, 283),
            (82, 282, 284), (83, 283, 283)]
    for runs in (mic1, mic3):
        for ry, rx0, rx1 in runs:
            draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                           fill=(16, 16, 18))
    # papers, hands and the middle microphone: measured row runs
    cluster = [
        (70, [(169, 171, "M")]),
        (71, [(168, 172, "M")]),
        (72, [(167, 173, "M")]),
        (73, [(167, 173, "M")]),
        (74, [(122, 126, "O"), (167, 173, "M"), (180, 184, "O")]),
        (75, [(117, 120, "P"), (121, 121, "O"), (122, 126, "F"),
              (127, 127, "O"), (128, 145, "P"), (168, 172, "M"),
              (179, 179, "O"), (180, 184, "T"), (185, 185, "O"),
              (186, 189, "P")]),
        (76, [(117, 119, "P"), (120, 120, "O"), (121, 127, "F"),
              (128, 128, "O"), (129, 145, "P"), (169, 173, "M"),
              (178, 178, "O"), (179, 185, "T"), (186, 186, "O"),
              (187, 189, "P")]),
        (77, [(117, 118, "P"), (119, 119, "O"), (120, 128, "F"),
              (129, 129, "O"), (130, 145, "P"), (172, 174, "M"),
              (177, 177, "O"), (178, 180, "T"), (182, 186, "T"),
              (187, 187, "O"), (188, 189, "P")]),
        (78, [(119, 119, "O"), (120, 128, "F"), (129, 129, "O"),
              (177, 177, "O"), (178, 179, "T"), (183, 186, "T"),
              (187, 187, "O"), (188, 189, "P")]),
        (79, [(119, 119, "O"), (120, 128, "F"), (129, 129, "O"),
              (130, 145, "P"), (177, 177, "O"), (178, 180, "T"),
              (184, 186, "T"), (187, 187, "O"), (188, 189, "P")]),
        (80, [(119, 119, "O"), (120, 128, "F"), (129, 129, "O"),
              (130, 145, "P"), (177, 177, "O"), (178, 181, "T"),
              (186, 186, "T"), (187, 187, "O"), (188, 189, "P")]),
        (81, [(119, 119, "O"), (120, 128, "F"), (129, 129, "O"),
              (177, 177, "O"), (178, 183, "T"), (187, 187, "O"),
              (188, 189, "P")]),
        (82, [(117, 119, "P"), (120, 120, "O"), (121, 127, "F"),
              (128, 128, "O"), (129, 145, "P"), (177, 177, "M"),
              (178, 178, "O"), (179, 184, "T"), (188, 189, "P")]),
        (83, [(117, 120, "P"), (121, 121, "O"), (122, 126, "F"),
              (127, 127, "O"), (128, 145, "P"), (178, 178, "M"),
              (179, 179, "O"), (180, 184, "T"), (185, 185, "O"),
              (187, 189, "P")]),
        (84, [(122, 126, "O"), (180, 184, "O")]),
    ]
    # grey edges of the paper stack, and the pen in the second hand
    for ry in (78, 81):
        draw.rectangle([x + 130, y + ry, x + 145, y + ry],
                       fill=(150, 148, 140))
    pen = [(77, 181, 181), (78, 180, 182), (79, 181, 183),
           (80, 182, 185), (81, 184, 186), (82, 185, 187),
           (83, 186, 186)]
    for ry, rx0, rx1 in pen:
        draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                       fill=(20, 20, 24))
    inks = {"P": (246, 244, 238), "T": (206, 164, 124),
            "O": (128, 90, 58), "F": (232, 192, 158), "M": (16, 16, 18)}
    for ry, runs in cluster:
        for rx0, rx1, code in runs:
            draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                           fill=inks[code])
    # nameplates on the desk front
    names = spec.get("names") or ["VON DER LEYEN", "COSTA", "BURNHAM"]
    for (px, tx) in ((13, 18), (142, 147), (237, 242)):
        pw = {0: 90, 1: 42, 2: 62}[(px // 100) if px < 200 else 2] \
            if False else (90 if px == 13 else 42 if px == 142 else 62)
        draw.rectangle([x + px, y + 93, x + px + pw, y + 108],
                       fill=(238, 232, 216))
        draw.text((x + tx, y + 96), names[(0 if px == 13 else
                                           1 if px == 142 else 2)],
                  font=font(palette.SANS_BOLD, 9), fill=(30, 28, 26))


def paint_rescue(img, draw, box, story, num):
    """Night rescue: a boat with a searchlight, a waving crewman,
    a life ring and a small dinghy on a swell."""
    x, y, w, h = box
    SKY = (34, 48, 76)
    SEAC = (26, 66, 96)
    ORANGE = (220, 110, 40)
    WHITE = (240, 238, 230)
    WAVE = (180, 205, 225)
    SKIN = (232, 192, 158)
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.rectangle([x, y + 57, x + w, y + 60], fill=(120, 150, 180))
    draw.rectangle([x, y + 61, x + w, y + h], fill=SEAC)
    # stars: small pale squares, one larger sparkle
    for sx, sy in ((22, 22), (28, 39), (35, 28), (35, 40),
                   (54, 19), (61, 29), (67, 7), (73, 5), (98, 40),
                   (113, 33)):
        draw.rectangle([x + sx, y + sy, x + sx + 1, y + sy + 1],
                       fill=(200, 205, 220))
    draw.rectangle([x + 43, y + 16, x + 44, y + 17], fill=(200, 205, 220))
    draw.rectangle([x + 42, y + 18, x + 43, y + 19], fill=(200, 205, 220))
    # hull with a white waterline stripe (cabin and crew stand on it)
    draw.polygon([(x + 12, y + 68), (x + 77, y + 68), (x + 69, y + 82),
                  (x + 20, y + 82)], fill=ORANGE)
    draw.rectangle([x + 16, y + 72, x + 73, y + 76], fill=WHITE)
    # searchlight: pole, lamp, then the beam fanning out over both
    draw.rectangle([x + 68, y + 32, x + 69, y + 68], fill=(220, 220, 220))
    draw.ellipse([x + 65, y + 28, x + 73, y + 36], fill=(255, 240, 170))
    draw.polygon([(x + 69, y + 32), (x + 95, y + 24), (x + 99, y + 23),
                  (x + 142, y + 23), (x + 143, y + 24), (x + 144, y + 28)],
                 fill=(240, 220, 150))
    # cabin with two windows
    draw.rectangle([x + 31, y + 48, x + 65, y + 68], fill=WHITE)
    draw.rectangle([x + 36, y + 53, x + 42, y + 60], fill=(30, 60, 90))
    draw.rectangle([x + 46, y + 53, x + 50, y + 60], fill=(30, 60, 90))
    # crewman: hair, face, life vest over a white shirt, raised arm
    draw.polygon([(x + 60, y + 41), (x + 64, y + 41), (x + 66, y + 43),
                  (x + 67, y + 46), (x + 57, y + 46), (x + 58, y + 43)],
                 fill=(30, 26, 22))
    draw.polygon([(x + 57, y + 47), (x + 67, y + 47), (x + 67, y + 49),
                  (x + 66, y + 50), (x + 58, y + 50), (x + 57, y + 49)],
                 fill=SKIN)
    draw.rectangle([x + 51, y + 51, x + 59, y + 65], fill=ORANGE)
    draw.rectangle([x + 65, y + 51, x + 73, y + 65], fill=ORANGE)
    draw.rectangle([x + 51, y + 53, x + 73, y + 53], fill=ORANGE)
    draw.rectangle([x + 60, y + 54, x + 64, y + 65], fill=WHITE)
    draw.polygon([(x + 61, y + 54), (x + 63, y + 54), (x + 62, y + 57)],
                 fill=ORANGE)
    draw.line([x + 82, y + 38, x + 72, y + 54], fill=SKIN, width=3)
    # life ring
    draw.ellipse([x + 88, y + 85, x + 106, y + 103], fill=(240, 120, 40))
    draw.ellipse([x + 92, y + 89, x + 102, y + 99], fill=SEAC)
    # dinghy with a thin mast
    draw.polygon([(x + 125, y + 85), (x + 151, y + 85), (x + 147, y + 92),
                  (x + 129, y + 92), (x + 126, y + 87)], fill=(40, 44, 54))
    draw.rectangle([x + 144, y + 75, x + 145, y + 85],
                   fill=(200, 200, 200))
    # rows of wave arcs over everything afloat
    for wy in (71, 87, 99):
        for cx in (19, 61, 103, 145):
            draw.arc([x + cx - 11, y + wy, x + cx + 11, y + wy + 8],
                     180, 360, fill=WAVE, width=2)


def paint_nato(img, draw, box, story, num):
    """Alliance summit: a white four-point star over a speaker at a
    lectern, with a row of member flags along the bottom."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(28, 44, 92))
    draw.rectangle([x, y, x + w, y + 15], fill=(20, 34, 74))
    # four-point compass star
    cx, cy = x + 78, y + 39
    draw.polygon([(cx, y + 11), (cx + 7, y + 32), (cx + 28, cy),
                  (cx + 7, y + 46), (cx, y + 67), (cx - 7, y + 46),
                  (cx - 28, cy), (cx - 7, y + 32)], fill=(238, 238, 230))
    # speaker: hair cap, face, suit with shirt and tie
    draw.polygon([(x + 76, y + 62), (x + 80, y + 62), (x + 84, y + 66),
                  (x + 84, y + 68), (x + 72, y + 68), (x + 72, y + 66)],
                 fill=(60, 56, 52))
    draw.polygon([(x + 72, y + 69), (x + 84, y + 69), (x + 84, y + 71),
                  (x + 82, y + 73), (x + 74, y + 73), (x + 72, y + 71)],
                 fill=(232, 192, 158))
    draw.rectangle([x + 67, y + 74, x + 75, y + 85], fill=(34, 38, 60))
    draw.rectangle([x + 81, y + 74, x + 89, y + 85], fill=(34, 38, 60))
    draw.rectangle([x + 76, y + 74, x + 80, y + 84], fill=(240, 238, 230))
    draw.polygon([(x + 76, y + 76), (x + 80, y + 76), (x + 78, y + 81)],
                 fill=(160, 36, 36))
    # lectern in two tones
    draw.rectangle([x + 58, y + 85, x + 98, y + 90], fill=(96, 72, 46))
    draw.rectangle([x + 58, y + 91, x + 98, y + 98], fill=(70, 50, 34))
    # row of member flags
    flags = [(178, 44, 52), (240, 240, 240), (178, 44, 52),
             (150, 60, 110), (178, 44, 52), (150, 60, 110),
             (52, 84, 168), (240, 240, 240), (52, 84, 168),
             (240, 240, 240), (52, 84, 168), (240, 240, 240)]
    for i, col in enumerate(flags):
        fx = x + 4 + i * 12
        draw.rectangle([fx, y + 100, fx + 9, y + 108], fill=col)


def paint_cop31_plenary(img, draw, box, story, num):
    """Plenary hall from behind the delegates: a big screen carrying
    the draft's figure cut, the speaker at the podium, four heads."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(36, 64, 56))
    # banner and side panels in the hall's deep green
    draw.rectangle([x + 43, y + 3, x + 113, y + 16], fill=(24, 60, 44))
    draw.text((x + 58, y + 5), "COP31", font=font(palette.SANS_BOLD, 11),
              fill=(244, 196, 84))
    draw.rectangle([x + 3, y + 17, x + 12, y + 60], fill=(24, 60, 44))
    draw.rectangle([x + 144, y + 17, x + 153, y + 60], fill=(24, 60, 44))
    # the screen and its message
    draw.rectangle([x + 21, y + 20, x + 135, y + 57], fill=(20, 20, 20))
    draw.rectangle([x + 23, y + 22, x + 133, y + 55],
                   fill=(240, 238, 228))
    draw.text((x + 50, y + 30), "144\u219280",
              font=font(palette.SANS_BOLD, 13), fill=(168, 38, 32))
    # speaker at the podium, in front of the screen's lower edge
    draw.polygon([(x + 77, y + 40), (x + 79, y + 40), (x + 80, y + 41),
                  (x + 81, y + 42), (x + 82, y + 43), (x + 82, y + 44),
                  (x + 74, y + 44), (x + 74, y + 43), (x + 75, y + 42),
                  (x + 76, y + 41)], fill=(60, 56, 52))
    draw.polygon([(x + 74, y + 45), (x + 82, y + 45), (x + 82, y + 46),
                  (x + 81, y + 47), (x + 75, y + 47), (x + 74, y + 46)],
                 fill=(232, 192, 158))
    draw.rectangle([x + 71, y + 48, x + 85, y + 57], fill=(34, 38, 60))
    draw.rectangle([x + 76, y + 48, x + 80, y + 57],
                   fill=(240, 238, 230))
    draw.rectangle([x + 76, y + 50, x + 80, y + 50], fill=(160, 36, 36))
    draw.rectangle([x + 77, y + 51, x + 79, y + 51], fill=(160, 36, 36))
    draw.rectangle([x + 78, y + 52, x + 78, y + 52], fill=(160, 36, 36))
    draw.rectangle([x + 65, y + 59, x + 91, y + 61], fill=(96, 72, 46))
    draw.rectangle([x + 65, y + 62, x + 91, y + 76], fill=(70, 50, 34))
    # rail between the stage and the delegates
    draw.rectangle([x, y + 77, x + w, y + 79], fill=(20, 40, 34))
    # four delegates from behind: round heads over broad shoulders
    delegates = [(6, (30, 28, 26), (52, 58, 74), -5, 35),
                 (47, (60, 44, 30), (84, 60, 52), 36, 76),
                 (91, (200, 200, 200), (66, 52, 76), 80, 120),
                 (132, (18, 18, 18), (44, 66, 58), 121, 161)]
    for hx, hair, suit, sx0, sx1 in delegates:
        draw.rectangle([x + sx0, y + 99, x + sx1, y + 110], fill=suit)
        draw.ellipse([x + hx, y + 83, x + hx + 18, y + 101], fill=hair)


def paint_cricket(img, draw, box, story, num):
    """Outfield and a pale pitch strip: the batsman from behind in the
    middle, the bowler in blue at the right, a stepped boundary rope
    sagging along the bottom edge."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(74, 140, 74))
    draw.rectangle([x, y, x + w, y + 33], fill=(120, 170, 120))
    draw.rectangle([x + 53, y + 33, x + 103, y + h], fill=(214, 196, 150))
    # boundary rope treads are drawn at the very end, over everything
    # batsman from behind: cap, neck, broad white shirt
    draw.polygon([(x + 66, y + 45), (x + 72, y + 45), (x + 74, y + 46),
                  (x + 75, y + 47), (x + 78, y + 50), (x + 78, y + 52),
                  (x + 79, y + 53), (x + 79, y + 55), (x + 59, y + 55),
                  (x + 59, y + 53), (x + 60, y + 52), (x + 60, y + 50),
                  (x + 63, y + 47), (x + 64, y + 46)], fill=(28, 28, 30))
    draw.polygon([(x + 59, y + 56), (x + 79, y + 56), (x + 79, y + 59),
                  (x + 78, y + 61), (x + 77, y + 62), (x + 75, y + 64),
                  (x + 63, y + 64), (x + 61, y + 62), (x + 60, y + 61),
                  (x + 59, y + 59)], fill=(198, 150, 110))
    draw.rectangle([x + 51, y + 65, x + 87, y + 89], fill=(238, 238, 234))
    draw.rectangle([x + 65, y + 65, x + 73, y + 89], fill=(240, 238, 230))
    # a tapering notch cut into the shirt front
    draw.rectangle([x + 67, y + 67, x + 71, y + 69], fill=(238, 238, 234))
    draw.rectangle([x + 68, y + 70, x + 70, y + 73], fill=(238, 238, 234))
    draw.rectangle([x + 69, y + 74, x + 69, y + 76], fill=(238, 238, 234))
    # three stump tops peeking below the shirt
    for sx in (72, 77, 82):
        draw.rectangle([x + sx, y + 90, x + sx + 2, y + 90],
                       fill=(240, 220, 140))
    # his arm reaches down to the bat, row by row; the ball sits past it
    arm_rows = [(70, 85, 85), (71, 84, 86), (72, 82, 87), (73, 83, 87),
                (74, 84, 88), (75, 84, 89), (76, 85, 90), (77, 86, 90),
                (78, 87, 91), (79, 87, 92), (80, 88, 93), (81, 89, 94),
                (82, 90, 94), (83, 91, 95), (84, 91, 96), (85, 92, 97),
                (86, 93, 98), (87, 94, 98), (88, 95, 99), (89, 95, 100),
                (90, 96, 101), (91, 97, 99), (92, 98, 98), (93, 98, 98)]
    for ry, rx0, rx1 in arm_rows:
        draw.rectangle([x + rx0, y + ry, x + rx1, y + ry],
                       fill=(232, 192, 158))
    draw.polygon([(x + 100, y + 90), (x + 103, y + 93), (x + 105, y + 94),
                  (x + 106, y + 95), (x + 107, y + 96), (x + 108, y + 97),
                  (x + 110, y + 99), (x + 112, y + 100), (x + 112, y + 101),
                  (x + 112, y + 103), (x + 113, y + 104),
                  (x + 112, y + 106), (x + 111, y + 105),
                  (x + 109, y + 103), (x + 107, y + 102),
                  (x + 105, y + 100), (x + 103, y + 98),
                  (x + 100, y + 96), (x + 98, y + 94), (x + 99, y + 92)],
                 fill=(190, 160, 110))
    draw.ellipse([x + 113, y + 99, x + 119, y + 105], fill=(200, 40, 36))
    # bowler in blue: hair, face, body, shirt front with a band
    draw.polygon([(x + 133, y + 62), (x + 137, y + 62), (x + 140, y + 65),
                  (x + 141, y + 66), (x + 141, y + 68), (x + 129, y + 68),
                  (x + 129, y + 66), (x + 130, y + 65)],
                 fill=(30, 26, 22))
    draw.polygon([(x + 129, y + 69), (x + 141, y + 69), (x + 141, y + 71),
                  (x + 140, y + 72), (x + 139, y + 73), (x + 131, y + 73),
                  (x + 130, y + 72), (x + 129, y + 71)],
                 fill=(232, 192, 158))
    draw.rectangle([x + 123, y + 74, x + 147, y + 90], fill=(30, 90, 160))
    draw.rectangle([x + 133, y + 74, x + 137, y + 90],
                   fill=(240, 238, 230))
    draw.rectangle([x + 131, y + 76, x + 139, y + 77], fill=(30, 90, 160))
    draw.rectangle([x + 134, y + 78, x + 136, y + 79], fill=(30, 90, 160))
    draw.rectangle([x + 135, y + 80, x + 135, y + 81], fill=(30, 90, 160))
    # boundary rope: two stair-stepped runs of flat treads, drawn last
    treads = [(95, 53, 53), (96, 49, 53), (97, 45, 49), (98, 41, 45),
              (99, 38, 41), (100, 34, 38), (101, 31, 34), (102, 25, 31),
              (103, 18, 25), (104, 12, 18), (105, 2, 12), (106, 2, 2),
              (96, 103, 103), (97, 103, 107), (98, 107, 111),
              (99, 111, 115), (100, 115, 118), (101, 118, 122),
              (102, 122, 125), (103, 125, 131), (104, 131, 138),
              (105, 138, 144), (106, 144, 155), (107, 155, 155)]
    for ty, tx0, tx1 in treads:
        draw.rectangle([x + tx0, y + ty, x + tx1, y + ty],
                       fill=(240, 240, 230))


def paint_sco(img, draw, box, story, num):
    """Sandstone hall: a cream-rimmed arch with a green SCO banner,
    hanging lanterns, a speaker at a lectern and four listeners."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(186, 148, 104))
    # lanterns on cords, either side of the arch
    for lx in (18, 124):
        draw.rectangle([x + lx + 7, y + 8, x + lx + 8, y + 23],
                       fill=(60, 48, 36))
        draw.rectangle([x + lx, y + 24, x + lx + 14, y + 41],
                       outline=(120, 80, 30), width=1)
        draw.rectangle([x + lx + 1, y + 25, x + lx + 13, y + 40],
                       fill=(244, 176, 60))
        draw.rectangle([x + lx + 1, y + 33, x + lx + 13, y + 33],
                       fill=(120, 80, 30))
    # arch: cream shell, dark interior (ellipse crowns on straight legs)
    draw.rectangle([x + 40, y + 35, x + 116, y + 79], fill=(240, 232, 210))
    crown_out = [(71, 11), (66, 12), (63, 13), (60, 14), (58, 15),
                 (56, 16), (55, 17), (53, 18), (52, 19), (51, 20),
                 (50, 21), (49, 22), (48, 23), (47, 24), (46, 25),
                 (46, 26), (45, 27), (45, 28), (44, 29), (44, 30),
                 (43, 31), (43, 32), (43, 33), (43, 34), (113, 34),
                 (113, 33), (113, 32), (113, 31), (112, 30), (112, 29),
                 (111, 28), (111, 27), (110, 26), (110, 25), (109, 24),
                 (108, 23), (107, 22), (106, 21), (105, 20), (104, 19),
                 (103, 18), (101, 17), (100, 16), (98, 15), (96, 14),
                 (93, 13), (90, 12), (85, 11)]
    draw.polygon([(x + px, y + py) for px, py in crown_out],
                 fill=(240, 232, 210))
    draw.rectangle([x + 47, y + 35, x + 109, y + 79], fill=(52, 44, 40))
    crown_in = [(72, 14), (67, 15), (63, 16), (61, 17), (59, 18),
                (57, 19), (55, 20), (54, 21), (52, 22), (51, 23),
                (50, 24), (50, 25), (49, 26), (48, 27), (48, 28),
                (47, 29), (47, 30), (47, 31), (46, 32), (46, 33),
                (46, 34), (110, 34), (110, 33), (110, 32), (109, 31),
                (109, 30), (109, 29), (108, 28), (108, 27), (107, 26),
                (106, 25), (106, 24), (105, 23), (104, 22), (102, 21),
                (101, 20), (99, 19), (97, 18), (95, 17), (93, 16),
                (89, 15), (84, 14)]
    draw.polygon([(x + px, y + py) for px, py in crown_in],
                 fill=(52, 44, 40))
    # banner with the forum initials
    draw.rectangle([x + 62, y + 22, x + 94, y + 40], fill=(24, 60, 44))
    draw.text((x + 66, y + 25), "SCO", font=font(palette.SANS_BOLD, 11),
              fill=(244, 196, 84))
    # speaker: hair, face, suit, shirt, papers on the lectern
    draw.polygon([(x + 76, y + 47), (x + 80, y + 47), (x + 82, y + 49),
                  (x + 83, y + 50), (x + 84, y + 51), (x + 84, y + 53),
                  (x + 72, y + 53), (x + 72, y + 51), (x + 73, y + 50),
                  (x + 74, y + 49)], fill=(20, 18, 16))
    draw.polygon([(x + 72, y + 54), (x + 84, y + 54), (x + 84, y + 56),
                  (x + 83, y + 57), (x + 82, y + 58), (x + 74, y + 58),
                  (x + 73, y + 57), (x + 72, y + 56)],
                 fill=(198, 150, 110))
    draw.rectangle([x + 67, y + 59, x + 89, y + 74], fill=(44, 66, 58))
    draw.rectangle([x + 76, y + 59, x + 80, y + 68],
                   fill=(240, 238, 230))
    draw.polygon([(x + 77, y + 68), (x + 79, y + 68), (x + 85, y + 70),
                  (x + 88, y + 71), (x + 90, y + 72), (x + 88, y + 73),
                  (x + 86, y + 74), (x + 84, y + 75), (x + 81, y + 76),
                  (x + 75, y + 76), (x + 73, y + 75), (x + 70, y + 74),
                  (x + 68, y + 73), (x + 66, y + 72), (x + 68, y + 71),
                  (x + 71, y + 70), (x + 74, y + 69)],
                 fill=(120, 110, 96))
    draw.polygon([(x + 77, y + 69), (x + 79, y + 69), (x + 88, y + 72),
                  (x + 86, y + 73), (x + 84, y + 74), (x + 81, y + 75),
                  (x + 75, y + 75), (x + 73, y + 74), (x + 70, y + 73),
                  (x + 68, y + 72), (x + 71, y + 71), (x + 74, y + 70)],
                 fill=(246, 244, 238))
    draw.rectangle([x + 76, y + 74, x + 80, y + 88], fill=(70, 54, 36))
    # four listeners: same head shape, different hair and suits
    heads = [(7, (30, 28, 26), (52, 58, 74), 1),
             (42, (120, 90, 60), (84, 60, 52), 36),
             (104, (200, 200, 200), (66, 52, 76), 98),
             (139, (60, 44, 30), (58, 62, 50), 133)]
    for hx, hair, suit, sx in heads:
        draw.polygon([(x + hx + 3, y + 82), (x + hx + 7, y + 82),
                      (x + hx + 8, y + 83), (x + hx + 9, y + 84),
                      (x + hx + 10, y + 86), (x + hx + 10, y + 87),
                      (x + hx, y + 87), (x + hx, y + 86),
                      (x + hx + 1, y + 84), (x + hx + 2, y + 83)],
                     fill=hair)
        draw.polygon([(x + hx, y + 88), (x + hx + 10, y + 88),
                      (x + hx + 10, y + 90), (x + hx + 9, y + 91),
                      (x + hx + 1, y + 91), (x + hx, y + 90)],
                     fill=(232, 192, 158))
        draw.rectangle([x + sx, y + 92, x + sx + 22, y + 106], fill=suit)
        draw.rectangle([x + sx + 9, y + 92, x + sx + 13, y + 106],
                       fill=(240, 238, 230))


def paint_ballot(img, draw, box, story, num):
    """Senate chamber: the presiding officer above three bench rows
    of round heads, some with a hand raised in the vote."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(96, 74, 54))
    draw.rectangle([x, y, x + w, y + 33], fill=(120, 94, 66))
    draw.rectangle([x + 143, y + 4, x + 153, y + 22], fill=(20, 20, 24))
    # presiding officer: hair, face, suit, shirt, tie, podium
    draw.polygon([(x + 76, y + 10), (x + 80, y + 10), (x + 82, y + 12),
                  (x + 83, y + 13), (x + 84, y + 14), (x + 84, y + 16),
                  (x + 72, y + 16), (x + 72, y + 14), (x + 73, y + 13),
                  (x + 74, y + 12)], fill=(40, 36, 32))
    draw.polygon([(x + 72, y + 17), (x + 84, y + 17), (x + 84, y + 19),
                  (x + 83, y + 20), (x + 82, y + 21), (x + 74, y + 21),
                  (x + 73, y + 20), (x + 72, y + 19)],
                 fill=(232, 192, 158))
    draw.rectangle([x + 62, y + 33, x + 94, y + 57], fill=(70, 50, 34))
    draw.rectangle([x + 67, y + 22, x + 89, y + 37], fill=(34, 38, 60))
    draw.rectangle([x + 76, y + 22, x + 80, y + 37],
                   fill=(240, 238, 230))
    draw.rectangle([x + 76, y + 24, x + 80, y + 25], fill=(160, 36, 36))
    draw.rectangle([x + 77, y + 26, x + 79, y + 27], fill=(160, 36, 36))
    draw.rectangle([x + 78, y + 28, x + 78, y + 29], fill=(160, 36, 36))
    # bench fronts
    for by in (71, 87, 102):
        draw.rectangle([x + 6, y + by, x + 151, y + by + 5],
                       fill=(70, 50, 34))
    # three rows of heads on a fixed grid; a hand rises beside some
    grid = (8, 25, 41, 58, 74, 90, 107, 123, 140)
    hands = {59: (0, 1, 2, 3, 4, 5, 6, 7, 8),
             75: (3, 6),
             90: (0, 1, 3, 5, 6)}
    for hy in (59, 75, 90):
        for k, gx in enumerate(grid):
            draw.ellipse([x + gx, y + hy, x + gx + 8, y + hy + 8],
                         fill=(222, 182, 148))
            if k in hands[hy]:
                draw.line([(x + gx + 14, y + hy - 4),
                           (x + gx + 9, y + hy + 10)],
                          fill=(222, 182, 148), width=3)


def paint_chip(img, draw, box, story, num):
    """Clean-room scene: a glowing wafer on a stand, a suited worker
    reaching to it, and a dotted status panel."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(36, 44, 56))
    # ceiling rods
    for rx in range(8, w, 26):
        draw.rectangle([x + rx, y + 4, x + rx + 1, y + 33],
                       fill=(70, 84, 100))
    # wafer: two discs and two etched rings, on a post
    draw.ellipse([x + 41, y + 31, x + 93, y + 83], fill=(90, 220, 230))
    draw.ellipse([x + 49, y + 39, x + 85, y + 75], fill=(160, 245, 250))
    draw.ellipse([x + 55, y + 45, x + 79, y + 69], outline=(60, 160, 175))
    draw.ellipse([x + 61, y + 51, x + 73, y + 63], outline=(60, 160, 175))
    draw.rectangle([x + 63, y + 83, x + 71, y + 102], fill=(110, 120, 130))
    # worker: helmet, then body and the arm reaching to the wafer
    draw.ellipse([x + 147, y + 17, x + 169, y + 39], fill=(238, 240, 242))
    draw.rectangle([x + 144, y + 39, x + 172, y + 104],
                   fill=(232, 234, 236))
    draw.rectangle([x + 91, y + 48, x + 143, y + 53],
                   fill=(232, 234, 236))
    draw.rectangle([x + 150, y + 24, x + 166, y + 30], fill=(70, 90, 110))
    # status panel with glowing dots
    draw.rectangle([x + 206, y + 22, x + 230, y + 60],
                   outline=(120, 140, 150))
    draw.rectangle([x + 207, y + 23, x + 229, y + 59], fill=(52, 66, 84))
    for dx, dy in ((215, 39), (223, 37), (227, 38), (225, 45),
                   (222, 56), (226, 55)):
        draw.rectangle([x + dx, y + dy, x + dx + 2, y + dy + 2],
                       fill=(120, 230, 200))


def paint_football(img, draw, box, story, num):
    """Pitch from the side: goal with net and a diving keeper at the
    back, halfway line, centre circle, a player in red in front."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(64, 132, 64))
    # halfway line and the nearer half in a deeper green
    draw.rectangle([x, y + 68, x + w, y + 69], fill=(240, 240, 240))
    draw.rectangle([x, y + 70, x + w, y + h], fill=(56, 118, 56))
    # goal: white frame, then the net grid over it
    draw.rectangle([x + 81, y + 19, x + 158, y + 21], fill=(240, 240, 240))
    draw.rectangle([x + 81, y + 48, x + 158, y + 50], fill=(240, 240, 240))
    draw.rectangle([x + 81, y + 22, x + 83, y + 47], fill=(240, 240, 240))
    draw.rectangle([x + 156, y + 22, x + 158, y + 47], fill=(240, 240, 240))
    for vx in range(87, 158, 10):
        draw.rectangle([x + vx, y + 19, x + vx, y + 50],
                       fill=(220, 220, 220))
    for hy in (25, 33, 41, 49):
        draw.rectangle([x + 81, y + hy, x + 158, y + hy],
                       fill=(220, 220, 220))
    # diving keeper in yellow, dark shorts block in front
    draw.polygon([(x + 98, y + 36), (x + 102, y + 36), (x + 104, y + 37),
                  (x + 106, y + 39), (x + 107, y + 41), (x + 107, y + 52),
                  (x + 84, y + 52), (x + 84, y + 40), (x + 94, y + 39),
                  (x + 96, y + 37)], fill=(240, 200, 60))
    draw.rectangle([x + 102, y + 44, x + 116, y + 54], fill=(30, 30, 34))
    # the ball, resting inside the goal's right corner
    draw.ellipse([x + 134, y + 43, x + 144, y + 53],
                 fill=(245, 245, 245), outline=(30, 30, 30))
    draw.ellipse([x + 137, y + 46, x + 141, y + 50], fill=(30, 30, 30))
    # centre circle in the near half
    draw.ellipse([x + 91, y + 74, x + 148, y + 103],
                 outline=(240, 240, 240), width=2)
    # player in a red strip: cap, face, blazer, shirt, tie, arm
    draw.polygon([(x + 170, y + 56), (x + 174, y + 56), (x + 176, y + 57),
                  (x + 178, y + 59), (x + 179, y + 61), (x + 179, y + 63),
                  (x + 165, y + 63), (x + 165, y + 61), (x + 166, y + 59),
                  (x + 168, y + 57)], fill=(20, 18, 16))
    draw.polygon([(x + 165, y + 64), (x + 179, y + 64), (x + 179, y + 66),
                  (x + 178, y + 67), (x + 178, y + 68), (x + 177, y + 69),
                  (x + 167, y + 69), (x + 166, y + 68), (x + 166, y + 67),
                  (x + 165, y + 66)], fill=(198, 150, 110))
    draw.rectangle([x + 158, y + 70, x + 186, y + 88], fill=(178, 40, 40))
    draw.rectangle([x + 169, y + 70, x + 175, y + 88],
                   fill=(240, 238, 230))
    draw.polygon([(x + 170, y + 72), (x + 174, y + 72), (x + 173, y + 76),
                  (x + 172, y + 78), (x + 171, y + 76)],
                 fill=(178, 40, 40))
    draw.line([(x + 182, y + 79), (x + 196, y + 88)],
              fill=(198, 150, 110), width=4)


def paint_hippo(img, draw, box, story, num):
    """Hippo in a pool: fence and wall behind, the animal's head and
    back above the waterline, a red buoy floating nearby."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(72, 130, 168))
    draw.rectangle([x, y, x + w, y + 23], fill=(196, 214, 190))
    draw.rectangle([x, y + 24, x + w, y + 32], fill=(120, 130, 110))
    for px in range(8, w, 22):
        draw.rectangle([x + px, y + 11, x + px + 1, y + 32],
                       fill=(70, 70, 66))
    # body and head ellipses, snout, ears, eyes and nostrils
    draw.ellipse([x + 58, y + 46, x + 162, y + 94], fill=(140, 132, 128))
    draw.ellipse([x + 44, y + 56, x + 102, y + 90], fill=(150, 142, 138))
    draw.ellipse([x + 38, y + 70, x + 76, y + 88], fill=(160, 152, 148))
    for ex in (47, 67):
        draw.ellipse([x + ex, y + 48, x + ex + 10, y + 58],
                     fill=(140, 132, 128), outline=(90, 84, 80))
    for ex in (51, 67):
        draw.ellipse([x + ex, y + 60, x + ex + 6, y + 66],
                     fill=(24, 22, 20))
    for ex in (46, 62):
        draw.ellipse([x + ex, y + 74, x + ex + 6, y + 80],
                     fill=(40, 36, 32))
    # wake: two widening ripples under the body
    draw.arc([x + 42, y + 62, x + 178, y + 98], 0, 180,
             fill=(200, 225, 235), width=2)
    draw.arc([x + 52, y + 62, x + 168, y + 98], 0, 180,
             fill=(200, 225, 235), width=2)
    # buoy: red cone, dark base, white lamp on top
    draw.polygon([(x + 184, y + 69), (x + 200, y + 69), (x + 204, y + 79),
                  (x + 180, y + 79)], fill=(178, 40, 40))
    draw.rectangle([x + 180, y + 79, x + 204, y + 83], fill=(140, 28, 28))
    draw.ellipse([x + 189, y + 65, x + 195, y + 71], fill=(240, 240, 240))


def paint_factory(img, draw, box, story, num):
    """Arms factory: sawtooth roof, twin chimneys with smoke puffs,
    a row of lit windows and a worker with a crate."""
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=(140, 152, 164))
    draw.rectangle([x, y + 38, x + w, y + 89], fill=(168, 178, 186))
    draw.rectangle([x, y + 90, x + w, y + h], fill=(110, 106, 98))
    # chimneys, each with a three-puff smoke stack
    for cx0 in (38, 72):
        draw.rectangle([x + cx0, y + 11, x + cx0 + 10, y + 45],
                       fill=(120, 60, 50))
        draw.ellipse([x + cx0 + 2, y + 8, x + cx0 + 8, y + 14],
                     fill=(168, 160, 150))
        draw.ellipse([x + cx0 + 5, y + 5, x + cx0 + 9, y + 9],
                     fill=(188, 180, 170))
        draw.ellipse([x + cx0 + 2, y + 2, x + cx0 + 6, y + 6],
                     fill=(205, 198, 188))
    # walls, then the sawtooth roof strip over their top
    draw.rectangle([x + 24, y + 46, x + 222, y + 90], fill=(96, 104, 116))
    draw.polygon([(x + 24, y + 46), (x + 48, y + 32), (x + 73, y + 46),
                  (x + 97, y + 32), (x + 122, y + 46), (x + 146, y + 32),
                  (x + 171, y + 46), (x + 195, y + 32), (x + 220, y + 46)],
                 fill=(80, 88, 100))
    # lit windows and the loading door
    for k in range(9):
        wx = x + 32 + k * 20
        draw.rectangle([wx, y + 58, wx + 12, y + 70], fill=(240, 200, 110))
    draw.rectangle([x + 106, y + 76, x + 135, y + 90], fill=(40, 42, 48))
    # worker in a blue jacket with a tie, crate beside him
    draw.polygon([(x + 167, y + 55), (x + 171, y + 55), (x + 175, y + 59),
                  (x + 175, y + 61), (x + 163, y + 61), (x + 163, y + 59)],
                 fill=(30, 26, 22))
    draw.polygon([(x + 163, y + 62), (x + 175, y + 62), (x + 175, y + 64),
                  (x + 173, y + 66), (x + 165, y + 66), (x + 163, y + 64)],
                 fill=(198, 150, 110))
    draw.rectangle([x + 157, y + 67, x + 181, y + 83], fill=(52, 84, 130))
    draw.rectangle([x + 167, y + 67, x + 171, y + 83],
                   fill=(240, 238, 230))
    draw.rectangle([x + 167, y + 69, x + 171, y + 70], fill=(52, 84, 130))
    draw.polygon([(x + 168, y + 71), (x + 170, y + 71), (x + 169, y + 74)],
                 fill=(52, 84, 130))
    draw.rectangle([x + 183, y + 82, x + 195, y + 89], fill=(140, 90, 40))


PAINTERS = {
    "cyclone": paint_cyclone,
    "summit_side": paint_summit_side,
    "rescue": paint_rescue,
    "nato": paint_nato,
    "cop31_plenary": paint_cop31_plenary,
    "cricket": paint_cricket,
    "sco": paint_sco,
    "ballot": paint_ballot,
    "chip": paint_chip,
    "football": paint_football,
    "hippo": paint_hippo,
    "factory": paint_factory,
}


def _label_chip(draw, box, label, side="right", hero=False):
    """Black chip inside the scene's top corner carrying a label.

    The chip hugs the corner named by ``side``; its width follows the
    label's ink box, and the label sits at a fixed inset.
    """
    x, y, w, h = box
    fnt = font(palette.SANS_BOLD, 11)
    bb = ink_box(draw, label, fnt)
    chip_w = bb[2] + 10
    if side == "right":
        cx1 = x + w - 4
        cx0 = cx1 - chip_w
    else:
        cx0 = x + 4
        cx1 = cx0 + chip_w
    cy0 = y + 4
    draw.rectangle([cx0, cy0, cx1, cy0 + 18], fill=palette.CHIP_FILL)
    draw.text((cx0 + 5, cy0 + 3), label, font=fnt, fill=(245, 242, 235))
    return cx0, cy0, cx1, cy0 + 18


def _number_badge(draw, box, num):
    """Ink badge (16x14) with the story number, inside the top-left."""
    x, y, w, h = box
    draw.rectangle([x + 5, y + 5, x + 20, y + 18], fill=palette.INK)
    label = str(num)
    fnt = font(palette.SANS_BOLD, 9)
    bb = ink_box(draw, label, fnt)
    draw.text((x + 9, y + 7), label, font=fnt, fill=palette.PAPER)


def paint_scene(img, draw, box, story):
    """Paint one illustrated story: scene, frame, badge, chip.

    The painter draws straight onto the page inside its box; the
    frame is stroked over the top afterwards, so a painter may
    deliberately bleed a shape under the frame line.
    """
    painter = PAINTERS[story["scene"]]
    x, y, w, h = box
    painter(img, draw, box, story, story["num"])
    draw.rectangle([x, y, x + w, y + h], outline=palette.FRAME, width=1)
    if story.get("tier") == "hero":
        _number_badge(draw, box, story["num"])
    label = (story.get("scene_spec") or {}).get("label")
    if label:
        side = CHIP_SIDE.get(story["scene"], "right")
        _label_chip(draw, box, label, side=side,
                    hero=story.get("tier") == "hero")
    if story["scene"] == "cricket":
        figure = next(tok for tok in story["headline"].split()
                      if "*" in tok)
        _label_chip(draw, box, figure, side="right")
