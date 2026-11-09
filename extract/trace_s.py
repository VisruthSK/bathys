# /// script
# requires-python = ">=3.13"
# dependencies = ["pillow==13.0.0", "potracer==0.0.4", "fonttools==4.68.0"]
# ///
"""Extract the subtitle S silhouette for comparison with the finished S.svg."""

from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from potrace import Bitmap

ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
GENERATED.mkdir(exist_ok=True)
SCALE = 12
CROP = (194, 452, 240, 514)
image = Image.open(ROOT / "reference/sea.jpg").crop(CROP)
r, g, b = image.split()
light = ImageChops.darker(ImageChops.darker(r, g), b)
light = light.resize((46 * SCALE, 62 * SCALE), Image.Resampling.LANCZOS)
light = light.filter(ImageFilter.GaussianBlur(4))
mask = light.point(lambda value: 0 if value > 180 else 255)
pixels = mask.load()
for y in range(mask.height):
    source_y = CROP[1] + (y + 0.5) / SCALE
    # E joins S at the shoulder and again near the baseline. Separate only
    # those contacts along the continuation of S's visible outer curvature.
    if source_y < 482.5:
        right = 236.7
    else:
        right = 238
    # One smooth outer curve across the two E contact points.
    if 482 <= source_y <= 502.5:
        lo, hi = 0.0, 1.0
        for _ in range(20):
            t = (lo + hi) / 2
            curve_y = (
                (1 - t) ** 3 * 482
                + 3 * (1 - t) ** 2 * t * 488
                + 3 * (1 - t) * t * t * 495
                + t**3 * 502.5
            )
            if curve_y < source_y:
                lo = t
            else:
                hi = t
        right = (
            (1 - t) ** 3 * 235.8
            + 3 * (1 - t) ** 2 * t * 240.1
            + 3 * (1 - t) * t * t * 239.6
            + t**3 * 234.8
        )
    for x in range(mask.width):
        if CROP[0] + (x + 0.5) / SCALE > right:
            pixels[x, y] = 255
ImageDraw.floodfill(mask, (342, 42), 128)
mask = mask.point(lambda value: 0 if value == 128 else 255)
mask.save(GENERATED / "S-mask.png")
contours = Bitmap(mask).trace(
    turdsize=64, alphamax=1.15, opticurve=True, opttolerance=4
)
pen = SVGPathPen(None, ntos=lambda n: f"{n:.4f}".rstrip("0").rstrip("."))
scaled = TransformPen(pen, (1 / SCALE, 0, 0, 1 / SCALE, CROP[0], CROP[1]))


def point(p):
    return p.x, p.y


for contour in contours:
    scaled.moveTo(point(contour.start_point))
    for segment in contour.segments:
        if segment.is_corner:
            scaled.lineTo(point(segment.c))
            scaled.lineTo(point(segment.end_point))
        else:
            scaled.curveTo(
                point(segment.c1), point(segment.c2), point(segment.end_point)
            )
    scaled.closePath()
(GENERATED / "S-extracted.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="194 452 46 62">'
    f'<path d="{pen.getCommands()}"/></svg>\n',
    encoding="utf-8",
)
print("Extracted generated/S-extracted.svg; the finished source is reference/S.svg.")
