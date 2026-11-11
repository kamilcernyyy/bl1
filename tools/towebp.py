import sys
from PIL import Image
src_dir, dst_dir = sys.argv[1], sys.argv[2]
plan = {
    "hero": [1920, 1200, 800],
    "street": [1600, 800], "bungalow": [1600, 800], "garden": [1600, 800],
    "aerial": [1600, 800], "entry": [1600, 800],
}
only = sys.argv[3:] or list(plan)
for name in only:
    im = Image.open(f"{src_dir}/{name}.png").convert("RGB")
    for w in plan[name]:
        h = round(im.height * w / im.width)
        out = im.resize((w, h), Image.LANCZOS)
        q = 74 if w >= 1600 else 76
        out.save(f"{dst_dir}/{name}-{w}.webp", "WEBP", quality=q, method=6)
        print(name, w, h)
