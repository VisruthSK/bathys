"""Bathys: hand-drawn cubic display capitals, compiled to CFF OpenType."""
from pathlib import Path
import json
import math
import html
import pathops
import uharfbuzz as hb
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'fonts'
SVG = ROOT / 'svg'
OUT.mkdir(exist_ok=True)
SVG.mkdir(exist_ok=True)
GLYPHS = {}

def path(d):
    p = pathops.Path()
    parse_path(d, p.getPen())
    return p

def poly(points):
    return path('M' + ' L'.join(f'{x},{y}' for x,y in points) + ' Z')

def rect(x,y,w,h):
    return poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)])

def bar(x,y,X,Y,t=66):
    dx,dy=X-x,Y-y
    l=math.hypot(dx,dy)
    a,b=-dy/l*t/2,dx/l*t/2
    return poly([(x+a,y+b),(X+a,Y+b),(X-a,Y-b),(x-a,y-b)])

def union(*parts):
    p=pathops.Path()
    for part in parts:
        p=pathops.op(p,part,pathops.PathOp.UNION,fix_winding=True)
    return p

def difference(a,b):
    return pathops.op(a,b,pathops.PathOp.DIFFERENCE)

def ellipse(cx,cy,rx,ry):
    k=.5522847498307936
    return path(f'M{cx+rx},{cy} C{cx+rx},{cy+k*ry} {cx+k*rx},{cy+ry} {cx},{cy+ry} C{cx-k*rx},{cy+ry} {cx-rx},{cy+k*ry} {cx-rx},{cy} C{cx-rx},{cy-k*ry} {cx-k*rx},{cy-ry} {cx},{cy-ry} C{cx+k*rx},{cy-ry} {cx+rx},{cy-k*ry} {cx+rx},{cy} Z')

def transform(p,scale=1,dx=0,dy=0):
    q=pathops.Path()
    p.draw(TransformPen(q.getPen(),(scale,0,0,scale,dx,dy)))
    return q

def add(name,p,width):
    GLYPHS[name]=(p,round(width))

def alphabet(t=66):
    g={}
    def put(c,p,w):g[c]=(p,w)
    # The asymmetric A is taken directly from the user's existing Glyphr drawing.
    source=json.loads(next(ROOT.glob('*.gs2')).read_text())
    contours=[]
    for shape in source['glyphs']['glyph-0x41']['shapes']:
        contours.append(poly([(v['p']['coord']['x']*700/1480,v['p']['coord']['y']*700/1480) for v in shape['pathPoints']]))
    put('A',difference(contours[0],contours[1]),636)
    stem=rect(38,0,t,700)
    def bowl(top,bottom,right):
        mid=(top+bottom)/2
        return path(f'M38,{bottom} L{right-190},{bottom} C{right-70},{bottom} {right},{mid-90} {right},{mid} C{right},{mid+90} {right-70},{top} {right-190},{top} L38,{top} Z')
    def hollow(top,bottom,right):
        return difference(bowl(top,bottom,right),bowl(top-t,bottom+t,right-t))
    put('B',union(stem,hollow(700,354,440),hollow(398,0,480)),520)
    ring=difference(ellipse(374,350,350,362),ellipse(374,350,350-t,362-t))
    put('O',ring,748)
    # Radial cuts leave clean, flat terminals on the open circular letters.
    cut=poly([(374,350),(900,770),(1000,350),(900,-70)])
    C=difference(ring,cut)
    put('C',C,707)
    D=path('M38,0 L240,0 C520,0 660,132 660,350 C660,568 520,700 240,700 L38,700 Z')
    Di=path(f'M{38+t},{t} L240,{t} C{520-t},{t} {660-t},155 {660-t},350 C{660-t},545 {520-t},{700-t} 240,{700-t} L{38+t},{700-t} Z')
    put('D',difference(D,Di),700)
    E=union(stem,rect(38,700-t,412,t),rect(38,326,354,t),rect(38,0,412,t))
    put('E',E,482)
    put('F',union(stem,rect(38,700-t,412,t),rect(38,326,354,t)),475)
    put('G',union(C,rect(420,315,276,t),rect(630,130,t,251)),748)
    put('H',union(stem,rect(514,0,t,700),rect(38,326,542,t)),618)
    put('I',rect(30,0,t,700),126)
    J=path(f'M380,700 L{380+t},700 L{380+t},185 C{380+t},50 345,-12 230,-12 C95,-12 24,65 24,195 L{24+t},195 C{24+t},105 135,{t-12} 230,{t-12} C325,{t-12} 380,100 380,185 Z')
    put('J',J,480)
    put('K',union(stem,bar(80,296,530,678,t),bar(270,464,550,20,t)),590)
    put('L',union(stem,rect(38,0,350,t)),417)
    put('M',union(stem,rect(648-t,0,t,700),poly([(38,700),(115,700),(343,275),(571,700),(648,700),(343,145)])),686)
    put('N',union(stem,rect(584-t,0,t,700),poly([(38,700),(116,700),(584,0),(506,0)])),622)
    P=union(stem,hollow(700,300,505))
    put('P',P,545)
    put('Q',union(ring,bar(468,186,730,-66,t)),760)
    put('R',union(stem,hollow(700,300,460),poly([(195,342),(275,342),(500,0),(420,0)])),532)
    S=path(f'M560,586 C513,666 427,712 308,712 C147,712 45,629 45,511 C45,395 141,348 293,310 C421,278 509,251 509,167 C509,92 434,54 326,54 C212,54 126,103 79,187 L24,151 C86,42 189,-12 326,-12 C479,-12 579,55 579,173 C579,299 471,345 321,383 C195,415 115,446 115,518 C115,590 185,646 307,646 C396,646 461,612 504,551 Z')
    put('S',S,612)
    put('T',union(rect(20,700-t,548,t),rect(294-t/2,0,t,700)),588)
    U=path(f'M38,700 L{38+t},700 L{38+t},238 C{38+t},116 175,54 302,54 C429,54 500,116 500,238 L500,700 L{500+t},700 L{500+t},238 C{500+t},77 470,-12 302,-12 C134,-12 38,77 38,238 Z')
    put('U',U,604)
    put('V',poly([(20,700),(94,700),(324,100),(554,700),(628,700),(360,0),(288,0)]),648)
    put('W',poly([(20,700),(91,700),(245,112),(420,700),(488,700),(663,112),(817,700),(888,700),(701,0),(626,0),(454,575),(282,0),(207,0)]),908)
    put('X',union(poly([(20,700),(100,700),(590,0),(510,0)]),poly([(510,700),(590,700),(100,0),(20,0)])),610)
    put('Y',union(poly([(20,700),(100,700),(285,365),(470,700),(550,700),(318,291),(252,291)]),rect(252,0,t,335)),570)
    put('Z',poly([(30,700),(567,700),(567,640),(113,t),(567,t),(567,0),(30,0),(30,60),(484,700-t),(30,700-t)]),597)
    return g

for c,(p,w) in alphabet().items():add(c,p,w)
for c,(p,w) in alphabet(77).items():add(c+'.sc',transform(p,.74),w*.74+10)
for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':add(c.lower(),*GLYPHS[c])
add('space',pathops.Path(),260)
add('nbspace',pathops.Path(),260)
add('.notdef',difference(rect(40,0,480,700),rect(100,60,360,580)),560)
# Numerals follow the same round bowls and unadorned terminals.
add('zero',*GLYPHS['O'])
add('one',union(rect(235,0,66,700),bar(88,546,268,670,66)),397)
add('two',path('M42,539 C65,650 160,712 292,712 C451,712 540,632 540,518 C540,430 493,374 399,297 L143,66 L550,66 L550,0 L38,0 L38,62 L354,346 C434,412 472,457 472,519 C472,598 409,646 292,646 C195,646 134,601 108,524 Z'),590)
add('three',union(difference(ellipse(285,522,245,190),ellipse(285,522,177,124)),difference(ellipse(285,180,265,192),ellipse(285,180,197,126))),590)
GLYPHS['three']=(difference(GLYPHS['three'][0],rect(-10,85,180,520)),590)
add('four',union(poly([(398,700),(475,700),(111,236),(550,236),(550,170),(28,170),(28,233)]),rect(410,0,66,700)),590)
add('five',path('M528,700 L528,634 L138,634 L123,395 C171,424 232,439 297,439 C454,439 550,353 550,219 C550,79 446,-12 285,-12 C173,-12 80,30 24,111 L78,153 C128,87 198,54 286,54 C406,54 481,116 481,219 C481,316 410,373 294,373 C218,373 152,348 101,307 L50,333 L74,700 Z'),590)
add('six',union(difference(ellipse(300,219,260,231),ellipse(300,219,192,165)),path('M40,219 C40,520 149,712 349,712 C422,712 477,693 523,663 L490,605 C451,631 406,646 349,646 C193,646 109,484 109,219 Z')),600)
add('seven',poly([(28,700),(568,700),(568,644),(235,0),(159,0),(492,634),(28,634)]),596)
add('eight',union(difference(ellipse(300,525,240,187),ellipse(300,525,172,121)),difference(ellipse(300,186,266,198),ellipse(300,186,198,132))),600)
add('nine',transform(GLYPHS['six'][0],-1,600,700),600)
for name,p,w in [('period',ellipse(65,32,34,34),130),('comma',poly([(35,68),(106,68),(100,0),(49,-110),(16,-110),(44,0),(35,0)]),140),('colon',union(ellipse(65,32,34,34),ellipse(65,443,34,34)),130),('semicolon',union(ellipse(65,443,34,34),poly([(35,68),(106,68),(100,0),(49,-110),(16,-110),(44,0)])),140),('hyphen',rect(35,310,240,58),310),('endash',rect(35,310,480,58),550),('emdash',rect(35,310,760,58),830),('quotesingle',rect(40,532,55,168),135),('quotedbl',union(rect(35,532,55,168),rect(150,532,55,168)),240),('slash',bar(45,-20,390,720,60),435),('exclam',union(rect(45,190,64,510),ellipse(77,32,34,34)),154),('question',path('M28,541 C42,653 129,712 247,712 C381,712 463,640 463,532 C463,445 414,401 347,354 C277,305 254,272 254,190 L188,190 C188,302 221,348 307,408 C367,451 395,480 395,533 C395,603 341,646 246,646 C159,646 108,607 95,530 Z'),500),('ampersand',path('M525,0 L440,0 L145,341 C80,412 53,462 53,530 C53,637 135,712 250,712 C365,712 442,642 442,543 C442,452 383,395 267,330 L167,273 C106,237 78,204 78,157 C78,93 132,54 213,54 C353,54 450,183 479,354 L545,343 C508,126 388,-12 211,-12 C90,-12 10,51 10,153 C10,226 48,278 134,327 L237,386 C333,440 375,484 375,543 C375,604 327,646 251,646 C173,646 120,600 120,534 C120,486 145,446 197,388 Z'),580),('parenleft',path('M240,760 C145,652 93,511 93,350 C93,189 145,48 240,-60 L162,-60 C73,47 27,191 27,350 C27,509 73,653 162,760 Z'),280)]:add(name,p,w)
add('parenright',transform(GLYPHS['parenleft'][0],-1,280,700),280)
add('plus',union(rect(40,315,400,60),rect(210,145,60,400)),480)
add('equal',union(rect(40,230,400,60),rect(40,410,400,60)),480)
add('question',union(GLYPHS['question'][0],ellipse(221,32,34,34)),500)
for name,target in [('quoteleft','quotesingle'),('quoteright','quotesingle'),('quotedblleft','quotedbl'),('quotedblright','quotedbl')]:add(name,*GLYPHS[target])

# Interlocking positions are drawn compositions, with their intersections united.
LIGS={'COR':([0,355,820],1352),'CO':([0,355],1080),'OR':([0,465],997),'BA':([0,210],846),'RA':([0,235],871)}
DLIGS={'OO':([0,545],1293),'OC':([0,545],1252),'RO':([0,460],1208),'LA':([0,345],981)}
for seq,(positions,width) in (LIGS|DLIGS).items():
    for suffix,scale in [('',1),('.sc',.74)]:
        parts=[transform(GLYPHS[c+suffix][0],1,x*scale) for c,x in zip(seq,positions)]
        add('_'.join(seq)+suffix,union(*parts),width*scale)

chars={32:'space',160:'nbspace'}
chars.update({ord(c):c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'})
chars.update({ord(c):n for c,n in zip('0123456789',['zero','one','two','three','four','five','six','seven','eight','nine'])})
chars.update({ord(c):n for c,n in {'!':'exclam','?':'question','.':'period',',':'comma',':':'colon',';':'semicolon','-':'hyphen','–':'endash','—':'emdash',"'":'quotesingle','"':'quotedbl','/':'slash','&':'ampersand','(':'parenleft',')':'parenright','+':'plus','=':'equal','‘':'quoteleft','’':'quoteright','“':'quotedblleft','”':'quotedblright'}.items()})
order=['.notdef']+[n for n in GLYPHS if n!='.notdef']
fb=FontBuilder(1000,isTTF=False)
fb.setupGlyphOrder(order)
fb.setupCharacterMap(chars)
cs={}
for n,(p,w) in GLYPHS.items():
    pen=T2CharStringPen(w,None,roundTolerance=.25)
    p.draw(pen)
    cs[n]=pen.getCharString()
fb.setupCFF('Bathys-Regular',{'FullName':'Bathys Regular','FamilyName':'Bathys','Weight':'Regular','version':'1.000','Notice':'Custom reference study; not an official album typeface.'},cs,{'BlueValues':[-12,0,700,712],'OtherBlues':[-110,-100],'StdHW':66,'StdVW':66})
fb.setupHorizontalMetrics({n:(w,round(p.bounds[0]) if len(p) else 0) for n,(p,w) in GLYPHS.items()})
fb.setupHorizontalHeader(ascent=820,descent=-180,lineGap=80)
fb.setupNameTable({'familyName':'Bathys','styleName':'Regular','uniqueFontIdentifier':'Bathys-Regular-1.000','fullName':'Bathys Regular','psName':'Bathys-Regular','version':'Version 1.000','description':'Geometric interlocking display capitals and optical small capitals. Album-reference reconstruction and alphabet extension.'})
fb.setupOS2(version=4,sTypoAscender=820,sTypoDescender=-180,sTypoLineGap=80,usWinAscent=820,usWinDescent=180,sCapHeight=700,sxHeight=518,usWeightClass=400,fsType=0,fsSelection=0xC0)
fb.setupPost()
fea=['languagesystem DFLT dflt;','languagesystem latn dflt;']
for tag,letters in [('smcp','abcdefghijklmnopqrstuvwxyz'),('c2sc','ABCDEFGHIJKLMNOPQRSTUVWXYZ')]:
    fea.append(f'feature {tag} {{')
    for c in letters:fea.append(f'sub {c} by {c.upper()}.sc;')
    fea.append(f'}} {tag};')
# Normalize capitals aliases only after the small-cap substitutions.
fea.append('feature calt {')
for c in 'abcdefghijklmnopqrstuvwxyz':fea.append(f'sub {c} by {c.upper()};')
fea.append('} calt;')
for tag,ligs in [('liga',LIGS),('dlig',DLIGS)]:
    fea.append(f'feature {tag} {{')
    for seq in sorted(ligs,key=len,reverse=True):
        for suffix in ['', '.sc']:
            fea.append(f'sub {" ".join(c+suffix for c in seq)} by {"_".join(seq)+suffix};')
    fea.append(f'}} {tag};')
kerns={'AV':-65,'AW':-48,'AY':-65,'AT':-50,'TA':-75,'VA':-65,'WA':-50,'YA':-72,'TO':-42,'OT':-42,'YO':-52,'OY':-52,'VO':-35,'OV':-35,'WO':-24,'OW':-24,'FA':-48,'PA':-40,'LT':-35,'LY':-48,'AE':-60,'NN':-40,'IN':-40,'NE':-40,'RI':-6,'IL':-45,'LE':-40,'EY':-65}
fea.append('feature kern {')
for pair,v in kerns.items():
    fea.append(f'pos {pair[0]} {pair[1]} {v};')
    fea.append(f'pos {pair[0]}.sc {pair[1]}.sc {round(v*.74)};')
for left,right,value in [('C_O_R','I',-12),('B_A','I',-55),('R_A','E',-60)]:
    fea.extend([f'pos {left} {right} {value};',f'pos {left}.sc {right}.sc {round(value*.74)};'])
fea.append('} kern;')
feature_text='\n'.join(fea)
(ROOT/'Bathys.fea').write_text(feature_text)
addOpenTypeFeaturesFromString(fb.font,feature_text)
fb.font['head'].fontRevision=1.0
fb.save(OUT/'Bathys-Regular.otf')
web=TTFont(OUT/'Bathys-Regular.otf');web.flavor='woff2';web.save(OUT/'Bathys-Regular.woff2')

def shape(text,features=None):
    font=hb.Font(hb.Face((OUT/'Bathys-Regular.otf').read_bytes()))
    buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
    hb.shape(font,buf,features or {})
    return [(order[i.codepoint],p.x_advance,p.x_offset,p.y_offset) for i,p in zip(buf.glyph_infos,buf.glyph_positions)]

def svg_text(text,x,y,size,fill,features=None):
    result=[];scale=size/1000
    for name,advance,dx,dy in shape(text,features):
        pen=SVGPathPen(None);GLYPHS[name][0].draw(pen)
        result.append(f'<path fill="{fill}" d="{pen.getCommands()}" transform="translate({x+dx*scale:.3f} {y-dy*scale:.3f}) scale({scale} {-scale})"/>')
        x+=advance*scale
    return ''.join(result)

def label(text,x,y):return f'<text x="{x}" y="{y}" fill="#9eafa8" font-family="sans-serif" font-size="12" letter-spacing="2">{html.escape(text)}</text>'
def write_svg(name,body,w,h):
    (SVG/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>Bathys — {html.escape(name)}</title>{body}</svg>',encoding='utf-8')

body='<rect width="1400" height="1800" fill="#0d2425"/><circle cx="1190" cy="300" r="350" fill="none" stroke="#39504a"/><circle cx="1190" cy="300" r="285" fill="none" stroke="#39504a"/>'
body+=label('BATHYS / A STUDY IN CIRCLES, SPACE & SOUND',80,70)
body+=svg_text('BATHYS',70,305,240,'#eee6cf')
body+=label('01 / THE REFERENCE LETTERING',80,390)
for s,y in [('CORINNE',600),('BAILEY',792),('RAE',984)]:body+=svg_text(s,78,y,250,'#eee6cf')
body+=svg_text('THE SEA / THE LOVE EP',85,1070,46,'#d5ac72',{'smcp':True,'c2sc':True})
body+=label('02 / AFTER THE LAST LIGHT',80,1190)
for s,y in [('WE ORBIT',1325),('THE SAME SUN.',1440)]:body+=svg_text(s,80,y,132,'#eee6cf')
body+=svg_text('and carry the sea into the stars',85,1555,49,'#d5ac72',{'smcp':True})
body+=label('CUBIC OUTLINES / INTERLOCKING LIGATURES / OPTICAL SMALL CAPITALS',80,1700)
write_svg('Bathys-poster.svg',body,1400,1800)
body='<rect width="1400" height="1600" fill="#f4eedf"/>'
body+=label('BATHYS / COMPLETE CHARACTER & SPACING PROOF',65,55)
for row,y in [('ABCDEFG',200),('HIJKLMN',350),('OPQRSTU',500),('VWXYZ',650),('0123456789',800)]:body+=svg_text(row,60,y,155,'#172d2b')
body+=svg_text('.,:;!? & / + = ( )',65,920,100,'#172d2b')
body+=label('OPTICAL SMALL CAPS / LOWERCASE INPUT + SMCP',65,990)
body+=svg_text('abcdefghijklmnopqrstuvwxyz',65,1070,86,'#172d2b',{'smcp':True})
body+=label('DEFAULT LIGATURES / CO  OR  COR  BA  RA',65,1160)
body+=svg_text('CO OR COR BA RA',65,1260,111,'#172d2b')
body+=label('DISCRETIONARY / OO  OC  RO  LA',65,1340)
body+=svg_text('OO OC RO LA',65,1440,111,'#172d2b',{'dlig':True})
body+=svg_text('AVATAR  WAVE  TOY  NOON  MINIMUM',65,1530,60,'#172d2b')
write_svg('Bathys-glyph-proof.svg',body,1400,1600)
# Each glyph is independently editable and uses font-coordinate cubic outlines.
glyphdir=SVG/'glyphs';glyphdir.mkdir(exist_ok=True)
for n,(p,w) in GLYPHS.items():
    if not len(p):continue
    pen=SVGPathPen(None);p.draw(pen)
    filename='lower-'+n if len(n)==1 and n.islower() else n
    (glyphdir/f'{filename}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -820 {w+40} 1020"><path transform="scale(1,-1)" d="{pen.getCommands()}"/></svg>')
(ROOT/'glyph-data.json').write_text(json.dumps({'upm':1000,'capHeight':700,'smallCapHeight':518,'glyphs':{n:{'advance':w,'bounds':list(p.bounds) if len(p) else None} for n,(p,w) in GLYPHS.items()},'ligatures':list(LIGS),'discretionary':list(DLIGS)},indent=2))
print(f'Built {len(GLYPHS)} glyphs, OTF, WOFF2, outlined SVG proofs and individual glyph SVGs.')

if __name__=='__main__':
    print('CORINNE:',shape('CORINNE'))
