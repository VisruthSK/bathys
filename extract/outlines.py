"""Cubic outline source; 700-unit capital height."""

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pathops
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

REFERENCE = Path(__file__).resolve().parent / "reference"
GLYPHS = {}
H_CROSSBAR = "M71,205 C71,310 122,359 228,359 L390,359 C495,359 547,410 547,515"


def path(d):
    p = pathops.Path()
    parse_path(d, p.getPen())
    return p


def poly(points):
    return path("M" + " L".join(f"{x},{y}" for x, y in points) + " Z")


def rect(x, y, w, h):
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def bar(x, y, X, Y, t=66):
    dx, dy = X - x, Y - y
    length = math.hypot(dx, dy)
    a, b = -dy / length * t / 2, dx / length * t / 2
    return poly([(x + a, y + b), (X + a, Y + b), (X - a, Y - b), (x - a, y - b)])


def union(*parts):
    p = pathops.Path()
    for part in parts:
        p = pathops.op(p, part, pathops.PathOp.UNION, fix_winding=True)
    return p


def difference(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def ellipse(cx, cy, rx, ry):
    k = 0.5522847498307936
    return path(
        f"M{cx + rx},{cy} C{cx + rx},{cy + k * ry} {cx + k * rx},{cy + ry} {cx},{cy + ry} C{cx - k * rx},{cy + ry} {cx - rx},{cy + k * ry} {cx - rx},{cy} C{cx - rx},{cy - k * ry} {cx - k * rx},{cy - ry} {cx},{cy - ry} C{cx + k * rx},{cy - ry} {cx + rx},{cy - k * ry} {cx + rx},{cy} Z"
    )


def transform(p, scale=1, dx=0, dy=0):
    q = pathops.Path()
    p.draw(TransformPen(q.getPen(), (scale, 0, 0, scale, dx, dy)))
    return q


def add(name, p, width):
    GLYPHS[name] = (p, round(width))


def spiral_s():
    # Fitted outer and inner cover edges, not a stroked centreline.
    element = ET.parse(REFERENCE / "S.svg").find("{http://www.w3.org/2000/svg}path")
    outline = path(element.attrib["d"])
    scale = 700 / 42
    outline = outline.transform(scale, 0, 0, -scale, 24 - 196 * scale, 497 * scale)
    # Fit the entire spiral in the capitals' overshoot band. Compensate its
    # stroke before positioning, instead of leaving a thin, shrunken letter.
    fit = (724 - 20) / (outline.bounds[3] - outline.bounds[1])
    outline = transform(outline, fit)
    edge = transform(outline)
    edge.stroke(20, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 2)
    outline = union(outline, edge)
    return transform(outline, 1, 24 - outline.bounds[0], -12 - outline.bounds[1])


def alphabet(t=66):
    g = {}

    def put(c, p, w):
        g[c] = (p, w)

    # The asymmetric A is taken directly from the user's existing Glyphr drawing.
    source = json.loads((REFERENCE / "Bathys.gs2").read_text())
    contours = []
    for shape in source["glyphs"]["glyph-0x41"]["shapes"]:
        contours.append(
            poly(
                [
                    (
                        v["p"]["coord"]["x"] * 700 / 1480,
                        v["p"]["coord"]["y"] * 700 / 1480,
                    )
                    for v in shape["pathPoints"]
                ]
            )
        )
    put("A", difference(contours[0], contours[1]), 636)
    stem = rect(38, 0, t, 700)

    def bowl(top, bottom, right):
        mid = (top + bottom) / 2
        return path(
            f"M38,{bottom} L{right - 190},{bottom} C{right - 70},{bottom} {right},{mid - 90} {right},{mid} C{right},{mid + 90} {right - 70},{top} {right - 190},{top} L38,{top} Z"
        )

    def hollow(top, bottom, right):
        return difference(
            bowl(top, bottom, right), bowl(top - t, bottom + t, right - t)
        )

    put("B", union(stem, hollow(700, 354, 440), hollow(398, 0, 480)), 520)
    ring = difference(ellipse(374, 350, 350, 362), ellipse(374, 350, 350 - t, 362 - t))
    put("O", ring, 748)
    # The cover's C has horizontal cut ends, not radial/diagonal terminals.
    cut = rect(374, 210, 500, 280)
    C = difference(ring, cut)
    put("C", C, 707)
    # An open lower return repeats the R's open throat, without losing D's bowl.
    D = path(
        "M38,0 L38,700 L286,700 C510,700 660,560 660,350 C660,140 510,0 286,0 L166,0 L166,66 L286,66 C470,66 594,174 594,350 C594,526 470,634 286,634 L104,634 L104,0 Z"
    )
    put("D", D, 700)
    E = union(
        stem, rect(38, 700 - t, 412, t), rect(38, 326, 354, t), rect(38, 0, 412, t)
    )
    put("E", E, 482)
    put("F", union(stem, rect(38, 700 - t, 412, t), rect(38, 326, 354, t)), 475)
    G = difference(ring, rect(374, 350, 500, 140))
    g_arm = path("M724,343 L510,343 C473,343 450,321 450,286 L450,244")
    g_arm.stroke(62, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 2)
    g_arm.convertConicsToQuads(0.1)
    G = pathops.op(
        union(G, g_arm), ellipse(374, 350, 350, 362), pathops.PathOp.INTERSECTION
    )
    put("G", G, 748)
    # Subtitle H's rising crossbar, at the main capitals' stroke weight.
    # The original descender loop is intentionally omitted.
    h_bridge = path(H_CROSSBAR)
    h_bridge.stroke(t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 2)
    h_bridge.convertConicsToQuads(0.1)
    put("H", union(stem, rect(514, 0, t, 700), h_bridge), 618)
    put("I", rect(30, 0, t, 700), 126)
    J = path(
        f"M380,700 L{380 + t},700 L{380 + t},185 C{380 + t},50 345,-12 230,-12 C95,-12 24,65 24,195 L{24 + t},195 C{24 + t},105 135,{t - 12} 230,{t - 12} C325,{t - 12} 380,100 380,185 Z"
    )
    put("J", union(J, rect(220, 634, 226, 66)), 480)
    put("K", union(stem, bar(80, 296, 530, 678, t), bar(270, 464, 550, 20, t)), 590)
    put("L", union(stem, rect(38, 0, 350, t)), 417)
    put(
        "M",
        union(
            stem,
            rect(648 - t, 0, t, 700),
            poly(
                [(38, 700), (115, 700), (343, 275), (571, 700), (648, 700), (343, 145)]
            ),
        ),
        686,
    )
    plain_N = union(
        stem,
        rect(569 - t, 0, t, 700),
        poly([(38, 700), (116, 700), (569, 0), (491, 0)]),
    )
    put("N.plain", plain_N, 607)
    # The second N has a horizontal return at the TOP of the right stem.
    # The earlier baseline spur misread the cover and is deliberately absent.
    put(
        "N",
        union(
            stem,
            rect(606 - t, 0, t, 700),
            rect(354, 700 - t, 252, t),
            poly([(38, 700), (116, 700), (606, 0), (528, 0)]),
        ),
        644,
    )
    P = path(
        "M38,0 L38,700 L250,700 C409,700 503,624 503,488 C503,353 415,276 244,276 L173,276 L173,342 L244,342 C362,342 432,388 432,488 C432,582 362,629 250,629 L109,629 L109,0 Z"
    )
    put("P", P, 545)
    q_tail = path("M470,180 C520,180 555,120 590,63 C625,6 665,-32 741,-32")
    q_tail.stroke(t, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 2)
    q_tail.convertConicsToQuads(0.1)
    put("Q", union(ring, q_tail), 760)
    # Traced from the standalone R in RAE: the bowl returns into the leg,
    # leaving an open throat beside the stem. There is no middle crossbar.
    R = path(
        "M38,0 L38,700 L250,700 C409,700 503,624 503,488 C503,353 415,276 303,259 L462,0 L379,0 L173,312 L244,312 C362,312 432,376 432,488 C432,582 362,629 250,629 L109,629 L109,0 Z"
    )
    put("R", R, 536)
    S = spiral_s()
    put("S", S, round(S.bounds[2] + 24))
    put("T", union(rect(20, 634, 548, 66), rect(261, 0, 66, 700)), 588)
    U = path(
        f"M38,700 L{38 + t},700 L{38 + t},238 C{38 + t},116 175,54 302,54 C429,54 500,116 500,238 L500,700 L{500 + t},700 L{500 + t},238 C{500 + t},77 470,-12 302,-12 C134,-12 38,77 38,238 Z"
    )
    put("U", U, 604)
    put(
        "V",
        poly(
            [
                (20, 700),
                (94, 700),
                (324, 100),
                (529, 634),
                (450, 634),
                (450, 700),
                (628, 700),
                (360, 0),
                (288, 0),
            ]
        ),
        648,
    )
    put(
        "W",
        poly(
            [
                (20, 700),
                (91, 700),
                (245, 112),
                (420, 700),
                (488, 700),
                (663, 112),
                (800, 634),
                (710, 634),
                (710, 700),
                (888, 700),
                (701, 0),
                (626, 0),
                (454, 575),
                (282, 0),
                (207, 0),
            ]
        ),
        908,
    )
    put(
        "X",
        union(
            poly([(20, 700), (100, 700), (590, 0), (510, 0)]),
            poly([(510, 700), (590, 700), (100, 0), (20, 0)]),
        ),
        610,
    )
    put(
        "Y",
        union(
            poly(
                [
                    (20, 700),
                    (100, 700),
                    (285, 365),
                    (470, 700),
                    (550, 700),
                    (318, 291),
                    (252, 291),
                ]
            ),
            rect(252, 0, t, 335),
        ),
        570,
    )
    put(
        "Z",
        poly(
            [
                (30, 700),
                (567, 700),
                (567, 640),
                (113, t),
                (567, t),
                (567, 0),
                (30, 0),
                (30, 60),
                (484, 700 - t),
                (30, 700 - t),
            ]
        ),
        597,
    )
    return g


CAPITALS = alphabet()
for c, (p, w) in CAPITALS.items():
    add(c, p, w)


def smallcap(outline):
    # Expand every contour, including fixed hand-drawn curves and diagonals,
    # before shrinking. Keep the final cap line at exactly 518 units.
    edge = transform(outline)
    edge.stroke(12, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 2)
    expanded = union(outline, edge)
    expanded = expanded.transform(1, 0, 0, 700 / 712, 0, 6 * 700 / 712)
    return transform(expanded, 0.74)


for c, (p, w) in CAPITALS.items():
    add(c + ".sc", smallcap(p), w * 0.74 + 10)
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    add(c.lower(), *GLYPHS[c])
add("space", pathops.Path(), 260)
add("nbspace", pathops.Path(), 260)
add(".notdef", difference(rect(40, 0, 480, 700), rect(100, 60, 360, 580)), 560)
# Numerals follow the same round bowls and unadorned terminals.
add("zero", difference(ellipse(264, 350, 230, 362), ellipse(264, 350, 164, 298)), 528)
add("zero.slash", union(GLYPHS["zero"][0], bar(142, 130, 386, 570, 42)), 528)
add(
    "one",
    poly(
        [(70, 542), (247, 700), (303, 700), (303, 0), (237, 0), (237, 610), (112, 498)]
    ),
    397,
)
add(
    "two",
    path(
        "M42,539 C65,650 160,712 292,712 C451,712 540,632 540,518 C540,430 493,374 399,297 L143,66 L550,66 L550,0 L38,0 L38,62 L354,346 C434,412 472,457 472,519 C472,598 409,646 292,646 C195,646 134,601 108,524 Z"
    ),
    590,
)
add(
    "three",
    union(
        difference(ellipse(285, 522, 245, 190), ellipse(285, 522, 177, 124)),
        difference(ellipse(285, 180, 265, 192), ellipse(285, 180, 197, 126)),
    ),
    590,
)
GLYPHS["three"] = (difference(GLYPHS["three"][0], rect(-10, 85, 180, 520)), 590)
add(
    "four",
    union(
        poly(
            [
                (398, 700),
                (475, 700),
                (111, 236),
                (550, 236),
                (550, 170),
                (28, 170),
                (28, 233),
            ]
        ),
        rect(410, 0, 66, 700),
    ),
    590,
)
add(
    "five",
    path(
        "M528,700 L528,634 L138,634 L123,395 C171,424 232,439 297,439 C454,439 550,353 550,219 C550,79 446,-12 285,-12 C173,-12 80,30 24,111 L78,153 C128,87 198,54 286,54 C406,54 481,116 481,219 C481,316 410,373 294,373 C218,373 152,348 101,307 L50,333 L74,700 Z"
    ),
    590,
)
add(
    "six",
    union(
        difference(ellipse(300, 219, 260, 231), ellipse(300, 219, 192, 165)),
        path(
            "M40,219 C40,520 149,712 349,712 C422,712 477,693 523,663 L490,605 C451,631 406,646 349,646 C193,646 109,484 109,219 Z"
        ),
    ),
    600,
)
seven_base = poly(
    [(28, 700), (568, 700), (568, 644), (235, 0), (159, 0), (492, 634), (28, 634)]
)
seven = pathops.Path()
for component in [seven_base, rect(230, 321, 300, 58)]:
    seven.addPath(pathops.simplify(component, fix_winding=True))
add("seven", seven, 596)
add(
    "eight",
    union(
        difference(ellipse(300, 525, 240, 187), ellipse(300, 525, 172, 121)),
        difference(ellipse(300, 186, 266, 198), ellipse(300, 186, 198, 132)),
    ),
    600,
)
nine_bowl = difference(ellipse(286, 480, 244, 232), ellipse(286, 480, 176, 166))
nine_tail = path(
    "M530,480 C530,170 424,-12 240,-12 C164,-12 112,10 67,42 L101,100 C139,73 182,54 240,54 C388,54 462,220 462,480 Z"
)
add("nine", union(nine_bowl, nine_tail), 576)
for name, p, w in [
    ("period", ellipse(65, 32, 34, 34), 130),
    (
        "comma",
        poly([(35, 68), (106, 68), (100, 0), (49, -110), (16, -110), (44, 0), (35, 0)]),
        140,
    ),
    ("colon", union(ellipse(65, 32, 34, 34), ellipse(65, 443, 34, 34)), 130),
    (
        "semicolon",
        union(
            ellipse(65, 443, 34, 34),
            poly([(35, 68), (106, 68), (100, 0), (49, -110), (16, -110), (44, 0)]),
        ),
        140,
    ),
    ("hyphen", rect(35, 310, 240, 58), 310),
    ("endash", rect(35, 310, 480, 58), 550),
    ("emdash", rect(35, 310, 760, 58), 830),
    ("quotesingle", rect(40, 532, 55, 168), 135),
    ("quotedbl", union(rect(35, 532, 55, 168), rect(150, 532, 55, 168)), 240),
    ("slash", bar(45, -20, 390, 720, 60), 435),
    ("exclam", union(rect(45, 190, 64, 510), ellipse(77, 32, 34, 34)), 154),
    (
        "question",
        path(
            "M28,541 C42,653 129,712 247,712 C381,712 463,640 463,532 C463,445 414,401 347,354 C277,305 254,272 254,190 L188,190 C188,302 221,348 307,408 C367,451 395,480 395,533 C395,603 341,646 246,646 C159,646 108,607 95,530 Z"
        ),
        500,
    ),
    (
        "ampersand",
        path(
            "M525,0 L440,0 L145,341 C80,412 53,462 53,530 C53,637 135,712 250,712 C365,712 442,642 442,543 C442,452 383,395 267,330 L167,273 C106,237 78,204 78,157 C78,93 132,54 213,54 C353,54 450,183 479,354 L545,343 C508,126 388,-12 211,-12 C90,-12 10,51 10,153 C10,226 48,278 134,327 L237,386 C333,440 375,484 375,543 C375,604 327,646 251,646 C173,646 120,600 120,534 C120,486 145,446 197,388 Z"
        ),
        580,
    ),
    (
        "parenleft",
        path(
            "M240,760 C145,652 93,511 93,350 C93,189 145,48 240,-60 L162,-60 C73,47 27,191 27,350 C27,509 73,653 162,760 Z"
        ),
        280,
    ),
]:
    add(name, p, w)
add("parenright", transform(GLYPHS["parenleft"][0], -1, 280, 700), 280)
add("plus", union(rect(40, 315, 400, 60), rect(210, 145, 60, 400)), 480)
add("equal", union(rect(40, 230, 400, 60), rect(40, 410, 400, 60)), 480)
add("question", union(GLYPHS["question"][0], ellipse(221, 32, 34, 34)), 500)
for name, target in [
    ("quoteleft", "quotesingle"),
    ("quoteright", "quotesingle"),
    ("quotedblleft", "quotedbl"),
    ("quotedblright", "quotedbl"),
]:
    add(name, *GLYPHS[target])

# Interlocking positions are drawn compositions, with their intersections united.
LIGS = {
    "BA": ([0, 180], 816),
    "NN": ([0, 543], 1187),
    "EY": ([0, 417], 987),
    "FY": ([0, 417], 987),
    "TH": ([0, 464], 1082),
    "TE": ([0, 445], 927),
    "TR": ([0, 459], 995),
    "TU": ([0, 464], 1068),
    "TW": ([0, 477], 1385),
}
DLIGS = {
    "CO": ([0, 355], 1080),
    "OR": ([0, 465], 1001),
    "COR": ([0, 355, 820], 1356),
    "RA": ([0, 235], 871),
    "OO": ([0, 545], 1293),
    "OC": ([0, 545], 1252),
    "OG": ([0, 520], 1268),
    "LA": ([0, 325], 961),
    "AE": ([0, 469], 951),
    "AR": ([0, 469], 1005),
    "AT": ([0, 515], 1103),
    "HE": ([0, 476], 958),
    "NE": ([0, 502], 984),
    "COO": ([0, 355, 900], 1648),
    "ET": ([0, 420], 1008),
    "FT": ([0, 420], 1008),
    "AY": ([0, 515], 1085),
    "NY": ([0, 538], 1108),
    "LY": ([0, 90], 660),
}
# Clear cap-bar and foot joins are normal; dense monograms remain optional.
for clear_join in ("LA", "AT", "ET", "FT", "AY", "RA", "AR", "AE"):
    LIGS[clear_join] = DLIGS.pop(clear_join)
SC_NN_GAP = 9
for seq, (positions, width) in (LIGS | DLIGS).items():
    for suffix, scale in [("", 1), (".sc", 0.74)]:
        gap = SC_NN_GAP if suffix and seq == "NN" else 0
        parts = [
            transform(
                GLYPHS[("N.plain" if seq == "NN" and i == 0 else c) + suffix][0],
                1,
                (round(x * scale) if seq == "BA" else x * scale) + (gap if i else 0),
            )
            for i, (c, x) in enumerate(zip(seq, positions, strict=True))
        ]
        if seq == "BA":
            # Preserve every A coordinate: translate its contours verbatim.
            # Consistent winding gives the same fill as a union, without
            # re-fitting or rounding new intersections along A's diagonal.
            outline = pathops.Path()
            for part in parts:
                outline.addPath(part)
        else:
            outline = union(*parts)
        if seq in {"EY", "FY"}:
            # Continue the full depth of E/F's top bar into the sloping Y.
            # A simple overlap only connects at the cap line and leaves a notch.
            bridge = rect(438, 634, 38, 66)
            outline = union(outline, smallcap(bridge) if suffix else bridge)
        add(
            "_".join(seq) + suffix, outline, width * scale + gap + (10 if suffix else 0)
        )


# One glyph per character in multi-join runs. Advances encode existing joins.
JOIN_FORMS = {}
for suffix in ["", ".sc"]:
    for letter in sorted(set("".join(LIGS))):
        name = f"{letter}.chain{suffix}"
        add(name, *GLYPHS[letter + suffix])
        JOIN_FORMS[name] = {"base": letter, "target": None, "suffix": suffix}
    for left, right in LIGS:
        pair = left + right
        name = f"{left}.join_{right}{suffix}"
        source = "N.plain" if pair == "NN" else left
        outline = GLYPHS[source + suffix][0]
        if pair in {"EY", "FY"}:
            bridge = rect(438, 634, 38, 66)
            outline = union(outline, smallcap(bridge) if suffix else bridge)
        advance = GLYPHS["_".join(pair) + suffix][1] - GLYPHS[right + suffix][1]
        add(name, outline, advance)
        JOIN_FORMS[name] = {"base": left, "target": right, "suffix": suffix}
