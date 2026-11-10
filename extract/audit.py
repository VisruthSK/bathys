"""Inspect the distributed font's contours and all capital-pair ink gaps."""

import json
import math
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent


def audit():
    filename = ROOT / "fonts/Bathys-Regular.otf"
    font = TTFont(filename)
    glyphs = font.getGlyphSet()
    order = font.getGlyphOrder()
    shaper = hb.Font(hb.Face(filename.read_bytes()))
    issues = []
    rows = {}
    outlines = {}
    for name in order:
        outline = pathops.Path()
        glyphs[name].draw(outline.getPen())
        outlines[name] = outline
        for contour in outline.contours:
            if abs(contour.area) < 1:
                issues.append({"glyph": name, "tiny_contour_area": contour.area})
        pen = RecordingPen()
        glyphs[name].draw(pen)
        previous = None
        for command, points in pen.value:
            if command == "lineTo" and points[0] == previous:
                issues.append({"glyph": name, "zero_length_line": points[0]})
            if points:
                previous = points[-1]
        if len(name) != 1 or not name.isupper():
            continue
        x0, _, x1, _ = outline.bounds
        left = range(math.floor(x0), math.ceil(x1) + 1, 2)
        right = range(math.ceil(x1), math.floor(x0) - 1, -2)
        rows[name] = {}
        for y in range(10, 700, 10):
            start = next((x for x in left if outline.contains((x, y))), None)
            end = next((x for x in right if outline.contains((x, y))), None)
            if start is not None:
                rows[name][y] = start, end
    pairs = {}
    collisions = {}
    smallcap_collisions = {}
    for left in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for right in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            buffer = hb.Buffer()
            buffer.add_str(left + right)
            buffer.guess_segment_properties()
            hb.shape(shaper, buffer, {"liga": False, "calt": False, "dlig": False})
            advance = buffer.glyph_positions[0].x_advance
            gaps = [
                advance + rows[right][y][0] - rows[left][y][1]
                for y in rows[left].keys() & rows[right].keys()
            ]
            pairs[left + right] = {
                "minimum_ink_gap": min(gaps),
                "mean_row_gap": round(sum(gaps) / len(gaps), 1),
            }
            for small, target in [(False, collisions), (True, smallcap_collisions)]:
                shaped = hb.Buffer()
                shaped.add_str(left + right)
                shaped.guess_segment_properties()
                hb.shape(
                    shaper,
                    shaped,
                    {"liga": False, "calt": False, "dlig": False, "c2sc": small},
                )
                names = [order[info.codepoint] for info in shaped.glyph_infos]
                placed = outlines[names[1]].transform(
                    1, 0, 0, 1, shaped.glyph_positions[0].x_advance, 0
                )
                area = abs(
                    pathops.op(
                        outlines[names[0]], placed, pathops.PathOp.INTERSECTION
                    ).area
                )
                if area > 0.01 and left + right != "EY":
                    target[left + right] = round(area, 3)
    result = {
        "glyphs": len(order),
        "outline_issues": issues,
        "unintended_collisions": collisions,
        "smallcap_collisions": smallcap_collisions,
        "pairs": pairs,
    }
    target = ROOT / "extract/generated/audit.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Inspected {len(order)} glyphs and {len(pairs)} capital pairs.")
    print("Outline issues:", issues)
    print(
        "Tightest pairs:",
        sorted(pairs.items(), key=lambda item: item[1]["minimum_ink_gap"])[:12],
    )
    print(
        "Pairs before A:",
        {
            pair: pairs[pair]
            for pair in ["HA", "OA", "TA", "YA", "FA", "PA", "VA", "WA"]
        },
    )
    assert not issues, issues
    assert not collisions, collisions
    assert not smallcap_collisions, smallcap_collisions


if __name__ == "__main__":
    audit()
