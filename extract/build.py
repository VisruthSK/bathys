# /// script
# requires-python = ">=3.13"
# dependencies = ["fonttools==4.68.0", "brotli==1.2.1", "uharfbuzz==0.57.0", "pillow==13.0.0", "skia-pathops==0.9.2"]
# ///
"""Build fonts and proofs: uv run extract/build.py [--check] [--glyphs]."""

import argparse
import json
import unittest
from datetime import UTC, datetime
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

from outlines import DLIGS, GLYPHS, LIGS, SC_NN_GAP

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts"
SVG = ROOT / "svg"
GENERATED = ROOT / "extract/generated"


def ligature_inputs(remaining, whole, suffix):
    if not remaining:
        yield []
        return
    for piece in [remaining[0], *LIGS]:
        if remaining.startswith(piece) and piece != whole:
            for rest in ligature_inputs(remaining[len(piece) :], whole, suffix):
                yield ["_".join(piece) + suffix, *rest]


def build():
    chars = {32: "space", 160: "nbspace"}
    chars.update(
        {ord(c): c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"}
    )
    chars.update(
        {
            ord(c): n
            for c, n in zip(
                "0123456789",
                [
                    "zero",
                    "one",
                    "two",
                    "three",
                    "four",
                    "five",
                    "six",
                    "seven",
                    "eight",
                    "nine",
                ],
                strict=True,
            )
        }
    )
    chars.update(
        {
            ord(c): n
            for c, n in {
                "!": "exclam",
                "?": "question",
                ".": "period",
                ",": "comma",
                ":": "colon",
                ";": "semicolon",
                "-": "hyphen",
                "–": "endash",
                "—": "emdash",
                "'": "quotesingle",
                '"': "quotedbl",
                "/": "slash",
                "&": "ampersand",
                "(": "parenleft",
                ")": "parenright",
                "+": "plus",
                "=": "equal",
                "‘": "quoteleft",
                "’": "quoteright",
                "“": "quotedblleft",
                "”": "quotedblright",
            }.items()
        }
    )
    order = [".notdef"] + [n for n in GLYPHS if n != ".notdef"]
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(chars)
    cs = {}
    for n, (p, w) in GLYPHS.items():
        pen = T2CharStringPen(w, None, roundTolerance=1)
        p.draw(pen)
        cs[n] = pen.getCharString()
    fb.setupCFF(
        "Bathys-Regular",
        {
            "FullName": "Bathys Regular",
            "FamilyName": "Bathys",
            "Weight": "Regular",
            "version": "1.400",
        },
        cs,
        {"BlueValues": [-12, 0, 700, 712], "StdHW": 66, "StdVW": 66},
    )
    fb.setupHorizontalMetrics(
        {n: (w, round(p.bounds[0]) if len(p) else 0) for n, (p, w) in GLYPHS.items()}
    )
    fb.setupHorizontalHeader(ascent=820, descent=-180, lineGap=80)
    fb.setupNameTable(
        {
            "familyName": "Bathys",
            "styleName": "Regular",
            "uniqueFontIdentifier": "Bathys-Regular-1.400",
            "fullName": "Bathys Regular",
            "psName": "Bathys-Regular",
            "version": "Version 1.400",
            "description": "Circular display capitals, open-throated R, returning N, interlocks and a spiral S.",
        }
    )
    fb.setupOS2(
        version=4,
        sTypoAscender=820,
        sTypoDescender=-180,
        sTypoLineGap=80,
        usWinAscent=820,
        usWinDescent=180,
        sCapHeight=700,
        sxHeight=518,
        usWeightClass=400,
        fsType=0,
        fsSelection=0xC0,
    )
    fb.setupPost()
    fea = ["languagesystem DFLT dflt;", "languagesystem latn dflt;"]
    for tag, letters in [
        ("smcp", "abcdefghijklmnopqrstuvwxyz"),
        ("c2sc", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ]:
        fea.append(f"feature {tag} {{")
        for c in letters:
            fea.append(f"sub {c} by {c.upper()}.sc;")
        fea.append(f"}} {tag};")
    # Normalize capitals aliases only after the small-cap substitutions.
    fea.append("feature calt {")
    for c in "abcdefghijklmnopqrstuvwxyz":
        fea.append(f"sub {c} by {c.upper()};")
    fea.append("} calt;")
    for tag, ligs in [("liga", LIGS), ("dlig", DLIGS)]:
        fea.append(f"feature {tag} {{")
        for seq in sorted(ligs, key=len, reverse=True):
            for suffix in ["", ".sc"]:
                # Accept standard ligatures already formed earlier in the run.
                variants = (
                    list(ligature_inputs(seq, seq, suffix))
                    if tag == "dlig"
                    else [[c + suffix for c in seq]]
                )
                for variant in variants:
                    fea.append(f"sub {' '.join(variant)} by {'_'.join(seq) + suffix};")
        fea.append(f"}} {tag};")
    fea.append("feature zero { sub zero by zero.slash; } zero;")
    kerns = {
        "AV": -65,
        "AW": -48,
        "AY": -65,
        "AT": -50,
        "TA": -235,
        "VA": -255,
        "WA": -180,
        "YA": -225,
        "TO": -42,
        "OT": -42,
        "YO": -125,
        "OY": -125,
        "VO": -90,
        "OV": -90,
        "WO": -60,
        "OW": -60,
        "FA": -275,
        "PA": -295,
        "LT": -225,
        "LY": -220,
        "LV": -230,
        "LW": -160,
        "OA": -150,
        "CA": -110,
        "DA": -165,
        "GA": -150,
        "JA": -80,
        "UA": -100,
        "BA": -100,
        "RA": -50,
        "TS": -185,
        "YS": -200,
        "VS": -140,
        "WS": -95,
        "FS": -60,
        "PS": -70,
        "ES": -60,
        "KS": -50,
        "LS": -60,
        "RS": -55,
        "XS": -90,
        "ZS": -60,
        "SA": -105,
        "SV": -80,
        "SW": -70,
        "SX": -100,
        "SY": -95,
        "ST": -60,
        "PJ": -260,
        "FJ": -180,
        "YJ": -180,
        "VJ": -180,
        "TJ": -175,
        "DX": -160,
        "DT": -145,
        "DY": -140,
        "DZ": -130,
        "CX": -100,
        "GX": -145,
        "OX": -145,
        "XC": -145,
        "XG": -145,
        "XO": -145,
        "XQ": -145,
        "LC": -130,
        "LG": -130,
        "LO": -130,
        "LQ": -130,
        "CY": -80,
        "GY": -125,
        "QY": -135,
        "QT": -130,
        "YC": -125,
        "YG": -125,
        "YQ": -125,
        "VC": -90,
        "VG": -90,
        "VQ": -90,
        "CV": -50,
        "GV": -90,
        "WC": -60,
        "WG": -60,
        "WQ": -60,
        "CW": -25,
        "GW": -60,
        "AE": -60,
        "NN": -40,
        "IN": -40,
        "NE": -40,
        "RI": -6,
        "IL": -45,
        "LE": -40,
        "EY": -65,
    }
    fea.append("feature kern {")
    # Every ligature inherits the spacing of its outside letters.
    edges = {c: (c, c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    edges.update({"_".join(seq): (seq[0], seq[-1]) for seq in LIGS | DLIGS})
    pairs = {
        (left, right): v
        for pair, v in kerns.items()
        for left, (_, end) in edges.items()
        if end == pair[0]
        for right, (start, _) in edges.items()
        if start == pair[1]
    }
    for left, right, value in [
        ("C_O_R", "I", -12),
        ("B_A", "I", -55),
        ("R_A", "E", -60),
        ("I", "N_N", -40),
        ("N_N", "E", -40),
    ]:
        pairs[left, right] = value
    for (left, right), value in sorted(pairs.items()):
        fea.extend(
            [
                f"pos {left} {right} {value};",
                f"pos {left}.sc {right}.sc {round(value * 0.74)};",
            ]
        )
    fea.append("} kern;")
    fea.append("table GDEF {")
    for sequence, (positions, _width) in (LIGS | DLIGS).items():
        # Midpoints between neighbouring letter origins yield editable carets.
        carets = [
            round((positions[i] + positions[i + 1]) / 2 + GLYPHS[sequence[i]][1] / 2)
            for i in range(len(sequence) - 1)
        ]
        for suffix, scale in [("", 1), (".sc", 0.74)]:
            gap = SC_NN_GAP / 2 if suffix and sequence == "NN" else 0
            values = " ".join(str(round(c * scale + gap)) for c in carets)
            fea.append(f"LigatureCaretByPos {'_'.join(sequence) + suffix} {values};")
    fea.append("} GDEF;")
    feature_text = "\n".join(fea)
    (GENERATED / "Bathys.fea").write_text(feature_text)
    addOpenTypeFeaturesFromString(fb.font, feature_text)
    fb.font["head"].fontRevision = 1.4
    fb.font["head"].created = fb.font["head"].modified = (
        int(datetime(2026, 11, 9, tzinfo=UTC).timestamp()) + 2082844800
    )
    fb.font.recalcTimestamp = False
    fb.save(OUT / "Bathys-Regular.otf")
    web = TTFont(OUT / "Bathys-Regular.otf", recalcTimestamp=False)
    web.flavor = "woff2"
    web.save(OUT / "Bathys-Regular.woff2")
    from variable import variable_font

    variable_font(fb.font, OUT)
    return order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--glyphs", action="store_true")
    args = parser.parse_args()
    for directory in [OUT, SVG, GENERATED]:
        directory.mkdir(parents=True, exist_ok=True)
    order = build()
    from specimen import proofs, render

    proofs(order)
    render()
    if args.glyphs:
        target = GENERATED / "glyphs"
        target.mkdir(exist_ok=True)
        for name, (outline, width) in GLYPHS.items():
            if not len(outline):
                continue
            pen = SVGPathPen(None)
            outline.draw(pen)
            filename = "lower-" + name if len(name) == 1 and name.islower() else name
            (target / f"{filename}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -820 {width + 40} 1100"><path transform="scale(1,-1)" d="{pen.getCommands()}"/></svg>'
            )
    (GENERATED / "glyph-data.json").write_text(
        json.dumps(
            {
                "glyphs": {
                    n: {"advance": w, "bounds": list(p.bounds) if len(p) else None}
                    for n, (p, w) in GLYPHS.items()
                },
                "ligatures": list(LIGS),
                "discretionary": list(DLIGS),
            },
            indent=2,
        )
    )
    print(f"Built {len(GLYPHS)} glyphs and visual proofs.")
    if args.check:
        suite = unittest.defaultTestLoader.discover(
            str(Path(__file__).parent), pattern="test_font.py"
        )
        if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
            raise SystemExit(1)


if __name__ == "__main__":
    main()
