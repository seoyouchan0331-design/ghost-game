# 암시장 밤 배경(통째로) + 노점 건물 4채 → assets/market_bg.png, assets/market_booths.png + 좌표 JSON
import json, sys, os, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "adv")); from keying import key
im = Image.open("bg_source.jpg").convert("RGB"); im = im.resize((round(im.width * 340 / im.height), 340), Image.BOX); im.save("../../assets/market_bg.png")
a = np.asarray(Image.open("booths_source.jpg").convert("RGB")).astype(int); m = key(a, 26, 3000)
m = ndimage.binary_opening(m, iterations=1)
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4)); objs = ndimage.find_objects(lab); sz = ndimage.sum(m, lab, range(1, n + 1))
ids = [i + 1 for i, s in sorted(enumerate(sz), key=lambda t: -t[1]) if s > 400]; bodies = sorted(ids[:4], key=lambda i: objs[i - 1][1].start)
cx = [(objs[i - 1][1].start + objs[i - 1][1].stop) / 2 for i in bodies]; owner = {b: k for k, b in enumerate(bodies)}
for i in ids[4:]: c = (objs[i - 1][1].start + objs[i - 1][1].stop) / 2; owner[i] = int(np.argmin([abs(c - x) for x in cx]))
H = 78; ps = []
for k in range(4):
    sub = np.isin(lab, [i for i, o in owner.items() if o == k]) & m; ys, xs = np.where(sub)
    p = Image.fromarray(np.dstack([a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8), (sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1] * 255).astype(np.uint8)]))
    p = p.resize((round(p.width * H / p.height), H), Image.BOX); px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); ps.append(Image.fromarray(px))
x = 0; at = Image.new("RGBA", (sum(p.width + 2 for p in ps), H)); meta = {}
for nm, p in zip(["cook", "merchant", "spirit", "smith"], ps): at.paste(p, (x, 0)); meta[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/market_booths.png"); print("const BOOTHS = " + json.dumps(meta, separators=(",", ":")) + ";")
