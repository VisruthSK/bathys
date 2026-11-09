# Bathys

Circular display capitals drawn from Corinne Bailey Rae’s **The Sea** and **The Love EP**: an open-throated R, returning N, asymmetric A, interlocking bowls, a rising H crossbar and the subtitle’s descending spiral S.

**[Open the interactive proof](proof.html)** · [Static OTF](fonts/Bathys-Regular.otf) · [Variable OTF](fonts/Bathys-Variable.otf)

The proof includes a width slider, small caps and ligature switches. For close inspection, open the [S/N/EY/H details and S overlay](svg/Bathys-detail-study.svg), [cover comparison](svg/Bathys-reference-study.svg), [complete ligature sheet](svg/Bathys-ligatures.svg), or [rendered font proof](svg/Bathys-rendered-proof.png). All SVG lettering is outlined.

## OpenType features

| Feature | What it does |
| --- | --- |
| `liga` | CO, OR, COR, BA, RA, NN, EY |
| `dlig` | 28 additional round overlaps, shared stems, joined top bars and longer interlocks |
| `smcp`, `c2sc` | Optical small caps, including every ligature |
| `zero` | Slashed zero; ordinary zero is already narrower than O |
| `kern` | Pair spacing inherited by the outside letters of each ligature |

Lowercase input displays as capitals. The flowing S is the ordinary S, including in small caps. Keep tracking at zero for the cover setting. The CFF2 variable font has a **width axis from 85–115**, with the reference construction at 100. Static and variable defaults have identical filled outlines and metrics. This is a width family; it does not claim a weight axis.

```css
@font-face {
  font-family: Bathys;
  src: url("fonts/Bathys-Variable.woff2") format("woff2");
  font-stretch: 85% 115%;
}
.title {
  font-family: Bathys;
  font-variation-settings: "wdth" 100;
  font-feature-settings: "liga" 1, "kern" 1;
}
```

## Rebuild

Everything used to draw, compile and test the font lives in **[`extract/`](extract/)**. Dependencies are declared in the uv script; no project virtual environment is needed.

```powershell
uv run --python 3.13 extract/build.py --check
uvx ruff format extract
uvx ruff check extract
```

Add `--glyphs` to export individual editable outlines into `extract/generated/glyphs/`. Intermediate feature code, metrics and browser screenshots also go into that ignored directory. Installable fonts stay in `fonts/`; shareable proofs stay in `svg/`.

For browser verification, serve this directory with `uv run --python 3.13 -m http.server 8765 --bind 127.0.0.1`. In a second terminal, run `uv run extract/test_browser.py`. Chromium must be installed once with `uv run --with playwright playwright install chromium`.

The font suite checks substitutions, small caps, ligature carets, contour details, kerning, bounds, webfont parity and variable interpolation. Browser checks cover font decoding, controls, actual variable layout and mobile overflow. Aesthetic decisions are documented with reference crops and proofs in [the design notes](extract/DESIGN.md).
