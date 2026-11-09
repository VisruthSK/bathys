"""Structural and real-shaping checks against the distributed binaries."""

import unittest
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from outlines import DLIGS, LIGS

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
            [n for n, w in self.shape("CORINNE")], ["C_O_R", "I", "N_N", "E"]
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

    def test_smallcaps(self):
        self.assertEqual(
            [n for n, w in self.shape("corinne", smcp=True)],
            ["C_O_R.sc", "I.sc", "N_N.sc", "E.sc"],
        )
        self.assertEqual(
            [n for n, w in self.shape("CORINNE", c2sc=True)],
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
                    self.assertGreaterEqual(y0, -260)
                    self.assertLessEqual(y1, 820)
                    self.assertGreaterEqual(x0, -1)
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
            ink("B_A", (411, 150)), "BA needs its small background opening"
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
        self.assertEqual([n for n, w in self.shape("SEA")], ["S", "E", "A"])
        self.assertEqual(
            [n for n, w in self.shape("sea", smcp=True)], ["S.sc", "E.sc", "A.sc"]
        )
        s = pathops.Path()
        self.glyphs["S"].draw(s.getPen())
        self.assertLess(
            s.bounds[1], -200, "S must keep the reference’s descending spiral"
        )
        self.assertFalse(s.contains((240, 117)), "The spiral’s counter must stay open")
        self.assertTrue(
            s.contains((260, -15)), "The inward spiral return must be present"
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
        for width in [85, 92.5, 107.5, 115]:
            f = hb.Font(hb.Face((ROOT / "fonts/Bathys-Variable.otf").read_bytes()))
            f.set_variations({"wdth": width})
            buf = hb.Buffer()
            buf.add_str("CORINNE BAILEY RAE")
            buf.guess_segment_properties()
            hb.shape(f, buf)
            self.assertTrue(all(pos.x_advance > 0 for pos in buf.glyph_positions))
            self.assertAlmostEqual(
                sum(pos.x_advance for pos in buf.glyph_positions),
                sum(w for n, w in self.shape("CORINNE BAILEY RAE")) * width / 100,
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
