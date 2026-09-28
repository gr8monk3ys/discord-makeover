"""Server icon in the Field Notebook style: forest-ink serif initial on night paper."""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
NIGHT, PEN, HAIRLINE = (17, 19, 23), (66, 169, 121), (41, 44, 50)

img = Image.new("RGB", (SIZE, SIZE), NIGHT)

# the paper grain: 3.5% noise, same as the site
rng = random.Random(7)
px = img.load()
for y in range(SIZE):
    for x in range(SIZE):
        n = int((rng.random() - 0.5) * 255 * 0.07)
        r, g, b = NIGHT
        px[x, y] = (r + n, g + n, b + n)

d = ImageDraw.Draw(img)
# a sand hairline ring, inset so it survives Discord's circle crop
inset = 96
d.ellipse([inset, inset, SIZE - inset, SIZE - inset], outline=HAIRLINE, width=6)

font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 600)
text = "L"
box = d.textbbox((0, 0), text, font=font)
w, h = box[2] - box[0], box[3] - box[1]
d.text(((SIZE - w) / 2 - box[0], (SIZE - h) / 2 - box[1] - 10), text, font=font, fill=PEN)

out = Path(__file__).with_name("server-icon.png")
img.save(out)
print(out)
