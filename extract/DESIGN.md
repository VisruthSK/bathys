# Drawing notes

The artist-name capitals on _The Sea_ and _The Love EP_ supply A, B, C, E, I, L, N, O, R and Y. The remaining letters, figures and punctuation extend that construction. The subtitle supplies the spiral S and the idea for H’s rising crossbar.

A retains the asymmetric original drawing in `reference/Bathys.gs2`. BA translates A without narrowing it. R keeps its open throat. The first N in NN is plain; the second has the upper return. Small caps receive stroke compensation before reduction to 518 units.

The adopted P/J/D/G/Q terminal faces are cut 20 degrees from their original orientation. Cuts extend past the curved edges to avoid slivers. This changes the exposed endings while preserving the main curves and advances. [Fontfabric’s terminal guide](https://www.fontfabric.com/blog/typography-knowledge-terminals-typography/) describes these as sheared terminals; [Glyphs’ harmonization guide](https://glyphsapp.com/learn/harmonization) relates opposing contours to the writing tool.

Zero has a fuller oval and a 66-unit normal stroke. Six retains a circular lower bowl and counter, with an upright left stem and a compact curved upper shoulder. Nine has a circular upper bowl and a straight right stem. Figures use the same −12/712 round overshoots as the capitals.

## Joining

`LIGS` is the source for standard compound pairs, contextual forms, carets and the specimen catalogue. A three-pass contextual lookup identifies connected runs, includes their endpoints, then selects each outgoing form. Its advance comes from the pair drawing. There are no word-specific ATH or THEATRE glyphs. [Glyphs’ contextual-substitution guide](https://glyphsapp.com/learn/features-part-2-contextual-substitutions) explains using classes for shared contexts.

E/F/H share the same bridge into V/W/Y. AV and AW preserve A and meet the diagonal’s entry at the cap. VT and WT share V/W’s upper return with T’s flat bar. Dense circular interlocks remain discretionary. T and seven retain their normal straight bars.

Kerning inherits the outside letters of a compound or contextual form; an outgoing form encodes its internal connection in its advance. Existing optical exceptions take precedence over the common spacing rule for upright terminals. Width masters scale contours, spacing, kerning and carets together over 85–115. The axis is mechanical width variation, not an optical width or weight family.

## Sources and proofing

`reference/S.path` stores the hand-finished spiral contour. The optional `trace_s.py` extracts a comparison contour and mask without overwriting it. The `.path` files contain plain drawing commands, not complete image documents.

The committed static site lives in `dist/`. `specimen-data.js` is generated from the catalogue; presentation and controls live in `specimen.css` and `specimen.js`. There are no vector proof sheets. The site uses the specified warm brand colors, with light and dark theme roles defined in `dist/specimen.css`.

The specimen's hierarchy draws on [GT Standard](https://www.grillitype.com/typeface/gt-standard), [Diatype](https://abcdinamo.com/typefaces/diatype), [Degular](https://ohnotype.co/fonts/degular), [Söhne](https://klim.co.nz/fonts/soehne/) and [Druk](https://commercialtype.com/catalog/druk): the editable sample leads into display settings and feature examples. Six featured interlocks introduce the construction before the full catalogue. The character inspector is always visible below Small capitals in the Letters section. Album covers appear in two columns on desktop and stack on small screens.

Response headers follow the same-origin approach in `../VisruthSK.github.io/public/_headers`, with no inline-script exceptions or external assets. Cloudflare serves `dist/` directly and applies `_headers`. There are no server, export or redirect helpers.

The public version is 1.0. Source builds reproduce its version strings and the Reserved Font Name declaration in `dist/OFL.txt`. Font metadata embeds the copyright and complete SIL Open Font License 1.1. The size controls use CSS points. The introduction and Reference section contain finalized editorial copy.

The tester defaults to 64 pt and a single-line pangram value. Numeric fields allow direct entry, and each slider resets to its own default on double-click. Typed size and tracking values can extend the slider range; width stays within the font’s 85–115 axis. The public gallery presents final forms only.
