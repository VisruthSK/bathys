# Bathys

Circular display capitals drawn from Corinne Bailey Rae’s **The Sea** and **The Love EP**: an open-throated R, returning N, asymmetric A, interlocking bowls, a rising H crossbar and the subtitle’s descending spiral S.

**[Open the interactive proof](proof.html)** · [Static OTF](fonts/Bathys-Regular.otf) · [Variable OTF](fonts/Bathys-Variable.otf)

The proof includes a width slider, small caps and ligature switches. For close inspection, open the [glyph and word proof](svg/Bathys-glyph-proof.svg), [cover comparison](svg/Bathys-reference-study.svg), [complete ligature sheet](svg/Bathys-ligatures.svg), [numeral proof](svg/Bathys-numerals-proof.svg), [reading-size spacing proof](svg/Bathys-spacing-proof.svg), or [rendered font proof](svg/Bathys-rendered-proof.png). All SVG lettering is outlined.

[Contextual joining proof](svg/Bathys-joining-proof.svg) shows both sides of ATH connected without a dedicated ATH glyph, followed by automatic joins in WEATHER, FEATURE, THEATRE, RARE and LAYER.

## OpenType features

| Feature | What it does |
| --- | --- |
| `liga` | BA, NN, EY, FY, TH, TE, TR, TU, TW, LA, AT, ET, FT, AY, RA, AR, AE |
| `dlig` | CO, OR, COR, OO, OC, OG, HE, NE, COO, NY, LY |
| `smcp`, `c2sc` | Optical small caps, including every ligature |
| `calt` | Composable joins, including EA and HY; lowercase capital aliases |
| `zero` | Slashed zero; the default has a fuller oval and remains narrower than O |
| `kern` | Pair spacing inherited by the outside letters of each ligature |

Lowercase input displays as capitals. The flowing S is the ordinary S, including in small caps; its full spiral fits the standard cap/baseline band. Keep tracking at zero for the cover setting. The CFF2 variable font has a **width axis from 85–115**, with the reference construction at 100. Static and variable defaults have identical filled outlines and metrics. This is a width family; it does not claim a weight axis.

Contextual alternates select individual joining forms in connected runs. EA and HY also work as isolated pairs, without compound glyphs. Compatible cap terminals share a construction rule; E's foot joins A's diagonal. These connections compose automatically in words such as THEATRE, WEATHER, HYMN and BATHYS. Existing pair ligatures retain their drawings. Disable `calt` for pair-only composition; disable both `calt` and `liga` for unconnected text. The proof's Ligatures switch controls both. The cover-comparison SVG deliberately uses pair-only composition for the original lettering.

```css
@font-face {
  font-family: Bathys;
  src: url("fonts/Bathys-Variable.woff2") format("woff2");
  font-stretch: 85% 115%;
}
.title {
  font-family: Bathys;
  font-variation-settings: "wdth" 100;
  font-feature-settings: "liga" 1, "calt" 1, "kern" 1;
}
```

## Rebuild

Everything used to draw, compile and test the font lives in **[`extract/`](extract/)**. One `pyproject.toml` and `uv.lock` cover the compiler, audit, browser tests and Ruff. uv manages the environment under `extract/`; dependencies are locked for reproducible builds.

```powershell
uv run --project extract --locked --python 3.13 extract/build.py --check
uv run --project extract --locked extract/audit.py
uv run --project extract --locked ruff format extract
uv run --project extract --locked ruff check extract
```

Add `--glyphs` to export individual editable outlines into `extract/generated/glyphs/`. Intermediate feature code, metrics and browser screenshots also go into that ignored directory. Installable fonts stay in `fonts/`; shareable proofs stay in `svg/`.

Browser validation covers Chromium, Firefox and WebKit, including all four font files. For browser verification, serve this directory with `uv run --project extract --locked python -m http.server 8765 --bind 127.0.0.1`. In a second terminal, run `uv run --project extract --locked extract/test_browser.py`. Install the browsers once with `uv run --project extract --locked playwright install chromium firefox webkit`.

The font suite checks substitutions, small caps, ligature carets, contour details, kerning, bounds, webfont parity and variable interpolation. Browser checks cover font decoding, controls, actual variable layout and mobile overflow. Aesthetic decisions are documented with reference crops and proofs in [the design notes](extract/DESIGN.md).
