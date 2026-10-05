"""Crops dashboard screenshots to the main content area so text is readable in the report."""
from pathlib import Path

from PIL import Image, ImageChops

FIG = Path(__file__).parent / "figures"
OUT = FIG / "cropped"
OUT.mkdir(exist_ok=True)

for path in sorted(FIG.glob("ss_*.png")):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # Sidebar: the left block whose background is not white; find where white content begins.
    y = int(h * 0.3)
    x_start = 0
    for x in range(w // 2):
        if im.getpixel((x, y)) == (255, 255, 255) and im.getpixel((min(x + 5, w - 1), y)) == (255, 255, 255):
            x_start = x
            break
    body = im.crop((x_start, int(110 * w / 2100), w, h))   # drop sidebar and the top "Deploy" bar
    bg = Image.new("RGB", body.size, (255, 255, 255))
    bbox = ImageChops.difference(body, bg).getbbox()
    if bbox:
        pad = 24
        body = body.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
                          min(bbox[2] + pad, body.width), min(bbox[3] + pad, body.height)))
    body.save(OUT / path.name)
    print(path.name, im.size, "->", body.size)
