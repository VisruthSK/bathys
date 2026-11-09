# Bathys

Geometric display capitals based on the artist-name lettering on Corinne Bailey Rae’s **The Sea** and **The Love EP**. Circular bowls, close verticals, an asymmetric right-stem A, and interlocking letter pairs. The existing Glyphr A supplies the original proportions; the rest is drawn as cubic outlines in `build.py`.

Open **[proof.html](proof.html)** to type, change size, toggle ligatures and small caps, invert the paper colour, and compare with the two reference images. Double-click **[fonts/Bathys-Regular.otf](fonts/Bathys-Regular.otf)** to install the font.

The covers provide a limited set of capitals, not an entire font. Bathys reconstructs that lettering and extends its construction to the missing letters, digits, punctuation and small caps. It is not the original production font. The handwritten album subtitles use a different style and are not reproduced here.

## Files

- `fonts/Bathys-Regular.otf` — installable CFF OpenType font.
- `fonts/Bathys-Regular.woff2` — browser version with identical outlines and features.
- `svg/Bathys-poster.svg` — outlined colour poster; no font installation needed.
- `svg/Bathys-glyph-proof.svg` — outlined alphabet, numbers and ligature sheet.
- `svg/Bathys-rendered-proof.png` — actual compiled OTF shaped by HarfBuzz and rasterized by FreeType.
- `svg/glyphs/` — editable cubic SVGs for individual glyphs.
- `Bathys.fea` and `glyph-data.json` — generated OpenType features and glyph metrics.

## Features

| Feature | Behaviour |
| --- | --- |
| `liga` | CO, OR, COR, BA, RA; enabled by default |
| `dlig` | OO, OC, RO, LA; opt in |
| `smcp` | Lowercase input becomes optical small capitals |
| `c2sc` | Uppercase input becomes optical small capitals |
| `kern` | Pair spacing for diagonals, rounds and reference words |
| `calt` | Lowercase aliases normalize to capitals so their ligatures also work |

Lowercase input has capital outlines by default. Small caps are 518 units tall against 700-unit capitals, with relatively stronger strokes. Both sizes have their own interlocking ligatures. Keep tracking at **zero** for the reference look. Use this face for titles and large display text; the proof includes smaller sizes to help judge where it stops working for your use.

```css
@font-face {
  font-family: Bathys;
  src: url("fonts/Bathys-Regular.woff2") format("woff2");
}
.title {
  font-family: Bathys;
  font-feature-settings: "liga" 1, "kern" 1;
  letter-spacing: 0;
}
.small-caps {
  font-feature-settings: "smcp" 1, "c2sc" 1, "liga" 1;
}
```

In desktop design applications, enable Standard Ligatures; use Discretionary Ligatures for the extra joins. Select Small Caps or All Small Caps for the small-cap sets. Applications that do not support OpenType substitutions still show the ordinary capitals.

## Build and verify

Python 3.13 was used for the delivered build. From this directory in PowerShell:

```powershell
uv venv .venv --python 3.13
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe build.py
.venv/Scripts/python.exe render_proof.py
.venv/Scripts/python.exe -m unittest test_font -v
```

The font tests check actual HarfBuzz substitutions, default and optional ligatures, lower/uppercase small caps, word boundaries, kerning, coverage, bounding boxes, stroke joins, and OTF/WOFF2 equivalence. They cannot certify aesthetic quality: use the supplied visual proofs to judge that.

For the browser checks, install Chromium once with `.venv/Scripts/playwright.exe install chromium`. Start `.venv/Scripts/python.exe -m http.server 8765 --bind 127.0.0.1` in another terminal, then run `.venv/Scripts/python.exe test_browser.py`. It checks font loading, editing, controls and mobile overflow, and saves desktop/mobile screenshots in `svg/`.

## Construction references

The build follows [Glyphs’ spacing guidance](https://glyphsapp.com/learn/spacing), [kerning guidance](https://glyphsapp.com/learn/kerning), and [its handbook’s optical overshoot guidance](https://handbook.glyphsapp.com/en/single-page/). Round letters extend 12 units past the baseline and cap line. Intersections are united before compilation to avoid winding knockouts; counters remain holes. CFF compilation uses the [FontTools FontBuilder](https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/fontBuilder.py), with substitutions compiled through [feaLib](https://fonttools.readthedocs.io/en/latest/feaLib/index.html).
