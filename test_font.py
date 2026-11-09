"""Structural and real-shaping checks against the distributed binaries."""
import unittest
from pathlib import Path
import uharfbuzz as hb
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parent

class FontProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font=TTFont(ROOT/'fonts/Bathys-Regular.otf',checkChecksums=2)
        cls.glyphs=cls.font.getGlyphSet()
        cls.order=cls.font.getGlyphOrder()
        cls.hbfont=hb.Font(hb.Face((ROOT/'fonts/Bathys-Regular.otf').read_bytes()))

    def shape(self,text,**features):
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(self.hbfont,b,features)
        return [(self.order[i.codepoint],p.x_advance) for i,p in zip(b.glyph_infos,b.glyph_positions)]

    def test_reference_word(self):
        self.assertEqual([n for n,w in self.shape('CORINNE')],['C_O_R','I','N','N','E'])

    def test_each_ligature_and_switch(self):
        for seq in ['CO','OR','COR','BA','RA']:
            with self.subTest(seq=seq):
                self.assertEqual(self.shape(seq)[0][0],'_'.join(seq))
                self.assertEqual([n for n,w in self.shape(seq,liga=False)],list(seq))

    def test_discretionary(self):
        for seq in ['OO','OC','RO','LA']:
            self.assertEqual([n for n,w in self.shape(seq)],list(seq))
            self.assertEqual([n for n,w in self.shape(seq,dlig=True)],['_'.join(seq)])

    def test_smallcaps(self):
        self.assertEqual([n for n,w in self.shape('corinne',smcp=True)],['C_O_R.sc','I.sc','N.sc','N.sc','E.sc'])
        self.assertEqual([n for n,w in self.shape('CORINNE',c2sc=True)],['C_O_R.sc','I.sc','N.sc','N.sc','E.sc'])
        self.assertEqual(self.shape('corinne'),self.shape('CORINNE'))
        for seq in ['CO','OR','COR','BA','RA']:
            self.assertEqual(self.shape(seq.lower(),smcp=True)[0][0],'_'.join(seq)+'.sc')
        self.assertEqual(self.shape('oo',smcp=True,dlig=True)[0][0],'O_O.sc')

    def test_word_boundaries(self):
        self.assertEqual([n for n,w in self.shape('C O R')],['C','space','O','space','R'])

    def test_kerning(self):
        self.assertLess(sum(w for n,w in self.shape('AV')),sum(w for n,w in self.shape('AV',kern=False)))
        self.assertLess(sum(w for n,w in self.shape('AV',c2sc=True)),sum(w for n,w in self.shape('AV',c2sc=True,kern=False)))

    def test_coverage(self):
        cmap=self.font.getBestCmap()
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?&/+-=()':
            self.assertIn(ord(c),cmap)
        self.assertNotIn('.notdef',[n for n,w in self.shape('CORINNE BAILEY RAE / THE SEA 2010')])

    def test_bounds_and_metrics(self):
        for name in self.order:
            with self.subTest(glyph=name):
                width,lsb=self.font['hmtx'][name]
                self.assertGreater(width,0)
                pen=BoundsPen(self.glyphs);self.glyphs[name].draw(pen)
                if pen.bounds:
                    x0,y0,x1,y1=pen.bounds
                    self.assertGreaterEqual(y0,-180);self.assertLessEqual(y1,820)
                    self.assertGreaterEqual(x0,-1);self.assertLessEqual(x1,width+1)
                    self.assertLessEqual(abs(lsb-x0),1)
        self.assertEqual(self.font['OS/2'].sCapHeight,700)
        self.assertEqual(self.font['OS/2'].sxHeight,518)

    def test_no_join_knockouts(self):
        # These points sit in joins that mixed contour winding previously knocked out.
        for name,point in [('N',(95,650)),('R',(250,330)),('Y',(285,310)),('Q',(600,70))]:
            p=pathops.Path();self.glyphs[name].draw(p.getPen())
            self.assertTrue(p.contains(point),name)
        p=pathops.Path();self.glyphs['O'].draw(p.getPen())
        self.assertFalse(p.contains((374,350)),'O counter must remain open')

    def test_webfont_matches_otf(self):
        web=TTFont(ROOT/'fonts/Bathys-Regular.woff2')
        self.assertEqual(web.getBestCmap(),self.font.getBestCmap())
        self.assertEqual(web['hmtx'].metrics,self.font['hmtx'].metrics)
        for table in ['CFF ','GSUB','GPOS']:
            self.assertEqual(web.getTableData(table),self.font.getTableData(table))

if __name__=='__main__':unittest.main(verbosity=2)
