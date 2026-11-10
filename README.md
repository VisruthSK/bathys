# Bathys

A art-deco display typeface heavily inspired by Corinne Bailey Rae's face from _The Sea_ and _The Love EP_.

[Specimen](dist/index.html) · [Regular OTF](dist/fonts/Bathys-Regular.otf) · [Variable OTF](dist/fonts/Bathys-Variable.otf)

## Font

The variable font has a width axis from 85 to 115, with the reference width at 100. Standard ligatures and contextual forms compose automatically; denser interlocks are optional. Lowercase input displays as capitals unless small caps are enabled.

```css
@font-face {
  font-family: Bathys;
  src: url("fonts/Bathys-Variable.woff2") format("woff2");
  font-stretch: 85% 115%;
}

.title {
  font-family: Bathys, sans-serif;
  font-feature-settings:
    "liga" 1,
    "calt" 1,
    "kern" 1;
}
```

The fonts use the [SIL Open Font License 1.1](dist/OFL.txt). Copyright and the full license are embedded in all four font files. 

Reference album artwork is not covered by this font license.

## Sources

Drawing and build tools remain in `extract/`, with dependencies locked by uv. Rebuilding writes the fonts and specimen catalogue directly into `dist/`.

```powershell
uv run --project extract --locked --python 3.13 extract/build.py --check
uv run --project extract --locked extract/audit.py
uv run --project extract --locked ruff check extract
```

