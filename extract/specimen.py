"""Outlined specimens and a raster proof of the compiled OTF."""

import base64
import html
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from outlines import DLIGS, GLYPHS, LIGS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts"
SVG = ROOT / "svg"
order = []


def shape(text, features=None):
    font = hb.Font(hb.Face((OUT / "Bathys-Regular.otf").read_bytes()))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    return [
        (order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
        for i, p in zip(buf.glyph_infos, buf.glyph_positions, strict=True)
    ]


def svg_text(text, x, y, size, fill, features=None):
    result = []
    scale = size / 1000
    for name, advance, dx, dy in shape(text, features):
        pen = SVGPathPen(None)
        GLYPHS[name][0].draw(pen)
        result.append(
            f'<path fill="{fill}" d="{pen.getCommands()}" transform="translate({x + dx * scale:.3f} {y - dy * scale:.3f}) scale({scale} {-scale})"/>'
        )
        x += advance * scale
    return "".join(result)


def label(text, x, y):
    return f'<text x="{x}" y="{y}" fill="#9eafa8" font-family="sans-serif" font-size="12" letter-spacing="2">{html.escape(text)}</text>'


def write_svg(name, body, w, h):
    (SVG / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>Bathys — {html.escape(name)}</title>{body}</svg>',
        encoding="utf-8",
    )


def proofs(glyph_order):
    global order
    order = glyph_order
    body = '<rect width="1400" height="1800" fill="#0d2425"/><circle cx="1190" cy="300" r="350" fill="none" stroke="#39504a"/><circle cx="1190" cy="300" r="285" fill="none" stroke="#39504a"/>'
    body += label("BATHYS / A STUDY IN CIRCLES, SPACE & SOUND", 80, 70)
    body += svg_text("BATHYS", 70, 305, 240, "#eee6cf")
    body += label("01 / THE REFERENCE LETTERING", 80, 390)
    for s, y in [("CORINNE", 600), ("BAILEY", 792), ("RAE", 984)]:
        body += svg_text(s, 78, y, 250, "#eee6cf")
    body += svg_text(
        "THE SEA / THE LOVE EP", 85, 1070, 46, "#d5ac72", {"smcp": True, "c2sc": True}
    )
    body += label("02 / AFTER THE LAST LIGHT", 80, 1190)
    for s, y in [("WE ORBIT", 1325), ("THE SAME SUN.", 1440)]:
        body += svg_text(s, 80, y, 132, "#eee6cf")
    body += svg_text(
        "and carry the sea into the stars", 85, 1555, 49, "#d5ac72", {"smcp": True}
    )
    body += label(
        "CUBIC OUTLINES / INTERLOCKING LIGATURES / OPTICAL SMALL CAPITALS", 80, 1700
    )
    write_svg("Bathys-poster.svg", body, 1400, 1800)
    body = '<rect width="1400" height="1600" fill="#f4eedf"/>'
    body += label("BATHYS / COMPLETE CHARACTER & SPACING PROOF", 65, 55)
    for row, y in [
        ("ABCDEFG", 200),
        ("HIJKLMN", 350),
        ("OPQRSTU", 500),
        ("VWXYZ", 650),
        ("0123456789", 800),
    ]:
        body += svg_text(row, 60, y, 155, "#172d2b")
    body += svg_text(".,:;!? & / + = ( )", 65, 920, 100, "#172d2b")
    body += label("OPTICAL SMALL CAPS / LOWERCASE INPUT + SMCP", 65, 990)
    body += svg_text(
        "abcdefghijklmnopqrstuvwxyz", 65, 1070, 86, "#172d2b", {"smcp": True}
    )
    body += label("DEFAULT LIGATURES / CO  OR  COR  BA  RA", 65, 1160)
    body += svg_text("CO OR COR BA RA", 65, 1260, 111, "#172d2b")
    body += label("DISCRETIONARY / OO  OC  LA  FY", 65, 1340)
    body += svg_text("OO OC LA FY", 65, 1440, 111, "#172d2b", {"dlig": True})
    body += svg_text("AVATAR  WAVE  TOY  NOON  MINIMUM", 65, 1530, 60, "#172d2b")
    body += label("D / P / J / V / W / 1 — OPEN BOWLS & CAP RETURNS", 65, 1640)
    body += svg_text("DPJVW1", 65, 1810, 205, "#172d2b")
    body += svg_text("DEEP / JUPITER", 65, 1980, 104, "#172d2b")
    body += svg_text("WAVES / VIEW / 101", 65, 2130, 104, "#172d2b")
    body = body.replace('height="1600"', 'height="2250"', 1)
    write_svg("Bathys-glyph-proof.svg", body, 1400, 2250)
    interlock_proof()
    reference_proof()


def interlock_proof():
    items = list(LIGS) + list(DLIGS)
    height = 180 + ((len(items) + 3) // 4) * 290 + 380
    body = f'<rect width="1600" height="{height}" fill="#eee8d8"/>'
    body += label("BATHYS / EVERY INTERLOCK / ORDINARY ABOVE, LIGATURE BELOW", 60, 65)
    for i, sequence in enumerate(items):
        x = 60 + (i % 4) * 390
        y = 140 + (i // 4) * 290
        body += label(
            sequence + (" / STANDARD" if sequence in LIGS else " / OPTIONAL"), x, y
        )
        size = 100 if len(sequence) < 4 else 84
        body += svg_text(
            sequence, x, y + 92, size, "#89938a", {"liga": False, "dlig": False}
        )
        body += svg_text(sequence, x, y + 197, size, "#102b2b", {"dlig": True})
        body += svg_text(
            sequence.lower(), x, y + 253, 62, "#a77b45", {"dlig": True, "smcp": True}
        )
    y = height - 270
    body += label("DEFAULT SPIRAL S", 60, y)
    body += svg_text("THE SEA", 60, y + 205, 230, "#102b2b")
    body += label("O / ZERO / SLASHED ZERO", 1090, y)
    body += svg_text("O 0", 1090, y + 105, 105, "#102b2b")
    body += svg_text("0", 1090, y + 225, 105, "#102b2b", {"zero": True})
    write_svg("Bathys-ligatures.svg", body, 1600, height)


def reference_proof():
    source = base64.b64encode(
        (ROOT / "extract/reference/sea.jpg").read_bytes()
    ).decode()
    body = '<rect width="2350" height="1480" fill="#102b2b"/>'
    body += f'<defs><image id="cover" href="data:image/jpeg;base64,{source}" width="1360" height="1360"/></defs>'
    body += label(
        "THE SEA / ENLARGED ORIGINAL LEFT / BATHYS AT THE SAME CAP HEIGHT RIGHT", 50, 60
    )
    rows = [
        ("CORINNE", (60, 65, 515, 135), 194, 120),
        ("BAILEY", (82, 193, 359, 128), 316, 118),
        ("RAE", (75, 315, 230, 135), 444, 119),
    ]
    for i, (word, (cx, cy, cw, ch), baseline, cap) in enumerate(rows):
        y = 115 + i * 420
        body += label(word, 50, y)
        body += f'<svg x="50" y="{y + 25}" width="{cw * 2}" height="{ch * 2}" viewBox="{cx} {cy} {cw} {ch}"><use href="#cover"/></svg>'
        body += svg_text(
            word, 1200, y + 25 + (baseline - cy) * 2, cap * 2 / 700 * 1000, "#eee8d8"
        )
    body += label(
        "CHECK: HORIZONTAL C ENDS / OPEN R THROAT / BA COUNTER / CONTINUOUS EY / SECOND N UPPER RETURN",
        50,
        1430,
    )
    write_svg("Bathys-reference-study.svg", body, 2350, 1480)


def render():
    data = (ROOT / "fonts/Bathys-Regular.otf").read_bytes()
    font = TTFont(ROOT / "fonts/Bathys-Regular.otf")
    order = font.getGlyphOrder()
    # A temporary PUA cmap exposes individual glyphs to FreeType; shipping font is unchanged.
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.update({0xE000 + i: n for i, n in enumerate(order)})

    renderfont = BytesIO()
    font.save(renderfont)
    renderdata = renderfont.getvalue()
    im = Image.new("RGB", (1600, 2180), "#eee8d8")
    draw = ImageDraw.Draw(im)

    def text(s, x, y, size, colour="#102b2b", features=None):
        f = hb.Font(hb.Face(data))
        buf = hb.Buffer()
        buf.add_str(s)
        buf.guess_segment_properties()
        hb.shape(f, buf, features or {})
        ft = ImageFont.truetype(BytesIO(renderdata), size)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions, strict=True):
            draw.text(
                (x + pos.x_offset * size / 1000, y - pos.y_offset * size / 1000),
                chr(0xE000 + info.codepoint),
                font=ft,
                fill=colour,
                anchor="ls",
            )
            x += pos.x_advance * size / 1000

    draw.rectangle((0, 0, 1600, 980), fill="#102b2b")
    for s, y in [("CORINNE", 260), ("BAILEY", 510), ("RAE", 760)]:
        text(s, 80, y, 320, "#eee8d8")
    text("THE SEA / THE LOVE EP", 85, 880, 65, "#d7b17c", {"c2sc": True})
    for s, y in [
        ("ABCDEFG", 1130),
        ("HIJKLMN", 1270),
        ("OPQRSTU", 1410),
        ("VWXYZ", 1550),
    ]:
        text(s, 60, y, 145)
    text("0123456789", 60, 1680, 125)
    text("CO OR COR BA RA NN EY", 60, 1800, 90)
    text("abcdefghijklmnopqrstuvwxyz", 60, 1890, 95, features={"smcp": True})
    text("WE ORBIT THE SAME SUN.", 60, 1990, 78)
    text("THE SEA", 60, 2110, 140)
    im.save(ROOT / "svg/Bathys-rendered-proof.png")
