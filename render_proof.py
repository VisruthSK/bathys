"""Raster proof using HarfBuzz shaping and FreeType's actual OTF rasterizer."""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parent
data=(ROOT/'fonts/Bathys-Regular.otf').read_bytes()
font=TTFont(ROOT/'fonts/Bathys-Regular.otf')
order=font.getGlyphOrder()
# A temporary PUA cmap exposes individual glyphs to FreeType; shipping font is unchanged.
for table in font['cmap'].tables:
    if table.isUnicode():table.cmap.update({0xE000+i:n for i,n in enumerate(order)})

if __name__ == '__main__':
    renderfont=BytesIO();font.save(renderfont);renderdata=renderfont.getvalue()
    im=Image.new('RGB',(1600,1920),'#eee8d8');draw=ImageDraw.Draw(im)
    def text(s,x,y,size,colour='#102b2b',features=None):
        f=hb.Font(hb.Face(data));buf=hb.Buffer();buf.add_str(s);buf.guess_segment_properties();hb.shape(f,buf,features or {})
        ft=ImageFont.truetype(BytesIO(renderdata),size)
        for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
            draw.text((x+pos.x_offset*size/1000,y-pos.y_offset*size/1000),chr(0xE000+info.codepoint),font=ft,fill=colour,anchor='ls')
            x+=pos.x_advance*size/1000
    draw.rectangle((0,0,1600,980),fill='#102b2b')
    for s,y in [('CORINNE',260),('BAILEY',510),('RAE',760)]:text(s,80,y,320,'#eee8d8')
    text('THE SEA / THE LOVE EP',85,880,65,'#d7b17c',{'c2sc':True})
    for s,y in [('ABCDEFG',1130),('HIJKLMN',1270),('OPQRSTU',1410),('VWXYZ 012345',1550)]:text(s,60,y,145)
    text('CO OR COR BA RA',60,1680,110)
    text('abcdefghijklmnopqrstuvwxyz',60,1770,95,features={'smcp':True})
    text('WE ORBIT THE SAME SUN.',60,1870,78)
    im.save(ROOT/'svg/Bathys-rendered-proof.png')
print('Rendered svg/Bathys-rendered-proof.png from the compiled OTF.')

