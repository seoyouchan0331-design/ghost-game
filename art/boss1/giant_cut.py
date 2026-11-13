# 거대 골렘: 몸통 1·2페이즈(같은 틀로 잘라 겹치게), 양손 6자세, 잔해 → assets/giant.png + 좌표 JSON
import json, sys, os, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "adv")); from keying import key
def hard(p): px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px)
def load(f, thr=24): a = np.asarray(Image.open(f).convert("RGB")).astype(int); m = key(a, thr, 10 ** 9); m = ndimage.binary_opening(m, iterations=1); return a, m
def rgba(a, m): return Image.fromarray(np.dstack([a.astype(np.uint8), (m * 255).astype(np.uint8)]))
BH = 212; parts = {}; meta = {}
b1, m1 = load("body_source.jpg"); b2, m2 = load("body2_source.jpg")
ys, xs = np.where(m1 | m2); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1); k = BH / (box[3] - box[1])
for nm, a, m in (("body", b1, m1), ("body2", b2, m2)):
    p = rgba(a, m).crop(box); parts[nm] = hard(p.resize((round(p.width * k), BH), Image.BOX))
core = ((701 - box[0]) * k, (520 - box[1]) * k)                                  # 가슴 핵 위치 (그림에서 잰 값)
a, m = load("hands_source.jpg"); H, W = m.shape
for i, nm in enumerate(["R_open", "R_fist", "R_side", "L_open", "L_fist", "L_side"]):
    r, c = divmod(i, 3); s = (slice(r * H // 2, (r + 1) * H // 2), slice(c * W // 3, (c + 1) * W // 3)); sub = m[s]
    lb, n = ndimage.label(sub); sz = ndimage.sum(sub, lb, range(1, n + 1)); sub = np.isin(lb, [j + 1 for j, v in enumerate(sz) if v > 300])
    p = rgba(a[s], sub); p = p.crop(p.getbbox()); h = 58 if "open" in nm else 46 if "fist" in nm else 40
    parts[nm] = hard(p.resize((round(p.width * h / p.height), h), Image.BOX))
a, m = load("rubble_source.jpg"); p = rgba(a, m); p = p.crop(p.getbbox()); parts["rubble"] = hard(p.resize((230, round(p.height * 230 / p.width)), Image.BOX))
Wt = sum(p.width + 2 for p in parts.values()); Ht = max(p.height for p in parts.values()); at = Image.new("RGBA", (Wt, Ht)); x = 0
for nm, p in parts.items(): at.paste(p, (x, 0)); meta[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/giant.png"); meta["core"] = [round(core[0]), round(core[1])]
print("const GIANT = " + json.dumps(meta, separators=(",", ":")) + ";")
