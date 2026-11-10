"""Structural and real-shaping checks against the distributed binaries."""

import math
import unittest
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from outlines import DLIGS, JOIN_FORMS, JOIN_PAIRS, LIGS

ROOT = Path(__file__).resolve().parent.parent


class FontProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font = TTFont(ROOT / "fonts/Bathys-Regular.otf", checkChecksums=2)
        cls.glyphs = cls.font.getGlyphSet()
        cls.order = cls.font.getGlyphOrder()
        cls.hbfont = hb.Font(hb.Face((ROOT / "fonts/Bathys-Regular.otf").read_bytes()))

    def shape(self, text, **features):
        b = hb.Buffer()
        b.add_str(text)
        b.guess_segment_properties()
        hb.shape(self.hbfont, b, features)
        return [
            (self.order[i.codepoint], p.x_advance)
            for i, p in zip(b.glyph_infos, b.glyph_positions, strict=True)
        ]

    def test_reference_word(self):
        self.assertEqual(
            [n for n, w in self.shape("CORINNE", dlig=True)], ["C_O_R", "I", "N_N", "E"]
        )
        self.assertEqual(
            [n for n, w in self.shape("CORINNE")], ["C", "O", "R", "I", "N_N", "E"]
        )
        self.assertEqual([n for n, w in self.shape("BAILEY")], ["B_A", "I", "L", "E_Y"])

    def test_each_ligature_and_switch(self):
        for seq in LIGS:
            with self.subTest(seq=seq):
                self.assertEqual(self.shape(seq)[0][0], "_".join(seq))
                self.assertEqual([n for n, w in self.shape(seq, liga=False)], list(seq))

    def test_discretionary(self):
        for seq in DLIGS:
            self.assertEqual(
                [n for n, w in self.shape(seq, dlig=True)], ["_".join(seq)]
            )
            self.assertNotEqual([n for n, w in self.shape(seq)], ["_".join(seq)])

    def test_tu_preserves_letter_identities(self):
        outline = pathops.Path()
        self.glyphs["T_U"].draw(outline.getPen())
        for point in [(294, 100), (1000, 500), (550, 670)]:
            self.assertTrue(outline.contains(point))
        self.assertFalse(outline.contains((766, 350)), "U counter must remain open")

    def test_th_has_no_cap_overhang(self):
        self.assertEqual(self.font["hmtx"]["T_H"][0], 1082)
        outline = pathops.Path()
        self.glyphs["T_H"].draw(outline.getPen())
        self.assertTrue(outline.contains((560, 670)))
        self.assertFalse(outline.contains((575, 670)))
        self.assertEqual(outline.bounds[2], 1044)

    def test_spacing_pairs_do_not_collide(self):
        for text in [
            "TA",
            "YA",
            "FA",
            "PA",
            "VA",
            "WA",
            "OA",
            "TS",
            "YS",
            "FS",
            "PS",
            "VS",
            "WS",
            "SA",
        ]:
            shaped = self.shape(text, liga=False, dlig=False)
            left = pathops.Path()
            right = pathops.Path()
            self.glyphs[shaped[0][0]].draw(left.getPen())
            self.glyphs[shaped[1][0]].draw(right.getPen())
            right = right.transform(1, 0, 0, 1, shaped[0][1], 0)
            self.assertLess(
                abs(pathops.op(left, right, pathops.PathOp.INTERSECTION).area),
                0.01,
                text,
            )

    def test_removed_ligatures(self):
        for sequence in [
            "RO",
            "ON",
            "OL",
            "LO",
            "OE",
            "ORA",
            "CORO",
            "OOR",
            "TI",
            "TB",
            "TD",
            "TF",
            "TK",
            "TL",
            "TM",
            "TN",
            "TP",
            "TV",
            "TX",
            "TZ",
            "TT",
            "TY",
        ]:
            for suffix in ["", ".sc"]:
                self.assertNotIn("_".join(sequence) + suffix, self.order)
            self.assertNotEqual(
                [n for n, w in self.shape(sequence, dlig=True)], ["_".join(sequence)]
            )

    def test_ba_uses_translated_unscaled_a(self):
        self.assertEqual(self.font["hmtx"]["A"], (636, 24))
        for suffix, offset in [("", 180), (".sc", 133)]:
            a = pathops.Path()
            b = pathops.Path()
            actual = pathops.Path()
            self.glyphs["A" + suffix].draw(a.getPen())
            self.glyphs["B" + suffix].draw(b.getPen())
            self.glyphs["B_A" + suffix].draw(actual.getPen())
            moved = a.transform(1, 0, 0, 1, offset, 0)
            expected = pathops.op(b, moved, pathops.PathOp.UNION)
            self.assertLess(
                abs(pathops.op(expected, actual, pathops.PathOp.XOR).area), 0.01
            )
            self.assertEqual(actual.bounds[2] - a.bounds[2], offset)

    def test_extension_details_and_one(self):
        for name, point in [("D", (130, 30)), ("P", (130, 310))]:
            p = pathops.Path()
            self.glyphs[name].draw(p.getPen())
            self.assertFalse(p.contains(point), f"{name} must have an open return")
            self.assertTrue(p.contains((70, 350)), f"{name} stem must remain solid")
        for name, point in [
            ("V", (460, 670)),
            ("W", (720, 670)),
            ("J", (230, 670)),
            ("one", (240, 650)),
        ]:
            p = pathops.Path()
            self.glyphs[name].draw(p.getPen())
            self.assertTrue(p.contains(point), name)
        p = pathops.Path()
        self.glyphs["one"].draw(p.getPen())
        self.assertEqual(p.bounds[3], 700, "The flag and stem must share one cap line")

    def test_main_t_and_seven_have_normal_bars(self):
        original = pathops.Path()
        from fontTools.svgLib.path import parse_path

        parse_path(
            "M28,700 L568,700 L568,644 L235,0 L159,0 L492,634 L28,634 Z",
            original.getPen(),
        )
        actual = pathops.Path()
        self.glyphs["seven"].draw(actual.getPen())
        crossbar = pathops.Path()
        parse_path("M230,321 L530,321 L530,379 L230,379 Z", crossbar.getPen())
        expected = pathops.op(original, crossbar, pathops.PathOp.UNION)
        self.assertLess(
            abs(pathops.op(expected, actual, pathops.PathOp.XOR).area), 0.01
        )
        t = pathops.Path()
        self.glyphs["T"].draw(t.getPen())
        original_t = pathops.Path()
        parse_path(
            "M20,700 L568,700 L568,634 L327,634 L327,0 L261,0 L261,634 L20,634 Z",
            original_t.getPen(),
        )
        self.assertLess(abs(pathops.op(original_t, t, pathops.PathOp.XOR).area), 0.01)

    def test_smallcaps(self):
        self.assertEqual(
            [n for n, w in self.shape("corinne", smcp=True, dlig=True)],
            ["C_O_R.sc", "I.sc", "N_N.sc", "E.sc"],
        )
        self.assertEqual(
            [n for n, w in self.shape("CORINNE", c2sc=True, dlig=True)],
            ["C_O_R.sc", "I.sc", "N_N.sc", "E.sc"],
        )
        self.assertEqual(self.shape("corinne"), self.shape("CORINNE"))
        for seq in LIGS:
            self.assertEqual(
                self.shape(seq.lower(), smcp=True)[0][0], "_".join(seq) + ".sc"
            )
        for seq in DLIGS:
            self.assertEqual(
                [n for n, w in self.shape(seq.lower(), smcp=True, dlig=True)],
                ["_".join(seq) + ".sc"],
            )

    def test_word_boundaries(self):
        self.assertEqual(
            [n for n, w in self.shape("C O R")], ["C", "space", "O", "space", "R"]
        )

    def test_bidirectional_joining_without_ath_glyph(self):
        self.assertNotIn("A_T_H", self.order)
        buffer = hb.Buffer()
        buffer.add_str("ATH")
        buffer.guess_segment_properties()
        hb.shape(self.hbfont, buffer)
        self.assertEqual([info.cluster for info in buffer.glyph_infos], [0, 1, 2])
        self.assertEqual(
            self.shape("ATH"), [("A.join_T", 515), ("T.join_H", 464), ("H.chain", 618)]
        )
        self.assertEqual(
            [n for n, w in self.shape("ETH")], ["E.join_T", "T.join_H", "H.chain"]
        )
        self.assertEqual(
            [n for n, w in self.shape("ATU")], ["A.join_T", "T.join_U", "U.chain"]
        )
        self.assertEqual(
            [n for n, w in self.shape("BATH")],
            ["B.join_A", "A.join_T", "T.join_H", "H.chain"],
        )
        self.assertEqual([n for n, w in self.shape("ATH", calt=False)], ["A_T", "H"])
        self.assertEqual(
            [n for n, w in self.shape("ATH", calt=False, liga=False)], ["A", "T", "H"]
        )
        self.assertFalse(
            any(".join_" in n or ".chain" in n for n, w in self.shape("AT H"))
        )

    def test_joining_preserves_a_t_and_h_ink(self):
        for base, form in [("A", "A.join_T"), ("T", "T.join_H"), ("H", "H.chain")]:
            left = pathops.Path()
            right = pathops.Path()
            self.glyphs[base].draw(left.getPen())
            self.glyphs[form].draw(right.getPen())
            self.assertLess(abs(pathops.op(left, right, pathops.PathOp.XOR).area), 0.01)
        self.assertEqual(
            [n for n, w in self.shape("ath", smcp=True)],
            ["A.join_T.sc", "T.join_H.sc", "H.chain.sc"],
        )

    def test_all_valid_joining_chains(self):
        runs = set(JOIN_PAIRS)
        for _ in range(3):
            runs = {
                run + right
                for run in runs
                for left, right in JOIN_PAIRS
                if run[-1] == left
            }
            for run in runs:
                expected = [
                    f"{left}.join_{right}"
                    for left, right in zip(run, run[1:], strict=False)
                ] + [run[-1] + ".chain"]
                self.assertEqual([n for n, w in self.shape(run)], expected, run)
                self.assertEqual(
                    [n for n, w in self.shape(run.lower(), smcp=True)],
                    [n + ".sc" for n in expected],
                    run,
                )

    def test_contextual_joins_in_words_and_at_boundaries(self):
        for word, middle in [
            ("WEATHER", ["A.join_T", "T.join_H", "H.chain"]),
            ("FEATHER", ["A.join_T", "T.join_H", "H.chain"]),
            ("GATHER", ["A.join_T", "T.join_H", "H.chain"]),
            ("FEATURE", ["A.join_T", "T.join_U", "U.chain"]),
            ("THEATRE", ["A.join_T", "T.join_R", "R.chain"]),
        ]:
            names = [n for n, _ in self.shape(word)]
            start = word.index("A")
            self.assertEqual(names[names.index(middle[0]) :][:3], middle, word)
            self.assertEqual(self.shape(word.lower()), self.shape(word))
            small = [n for n, _ in self.shape(word.lower(), smcp=True)]
            self.assertIn(middle[0] + ".sc", small)
            # A separator must end a chain, including punctuation and NBSP.
            for separator in [" ", "\u00a0", "-", "/", "."]:
                broken = word[: start + 2] + separator + word[start + 2 :]
                self.assertNotIn(middle[1], [n for n, _ in self.shape(broken)])

    def test_zero_has_even_curved_strokes(self):
        outline = pathops.Path()
        self.glyphs["zero"].draw(outline.getPen())
        self.assertEqual(self.font["hmtx"]["zero"][0], 610)
        self.assertEqual(outline.bounds, (34, -12, 576, 712))
        # Measure across the stroke, perpendicular to the centreline rather
        # than along horizontal scanlines through the sloping shoulders.
        for angle in range(0, 360, 15):
            theta = math.radians(angle)
            cx = 305 + 238 * math.cos(theta)
            cy = 350 + 329 * math.sin(theta)
            nx, ny = 329 * math.cos(theta), 238 * math.sin(theta)
            length = math.hypot(nx, ny)
            samples = [
                step / 4
                for step in range(-160, 161)
                if outline.contains(
                    (cx + step / 4 * nx / length, cy + step / 4 * ny / length)
                )
            ]
            self.assertAlmostEqual(max(samples) - min(samples), 66, delta=1.5)

    def test_new_connections_are_composable_individual_letters(self):
        for text, expected in [
            ("HY", ["H.join_Y", "Y.chain"]),
            ("EA", ["E.join_A", "A.chain"]),
            ("EATHY", ["E.join_A", "A.join_T", "T.join_H", "H.join_Y", "Y.chain"]),
            ("THEATRE", ["T_H", "E.join_A", "A.join_T", "T.join_R", "R.chain", "E"]),
        ]:
            self.assertEqual([n for n, _ in self.shape(text)], expected)
            self.assertEqual(
                [n for n, _ in self.shape(text.lower(), smcp=True)],
                [n + ".sc" for n in expected],
            )
        for pair in ["HY", "EA"]:
            self.assertNotIn("_".join(pair), self.order)
            self.assertEqual([n for n, _ in self.shape(pair, calt=False)], list(pair))
            for separator in [" ", "\u00a0", "-", "/", "."]:
                names = [n for n, _ in self.shape(separator.join(pair))]
                self.assertFalse(any(".join_" in name for name in names))
        for text in ["HY", "EA"]:
            for features in [{}, {"c2sc": True}]:
                shaped = self.shape(text, **features)
                a = pathops.Path()
                b = pathops.Path()
                self.glyphs[shaped[0][0]].draw(a.getPen())
                self.glyphs[shaped[1][0]].draw(b.getPen())
                b = b.transform(1, 0, 0, 1, shaped[0][1], 0)
                self.assertGreater(
                    abs(pathops.op(a, b, pathops.PathOp.INTERSECTION).area), 1
                )

    def test_six_circle_and_upright_nine(self):
        six = pathops.Path()
        nine = pathops.Path()
        self.glyphs["six"].draw(six.getPen())
        self.glyphs["nine"].draw(nine.getPen())
        # The lower 6 counter stays circular, without the shoulder intruding.
        for angle in range(0, 360, 15):
            theta = math.radians(angle)
            self.assertFalse(
                six.contains((268 + 153 * math.cos(theta), 210 + 153 * math.sin(theta)))
            )
            self.assertTrue(
                six.contains((268 + 160 * math.cos(theta), 210 + 160 * math.sin(theta)))
            )
        for y in [10, 100, 200, 300]:
            self.assertTrue(nine.contains((427, y)))
            self.assertTrue(nine.contains((487, y)))
            self.assertFalse(nine.contains((494, y)))
        self.assertFalse(nine.contains((268, 490)))

    def test_kerning(self):
        self.assertLess(
            sum(w for n, w in self.shape("AV")),
            sum(w for n, w in self.shape("AV", kern=False)),
        )
        self.assertLess(
            sum(w for n, w in self.shape("AV", c2sc=True)),
            sum(w for n, w in self.shape("AV", c2sc=True, kern=False)),
        )

    def test_coverage(self):
        cmap = self.font.getBestCmap()
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?&/+-=()":
            self.assertIn(ord(c), cmap)
        self.assertNotIn(
            ".notdef", [n for n, w in self.shape("CORINNE BAILEY RAE / THE SEA 2010")]
        )

    def test_bounds_and_metrics(self):
        for name in self.order:
            with self.subTest(glyph=name):
                width, lsb = self.font["hmtx"][name]
                self.assertGreater(width, 0)
                pen = BoundsPen(self.glyphs)
                self.glyphs[name].draw(pen)
                if pen.bounds:
                    x0, y0, x1, y1 = pen.bounds
                    self.assertGreaterEqual(y0, -180)
                    self.assertLessEqual(y1, 820)
                    self.assertGreaterEqual(x0, -1)
                    if name not in JOIN_FORMS or JOIN_FORMS[name]["target"] is None:
                        self.assertLessEqual(x1, width + 1)
                    self.assertLessEqual(abs(lsb - x0), 1)
        self.assertEqual(self.font["OS/2"].sCapHeight, 700)
        self.assertEqual(self.font["OS/2"].sxHeight, 518)

    def test_no_join_knockouts(self):
        # These points sit in joins that mixed contour winding previously knocked out.
        for name, point in [("N", (95, 650)), ("Y", (285, 310)), ("Q", (600, 70))]:
            p = pathops.Path()
            self.glyphs[name].draw(p.getPen())
            self.assertTrue(p.contains(point), name)
        p = pathops.Path()
        self.glyphs["O"].draw(p.getPen())
        self.assertFalse(p.contains((374, 350)), "O counter must remain open")

    def test_reference_details(self):
        def ink(name, point):
            p = pathops.Path()
            self.glyphs[name].draw(p.getPen())
            return p.contains(point)

        self.assertFalse(
            ink("R", (130, 310)), "R must have an open throat beside its stem"
        )
        self.assertTrue(ink("R", (260, 240)), "R bowl must flow into its diagonal leg")
        self.assertTrue(ink("N", (360, 670)), "N needs its upper horizontal return")
        self.assertFalse(ink("N", (583, -10)), "N must not have a baseline spur")
        self.assertFalse(ink("N_N", (360, 670)), "First N must have no upper return")
        self.assertTrue(ink("N_N", (903, 670)), "Second N needs its upper return")
        self.assertFalse(ink("N_N", (575, 350)), "The two Ns must remain separated")
        self.assertFalse(ink("N_N.sc", (430, 260)), "Small-cap NN must keep its gap")
        self.assertTrue(
            ink("N_N.sc", (420, 260)), "First small N stem must stay intact"
        )
        self.assertTrue(
            ink("N_N.sc", (440, 260)), "Second small N stem must stay intact"
        )
        self.assertFalse(
            ink("B_A", (398, 150)), "BA must keep the natural background opening"
        )
        self.assertTrue(ink("E_Y", (443, 667)), "EY must meet at the top bar")
        self.assertTrue(
            ink("E_Y", (460, 640)), "EY must not have a notch under its join"
        )
        self.assertTrue(
            ink("E_Y.sc", (340, 465)), "Small-cap EY must also have a full-depth join"
        )

    def test_zero_and_spiral_s(self):
        self.assertNotEqual(self.font["hmtx"]["zero"][0], self.font["hmtx"]["O"][0])
        self.assertEqual(self.shape("0", zero=True)[0][0], "zero.slash")
        self.assertEqual(
            [n for n, w in self.shape("SEA")], ["S", "E.join_A", "A.chain"]
        )
        self.assertEqual(
            [n for n, w in self.shape("sea", smcp=True)],
            ["S.sc", "E.join_A.sc", "A.chain.sc"],
        )
        s = pathops.Path()
        self.glyphs["S"].draw(s.getPen())
        self.assertAlmostEqual(s.bounds[1], -12, delta=1)
        self.assertAlmostEqual(s.bounds[3], 712, delta=1)
        self.assertFalse(s.contains((177, 264)), "The spiral’s counter must stay open")
        self.assertTrue(
            s.contains((192, 168)), "The inward spiral return must be present"
        )

    def test_h_curved_bridge_without_loop(self):
        h = pathops.Path()
        self.glyphs["H"].draw(h.getPen())
        self.assertTrue(
            h.contains((100, 285)), "H bridge must curve out of the lower left stem"
        )
        self.assertTrue(
            h.contains((510, 440)), "H bridge must rise into the right stem"
        )
        self.assertFalse(h.contains((200, 70)), "H must not have a bottom-left loop")
        self.assertEqual(h.bounds, (38, 0, 580, 700))

    def test_smallcap_weight_and_height(self):
        for name in ["H.sc", "I.sc", "E.sc"]:
            pen = BoundsPen(self.glyphs)
            self.glyphs[name].draw(pen)
            self.assertAlmostEqual(pen.bounds[1], 0, delta=0.1)
            self.assertAlmostEqual(pen.bounds[3], 518, delta=0.1)
        pen = BoundsPen(self.glyphs)
        self.glyphs["I.sc"].draw(pen)
        self.assertGreater(pen.bounds[2] - pen.bounds[0], 66 * 0.74 + 6)

    def test_caret_positions(self):
        table = self.font["GDEF"].table.LigCaretList
        entries = dict(zip(table.Coverage.glyphs, table.LigGlyph, strict=True))
        for sequence in LIGS | DLIGS:
            for suffix in ["", ".sc"]:
                positions = [
                    v.Coordinate
                    for v in entries["_".join(sequence) + suffix].CaretValue
                ]
                self.assertEqual(len(positions), len(sequence) - 1)
                self.assertEqual(positions, sorted(set(positions)))

    def test_variable_default_and_extremes(self):
        variable = TTFont(ROOT / "fonts/Bathys-Variable.otf")
        axis = variable["fvar"].axes[0]
        self.assertEqual(
            (axis.axisTag, axis.minValue, axis.defaultValue, axis.maxValue),
            ("wdth", 85, 100, 115),
        )
        default = instantiateVariableFont(variable, {"wdth": 100}, inplace=False)
        gs = default.getGlyphSet()
        for name in self.order:
            left = pathops.Path()
            right = pathops.Path()
            self.glyphs[name].draw(left.getPen())
            gs[name].draw(right.getPen())
            difference = pathops.op(left, right, pathops.PathOp.XOR)
            self.assertLess(abs(difference.area), 0.01, name)
            self.assertEqual(self.font["hmtx"][name], default["hmtx"][name], name)
        for text in ["CORINNE BAILEY RAE", "AVATAR FABLE PALACE"]:
            for width in [85, 92.5, 107.5, 115]:
                f = hb.Font(hb.Face((ROOT / "fonts/Bathys-Variable.otf").read_bytes()))
                f.set_variations({"wdth": width})
                buf = hb.Buffer()
                buf.add_str(text)
                buf.guess_segment_properties()
                hb.shape(f, buf)
                self.assertTrue(all(pos.x_advance > 0 for pos in buf.glyph_positions))
                self.assertAlmostEqual(
                    sum(pos.x_advance for pos in buf.glyph_positions),
                    sum(w for n, w in self.shape(text)) * width / 100,
                    delta=12,
                )

    def test_webfont_matches_otf(self):
        web = TTFont(ROOT / "fonts/Bathys-Regular.woff2")
        self.assertEqual(web["head"].modified, self.font["head"].modified)
        self.assertEqual(web.getBestCmap(), self.font.getBestCmap())
        self.assertEqual(web["hmtx"].metrics, self.font["hmtx"].metrics)
        for table in ["CFF ", "GSUB", "GPOS"]:
            self.assertEqual(web.getTableData(table), self.font.getTableData(table))


if __name__ == "__main__":
    unittest.main(verbosity=2)
