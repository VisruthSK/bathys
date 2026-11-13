# Drawing notes

The artist-name capitals on _The Sea_ and _The Love EP_ supply A, B, C, E, I, L, N, O, R and Y. The remaining letters, figures and punctuation extend that construction. The subtitle supplies the spiral S and the idea for H’s rising crossbar.

A retains the asymmetric original drawing in `reference/Bathys.gs2`. BA translates A without narrowing it. R keeps its open throat. The first N in NN is plain; the second has the upper return. Small caps receive stroke compensation before reduction to 518 units.

The adopted P/J/D/G/Q terminal faces are cut 20 degrees from their original orientation. Cuts extend past the curved edges to avoid slivers. This changes the exposed endings while preserving the main curves and advances. [Fontfabric’s terminal guide](https://www.fontfabric.com/blog/typography-knowledge-terminals-typography/) describes these as sheared terminals; [Glyphs’ harmonization guide](https://glyphsapp.com/learn/harmonization) relates opposing contours to the writing tool.

Zero has a fuller oval and a 66-unit normal stroke. Six retains a circular lower bowl and counter, with an upright left stem and a compact curved upper shoulder. Nine has a circular upper bowl and a straight right stem. Figures use the same −12/712 round overshoots as the capitals.

## Joining

`LIGS` is the source for standard compound pairs, contextual forms, carets and the specimen catalogue. Three contextual passes inside `liga` identify connected runs, include their endpoints, then select each outgoing form. Turning off `liga` disables both pair ligatures and ordinary connected runs, independently of `calt`, which normalizes lowercase aliases. Its advance comes from the pair drawing. There are no word-specific ATH or THEATRE glyphs. [Glyphs’ contextual-substitution guide](https://glyphsapp.com/learn/features-part-2-contextual-substitutions) explains using classes for shared contexts.

E/F/H share the same bridge into V/W/Y. VT and WT share V/W’s upper return with T’s flat bar. Dense circular interlocks remain discretionary. T and seven retain their normal straight bars.

TT shares a continuous flat cap by default. Optional AK and AF share A's existing right upright, using the same placement as AE/AR. They participate in longer runs such as FAKIR and AFTER without whole-word substitutions. X's upper-right arm has the same 178-unit cap return as V/W, with a 66-unit horizontal stroke; its crossing, lower diagonals and advance are unchanged.

FA extends F's middle arm into A's existing diagonal and participates in contextual runs such as FATHER. CC (440-unit origin), GO and COG are optional. AV, AW, AL and LY are removed. GT, TC and KO have tighter optical spacing; S and its spacing remain unchanged. The slash has a compensated small-cap form under both `smcp` and `c2sc`.

Optional connected runs use the same catalogue-driven passes as standard runs, before isolated pair ligatures are substituted. Thus ATE connects on both sides of T, while optional sequences can continue through circular and structural joins without consuming a shared letter prematurely. Existing COR/COO/COG drawings are retained at run endings; their internal origins agree with the pair catalogue. Continuing optional forms use actual component origins, including CO's optical end-bearing difference. No whole-word alternates are generated.

Kerning inherits the outside letters of a compound or contextual form; an outgoing form encodes its internal connection in its advance. Existing optical exceptions take precedence over the common spacing rule for upright terminals. Width masters scale contours, spacing, kerning and carets together over 85–115. The axis is mechanical width variation, not an optical width or weight family.

## Sources and proofing

`reference/S.path` stores the hand-finished spiral contour. The optional `trace_s.py` extracts a comparison contour and mask without overwriting it. The `.path` files contain plain drawing commands, not complete image documents.

The committed static site lives in `dist/`. `specimen-data.js` is generated from the catalogue; presentation and controls live in `specimen.css` and `specimen.js`. There are no vector proof sheets. The site uses the specified warm brand colors, with light and dark theme roles defined in `dist/specimen.css`.

The specimen's hierarchy draws on [GT Standard](https://www.grillitype.com/typeface/gt-standard), [Diatype](https://abcdinamo.com/typefaces/diatype), [Degular](https://ohnotype.co/fonts/degular), [Söhne](https://klim.co.nz/fonts/soehne/) and [Druk](https://commercialtype.com/catalog/druk): the editable sample leads into display settings and feature examples. Six featured interlocks introduce the construction before the full catalogue. The character inspector is always visible below Small capitals in the Letters section. Album covers appear in two columns on desktop and stack on small screens.

Response headers follow the same-origin approach in `../VisruthSK.github.io/public/_headers`, with no inline-script exceptions or external assets. Cloudflare serves `dist/` directly and applies `_headers`. There are no server, export or redirect helpers.

The public version is 1.0. Source builds reproduce its version strings and the Reserved Font Name declaration in `dist/OFL.txt`. Font metadata embeds the copyright and complete SIL Open Font License 1.1. The size controls use CSS points. The introduction and Reference section contain finalized editorial copy.

The tester starts at 40 pt on mobile and 64 pt on larger screens, with a single-line pangram value. Numeric fields allow direct entry, and each slider resets to its initial default on double-click. Typed size and tracking values can extend the slider range. The trial uses the reference width; variable fonts remain available for download. Featured cards compare unjoined and joined forms. The optional catalogue has its own count, and numerals appear below the small-cap alphabet at the same type size.

Ordinary FA kerning is −300 instead of −275; the joined FA retains its original 120-unit origin. RT, EA and selected sloping-A pairs are slightly closer. IL has about 10% more clearance. HA and MA are default overlap ligatures, with A translated at the same offset relative to the H/M right stem. Standalone A and its advance are preserved. Lowercase aliases inherit uppercase kerning even with `calt` disabled; MILLION has no IL ligature and keeps the same spacing when features switch. Deployment checks cover names, dates, times and short headings without expanding the character set.

Unjoined EY now has clear separation; its joined drawing is unchanged, and the audit has no collision exemption for it. U's right stem follows the same spacing policy as H/M/N before uprights.

Alias normalization is shared with `liga` and `dlig`, so lowercase joins do not require `calt`. Optical exceptions at a compound's incoming edge also apply to its first contextual form, preserving spacing around longer runs.

The colon is centred vertically beside lining numerals; the semicolon's upper dot aligns with it. Their circular dots keep the existing weight and advances.

HA/MA use a straight-sided A join alternate, with its toe tucked inside the H/M stem. The visible shared foot is 66 units in capitals and 58 in small caps. There is no curved blend: the toe vertices connect directly to the existing diagonal endpoints. A's standalone drawing, advance, counter and right stem are unchanged. A final contextual lookup selects matching incoming-foot variants after H/M in longer runs. The stem owns the exposed baseline edges; isolated compounds use the same integer origins as composed forms.
