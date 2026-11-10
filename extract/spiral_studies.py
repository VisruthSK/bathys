"""Generate the retained Undertow G/Q trial without changing the font."""

import html
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

from outlines import GLYPHS, bar, difference, path, rect, union

ROOT = Path(__file__).resolve().parent.parent


def stroke(d, width=66):
    outline = path(d)
    outline.stroke(width, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 2)
    outline.convertConicsToQuads(0.1)
    return pathops.simplify(outline, fix_winding=True)


def studies():
    return {"G": GLYPHS["G"][0], "Q": GLYPHS["Q"][0]}


def main():
    drawings = studies()
    previous = {
        "G": union(
            difference(GLYPHS["O"][0], rect(374, 350, 500, 140)),
            rect(450, 312, 274, 62),
        ),
        "Q": union(GLYPHS["O"][0], bar(468, 186, 730, -66)),
    }
    previous = {
        "G": union(
            difference(GLYPHS["O"][0], rect(374, 350, 500, 140)),
            rect(450, 312, 274, 62),
        ),
        "Q": union(GLYPHS["O"][0], bar(468, 186, 730, -66)),
    }
    filename = ROOT / "fonts/Bathys-Regular.otf"
    shaper = hb.Font(hb.Face(filename.read_bytes()))
    order = TTFont(filename).getGlyphOrder()

    def text(s, x, y, size, trial=False, fill="#102b2b"):
        buffer = hb.Buffer()
        buffer.add_str(s)
        buffer.guess_segment_properties()
        hb.shape(shaper, buffer)
        out = []
        scale = size / 1000
        for info, position in zip(
            buffer.glyph_infos, buffer.glyph_positions, strict=True
        ):
            name = order[info.codepoint]
            outline = (
                drawings.get(name, GLYPHS[name][0])
                if trial
                else previous.get(name, GLYPHS[name][0])
            )
            pen = SVGPathPen(None)
            outline.draw(pen)
            out.append(
                f'<path fill="{fill}" d="{pen.getCommands()}" transform="translate({x} {y}) scale({scale} {-scale})"/>'
            )
            x += position.x_advance * scale
        return "".join(out)

    def label(s, x, y):
        return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="15" letter-spacing="2" fill="#647d71">{html.escape(s)}</text>'

    body = '<rect width="1800" height="1080" fill="#eee8d8"/>'
    body += label("BATHYS / UNDERTOW / G & Q", 65, 65)
    body += label("SELECTED GLYPHS / CURRENT WEIGHT / CLEAN JOINS", 65, 110)
    for i, (letter, word, line) in enumerate(
        [
            ("G", "GRAVITY", "GLOW / GOLD / GARDEN"),
            ("Q", "QUARTZ", "QUIET / AQUA / QUEST"),
        ]
    ):
        y = 195 + i * 400
        body += (
            label(letter, 65, y)
            + label("PREVIOUS", 430, y)
            + label("SELECTED", 1080, y)
        )
        body += text(letter, 65, y + 240, 320, True)
        body += text(word, 430, y + 160, 105, False, "#7f8e83") + text(
            word, 1080, y + 160, 105, True
        )
        body += text(line, 430, y + 270, 48, False, "#7f8e83") + text(
            line, 1080, y + 270, 48, True
        )
        body += f'<path d="M65,{y + 345} H1735" stroke="#c5c4b5"/>'
    body += label("SELECTED G AND Q / ALL REJECTED GLYPH STUDIES REMOVED", 65, 1040)
    target = ROOT / "svg/trials"
    target.mkdir(exist_ok=True)
    (target / "spirals-undertow.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1080" viewBox="0 0 1800 1080"><title>Undertow G and Q</title>{body}</svg>\n',
        encoding="utf-8",
    )
    print("Wrote the retained G/Q trial.")


if __name__ == "__main__":
    main()
