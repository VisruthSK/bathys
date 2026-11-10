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
| S | The subtitle’s outer and inner edges are hand-fitted in source-image coordinates in `reference/S.svg`, using the neighbouring E to set the cap height and baseline. The whole spiral is uniformly fitted to the -12/712 overshoot band with stroke compensation. Its inward return and counter remain open. This is the default S. |
| H | The subtitle’s crossbar curves out of the lower left stem and rises into the right stem. Bathys keeps the main 66-unit stroke and straight stems; the bottom-left loop is omitted. |

`Bathys-reference-study.svg` places the original raster lettering beside the new outlines at the same cap height. `Bathys-glyph-proof.svg` shows the alphabet, figures and word trials. `Bathys-ligatures.svg` shows every interlock at two sizes, alongside its unligated counterpart. The full original covers remain under `reference/` for comparison.

The optional `uv run --project extract --group trace extract/trace_s.py` extracts the S silhouette into `generated/S-extracted.svg` for comparison. The final outline is finished by hand in `reference/S.svg`; the extraction script does not overwrite it. This avoids carrying the JPEG’s edge noise into the font. Two connections to the neighbouring E are separated along the S’s visible outer curvature.

## Drawing and spacing

- [Glyphs: Drawing good paths](https://glyphsapp.com/learn/drawing-good-paths) explains curve handles, extrema, contour direction and overlap removal. Bathys keeps cubic curves, unites intersections before compilation and preserves intended counters explicitly. CFF coordinates are rounded once, consistently in static and variable fonts.
- [Glyphs: Spacing](https://glyphsapp.com/learn/spacing) uses H and O as capital spacing controls. The proof includes straight/round strings and actual headlines; reference words are judged at reading size as well as enlarged.
- [OH no: Spacing](https://ohnotype.co/blog/spacing) emphasizes the relationship between interior and exterior space. The close cover spacing is retained without treating every pair as a ligature.
- [Glyphs: Kerning](https://glyphsapp.com/learn/kerning) separates general spacing from pair corrections. Ligatures inherit the pair adjustments of their outside letters, so a new interlock does not introduce an arbitrary gap in a word.
- [OH no: Proof It!](https://ohnotype.co/blog/proof-it) distinguishes a useful diagnostic proof from a polished specimen. Bathys supplies both: same-height reference comparisons, plain/ligated pairs, multiple sizes and a separate poster.
- [Glyphs: Making small caps](https://glyphsapp.com/learn/making-small-caps) calls for weight compensation rather than simple shrinking. Every small-cap contour is expanded before reduction; flat caps finish at 518 units. Small-cap interlocks retain their own counters and advances.

## Features and interpolation

- [Glyphs: Ligatures](https://glyphsapp.com/learn/ligatures) describes standard/discretionary substitutions and caret positions. Clear cap-bar and foot joins, RA, AR and AE are standard. OR, COR and the denser overlapping circles remain discretionary. Longer interlocks accept already-formed standard ligatures.
- [Microsoft: GDEF](https://learn.microsoft.com/en-us/typography/opentype/spec/gdef) defines carets inside ligatures. Bathys provides ordered internal caret positions for every interlock, in both sizes.
- [Microsoft: Width axis](https://learn.microsoft.com/en-us/typography/opentype/spec/dvaraxistag_wdth) defines 100 as the normal-width value. Bathys uses a restrained 85–115 range, transforming matching cubic topology, spacing, kern values and carets together.
- [FontTools: varLib](https://fonttools.readthedocs.io/en/latest/varLib/index.html) compiles the CFF2 variable font. Tests compare the default’s filled geometry with the static font and exercise both endpoints and intermediate positions. Width is deliberately mechanical; these are not separately optically redrawn condensed/expanded masters.
- [uv: Project layout](https://docs.astral.sh/uv/concepts/projects/layout/) describes the shared project metadata and cross-platform lockfile. All build dependencies and Ruff settings live in `extract/pyproject.toml`; browser/lint tools use the dev group, and silhouette extraction uses the optional trace group. `build.py` owns the reproducible build; importing the outline source never writes files.

## Scope of the extensions

G has the approved downward hook; the bar reaches the outer bowl and is clipped to the same ellipse to remove the step at the connection. Q uses the approved flowing tail. D and P use open returns related to R’s open throat. V and W retain diagonal valleys with a leftward upper return on their final strokes, repeating N’s cap flourish. J adds the same cap return over its hooked bowl. Zero is a narrower oval, with an optional slash; six has a smaller circular lower bowl and nine has a circular upper bowl with a straight upright stem.

The proportional lining one uses a single outline: its angled flag meets the upright at the 700-unit cap line. This replaces the overlapping diagonal bar that left the old top malformed. [Glyphs’ figure-set guidance](https://glyphsapp.com/learn/figure-sets) distinguishes these proportional lining figures from tabular and old-style sets.

The extra interlocks use three recurring devices: overlapping circles, shared vertical stems and joined top bars. They are tested in words as well as pairs. FY, ET, FT, TE, AY and NY extend the top-bar relationships; LY connects its foot to Y’s stem. A heavily nested TA was rejected during proofing because the letter identities became ambiguous.

RO, ON, OL, LO, OE, ORA, CORO, OOR and TI are excluded. Only TH, TE, TR, TU and TW remain from the T-series; mechanically repetitive T combinations have been removed.

A weight axis needs separate drawing work around BA’s narrow aperture, the R throat and the small-cap counters. The delivered width axis keeps those details intact. Weight is not simulated by thickening the outlines indiscriminately.

## Validation and study boundary

The compiled-font audit checks every contour and exact ink intersections in all 676 capital pairs and all 676 small-cap pairs. EY has intentional contact with standard ligatures disabled. The reading-size sheet checks the revised spacing in words from 32 to 144 units.

Static/variable design outlines, default advances, webfont tables, ligatures, carets and width-axis endpoints are checked independently. Browser tests load OTF and WOFF2 in Chromium, Firefox and WebKit. Design-unit equality is measured at 1000 px; Windows Chromium rounds CFF2 device-pixel advances differently at smaller sizes.

Production T keeps its flat bar; 7 keeps its original top and uses a straight crossbar, enforced by exact geometry tests. Rejected bar experiments have been removed. The accepted G/Q treatment is in the font. All rejected letter studies, Tide and the conventional S drawing have been removed.

## Composable joining

Longer runs use contextual alternates, retaining one glyph per character. A marking pass identifies runs with at least two compatible connections, an endpoint pass includes their first and last letters, and a resolving pass selects outgoing forms. Their advances come from the existing pair placements. Terminal forms retain the ordinary advance. There are no word-specific ATH or BATH glyphs.

A/T/H keep their original ink. EY/FY retain their purpose-built cap bridge, and NN retains the plain-first/returning-last construction. Outgoing advances already encode a join, so ordinary pair kerning is suppressed inside a connected run; kerning is inherited normally at its outside edges. Negative right sidebearings on outgoing forms are intentional. Individual letters remain selectable.

Tests cover every valid connected run of three, four and five letters in capitals and small caps, plus explicit ATH positions of 0, 515 and 979. `calt=0` retains the legacy pair-only path. The poster and cover comparison use that mode for the reference lettering.

[Microsoft's contextual-alternate specification](https://learn.microsoft.com/en-us/typography/opentype/spec/features_ae#tag-calt) defines context-dependent forms for better joins and recommends enabling them by default. [Glyphs' positional-alternate guidance](https://glyphsapp.com/learn/features-part-4-positional-alternates) explains why Latin joining should use `calt` rather than Arabic positional features. Bathys follows that approach. The expanded proof includes WEATHER, FEATHER, GATHER, FEATURE, THEATRE, RARE, LAYER and ARRAY. Tests also break joining contexts with spaces, nonbreaking spaces, hyphens, slashes and periods.

## Zero and stroke review

Zero's body is 542 units wide against O's 700, with its height and 34-unit sidebearings retained. Its fuller shoulders make the cap and baseline turns less pinched. Its outline is a 66-unit offset of a smooth oval centreline, avoiding the uneven shoulder thickness of subtracting two ellipses. The compiled contour is measured normal to that centreline at 24 positions, with a 1.5-unit tolerance for coordinate rounding and sampling. The slash follows the revised centre. O retains its much wider circular construction.

[Glyphs' harmonization guidance](https://glyphsapp.com/learn/harmonization) relates opposing curves and their handles to the stroke direction; [Drawing good paths](https://glyphsapp.com/learn/drawing-good-paths#harmony) explains the uneven weight that mismatched inner and outer curves can introduce. The straight-stem system remains 66 units. The reference-derived A and the 71-unit P/R stems retain their existing proportions; G's 62-unit hook and the short 58-unit seven crossbar are deliberate lighter accents. These differences are preserved rather than redrawing the accepted characters to one numerical thickness.

EA and HY extend the joining graph independently of the ligature catalogue. E/F/H use the same cap-to-Y construction; E/L supply foot-to-A connections, retaining the established LA placement. No EA, HY or word-specific glyph is added. THEATRE composes E–A–T–R as individual forms; BATHYS composes B–A–T–H–Y. The A outline remains unchanged.

A common 44-unit bounding gap tightens upright terminals against neighbouring stems and A. Existing optical kerning exceptions take precedence. The outside-edge inheritance applies this spacing to both compound ligatures and contextual forms, preventing detached-looking gaps at the ends of connected runs. Exact collision audits still cover all 676 capital and 676 small-cap pairs with joining disabled.

[Briem's numeral-spacing method](https://help.fontlab.com/fontlab/8/tutorials/briem/5-0-spacing/briem-5-05-numerals/) tests figures between repeated controls. The numeral proof adds alternating zero, six and nine rows for that review. [Microsoft's figure standards](https://learn.microsoft.com/en-us/typography/develop/character-design-standards/figures) also use zero as the spacing control and distinguish flat alignments from round overshoots. Bathys retains proportional lining figures, equal zero sidebearings and the shared −12/712 overshoot band; nine's flat stem ends at the baseline.

[Briem's joined-letter guidance](https://help.fontlab.com/fontlab/8/tutorials/briem/5-0-spacing/briem-5-07-joined-letters/) distinguishes joins that meet another joining stroke from joins that overlap a stem. Bathys uses controlled overlap at its cap and foot contacts, with outgoing advances carrying that placement. Kerning handles the unconnected neighbours outside a run.
