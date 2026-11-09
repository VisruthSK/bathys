# Bathys: reference audit and drawing decisions

The artist-name lettering and the thin **THE SEA** subtitle are two different constructions. Bathys follows the artist name, with its ordinary S drawn from the subtitle’s large descending spiral. Letters visible in the artist name are **A B C E I L N O R Y**; the other capitals, numerals and punctuation extend those forms.

## What the enlarged covers show

| Form | Observation and implementation |
| --- | --- |
| C | Circular bowl with **horizontal** terminals. The first build’s radial cuts were wrong. |
| O | Nearly circular, with optical overshoot. CO offsets the bowls; OR places R’s stem inside O’s right side. |
| R | The return of the bowl runs into the diagonal leg. It **does not cross back to the stem**. The standalone R in RAE is the clearest reference. |
| A | Rising left diagonal, vertical right stem, low crossbar. The supplied Glyphr drawing is retained as the starting geometry. |
| B / BA | A is the unchanged 636-unit character, translated 180 units to the right of B’s origin. Both source contours are retained verbatim. The small background opening follows naturally from the placement; no cut, scaling or stroke alteration is applied to A. |
| I / L | Simple vertical and foot; their close spacing contributes to BAILEY’s rhythm. |
| E / EY | Square arms; E’s top bar continues at full depth into Y’s left diagonal. EY has a custom bridge so the underside has no notch. FY uses the same construction. |
| Y | Narrow fork, straight stem, flat terminals. |
| N / NN | The flourish is a horizontal return at the TOP of the right stem. There is no spur below the baseline. NN has a narrower plain first N, a slightly wider returning second N, and an open gap between their stems. |
| S | The subtitle’s outer and inner edges are hand-fitted in source-image coordinates in `reference/S.svg`, using the neighbouring E to set the cap height and baseline. The lower loop descends below that baseline, and its inward return and counter remain open. This is the default S. |
| H | The subtitle’s crossbar curves out of the lower left stem and rises into the right stem. Bathys keeps the main 66-unit stroke and straight stems; the bottom-left loop is omitted. |

`Bathys-reference-study.svg` places the original raster lettering beside the new outlines at the same cap height. `Bathys-glyph-proof.svg` shows the alphabet, figures and word trials. `Bathys-ligatures.svg` shows every interlock at two sizes, alongside its unligated counterpart. The full original covers remain under `reference/` for comparison.

The optional `uv run extract/trace_s.py` extracts the S silhouette into `generated/S-extracted.svg` for comparison. The final outline is finished by hand in `reference/S.svg`; the extraction script does not overwrite it. This avoids carrying the JPEG’s edge noise into the font. Two connections to the neighbouring E are separated along the S’s visible outer curvature.

## Drawing and spacing

- [Glyphs: Drawing good paths](https://glyphsapp.com/learn/drawing-good-paths) explains curve handles, extrema, contour direction and overlap removal. Bathys keeps cubic curves, unites intersections before compilation and preserves intended counters explicitly. CFF coordinates are rounded once, consistently in static and variable fonts.
- [Glyphs: Spacing](https://glyphsapp.com/learn/spacing) uses H and O as capital spacing controls. The proof includes straight/round strings and actual headlines; reference words are judged at reading size as well as enlarged.
- [OH no: Spacing](https://ohnotype.co/blog/spacing) emphasizes the relationship between interior and exterior space. The close cover spacing is retained without treating every pair as a ligature.
- [Glyphs: Kerning](https://glyphsapp.com/learn/kerning) separates general spacing from pair corrections. Ligatures inherit the pair adjustments of their outside letters, so a new interlock does not introduce an arbitrary gap in a word.
- [OH no: Proof It!](https://ohnotype.co/blog/proof-it) distinguishes a useful diagnostic proof from a polished specimen. Bathys supplies both: same-height reference comparisons, plain/ligated pairs, multiple sizes and a separate poster.
- [Glyphs: Making small caps](https://glyphsapp.com/learn/making-small-caps) calls for weight compensation rather than simple shrinking. Every small-cap contour is expanded before reduction; flat caps finish at 518 units. Small-cap interlocks retain their own counters and advances.

## Features and interpolation

- [Glyphs: Ligatures](https://glyphsapp.com/learn/ligatures) describes standard/discretionary substitutions and caret positions. The seven cover-related interlocks are standard; experimental combinations are discretionary. Longer interlocks accept already-formed standard ligatures.
- [Microsoft: GDEF](https://learn.microsoft.com/en-us/typography/opentype/spec/gdef) defines carets inside ligatures. Bathys provides ordered internal caret positions for every interlock, in both sizes.
- [Microsoft: Width axis](https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_wdth) defines 100 as the normal-width value. Bathys uses a restrained 85–115 range, transforming matching cubic topology, spacing, kern values and carets together.
- [FontTools: varLib](https://fonttools.readthedocs.io/en/latest/varLib/index.html) compiles the CFF2 variable font. Tests compare the default’s filled geometry with the static font and exercise both endpoints and intermediate positions. Width is deliberately mechanical; these are not separately optically redrawn condensed/expanded masters.
- [uv: Running scripts](https://docs.astral.sh/uv/guides/scripts/) documents inline dependency metadata. `build.py` owns the reproducible build; importing the outline source never writes files.

## Scope of the extensions

G follows the circular construction with an inward shelf. D and P use open returns related to R’s open throat. V and W retain diagonal valleys with a leftward upper return on their final strokes, repeating N’s cap flourish. J adds the same cap return over its hooked bowl. Zero is a narrower oval, with an optional slash; nine has an upright upper bowl and descending return.

The proportional lining one uses a single outline: its angled flag meets the upright at the 700-unit cap line. This replaces the overlapping diagonal bar that left the old top malformed. [Glyphs’ figure-set guidance](https://glyphsapp.com/learn/figure-sets) distinguishes these proportional lining figures from tabular and old-style sets.

The extra interlocks use three recurring devices: overlapping circles, shared vertical stems and joined top bars. They are tested in words as well as pairs. FY, ET, FT, TE, AY and NY extend the top-bar relationships; LY connects its foot to Y’s stem. A heavily nested TA was rejected during proofing because the letter identities became ambiguous.

RO, ON, OL, LO, OE, ORA, CORO and OOR are excluded from both sizes and both font formats.

A weight axis needs separate drawing work around BA’s narrow aperture, the R throat and the small-cap counters. The delivered width axis keeps those details intact. Weight is not simulated by thickening the outlines indiscriminately.
