"""Copy only public site files into dist/: python3 extract/publish.py."""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dist"
PUBLIC_FILES = (
    "index.html",
    "404.html",
    "specimen.css",
    "specimen.js",
    "specimen-data.js",
    "_headers",
    "_redirects",
    "fonts/Bathys-Regular.otf",
    "fonts/Bathys-Regular.woff2",
    "fonts/Bathys-Variable.otf",
    "fonts/Bathys-Variable.woff2",
    "assets/sea.jpg",
    "assets/LoveEP.jpg",
    "assets/icon.png",
)


def publish():
    # Never follow a redirected output directory when clearing old artifacts.
    if OUTPUT.resolve() != ROOT / "dist":
        raise ValueError("dist must resolve to the workspace's dist directory")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    for name in PUBLIC_FILES:
        target = OUTPUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return OUTPUT


if __name__ == "__main__":
    print(f"Published {len(PUBLIC_FILES)} public files to {publish()}")
