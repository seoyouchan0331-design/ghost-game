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
# 손 6개: 칸을 똑같이 나누면 펼친 손가락이 옆 칸에 걸린다 → 줄마다 덩어리를 찾고, 큰 덩어리 3개(손)에 작은 조각을 가까운 쪽으로 붙인다
NM = ["R_open", "R_fist", "R_side", "L_open", "L_fist", "L_side"]
for r in range(2):
    s = (slice(r * H // 2, (r + 1) * H // 2), slice(0, W)); row = m[s]; lb, n = ndimage.label(ndimage.binary_dilation(row, iterations=3)); ob = ndimage.find_objects(lb); sz = ndimage.sum(row, lb, range(1, n + 1))
    ids = [j + 1 for j, v in sorted(enumerate(sz), key=lambda t: -t[1]) if v > 200]; bodies = sorted(ids[:3], key=lambda j: ob[j - 1][1].start)
    cxs = [(ob[j - 1][1].start + ob[j - 1][1].stop) / 2 for j in bodies]; own = {b: k for k, b in enumerate(bodies)}
    for j in ids[3:]: cc = (ob[j - 1][1].start + ob[j - 1][1].stop) / 2; own[j] = int(np.argmin([abs(cc - x) for x in cxs]))
    for c in range(3):
        nm = NM[r * 3 + c]; sub = np.isin(lb, [j for j, o in own.items() if o == c]) & row
        p = rgba(a[s], sub); p = p.crop(p.getbbox()); h = 104 if "open" in nm else 82 if "fist" in nm else 70   # 손은 크게 (보이드의 3배 넘게)
        parts[nm] = hard(p.resize((round(p.width * h / p.height), h), Image.BOX))
a, m = load("rubble_source.jpg"); p = rgba(a, m); p = p.crop(p.getbbox()); parts["rubble"] = hard(p.resize((230, round(p.height * 230 / p.width)), Image.BOX))
Wt = sum(p.width + 2 for p in parts.values()); Ht = max(p.height for p in parts.values()); at = Image.new("RGBA", (Wt, Ht)); x = 0
for nm, p in parts.items(): at.paste(p, (x, 0)); meta[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/giant.png"); meta["core"] = [round(core[0]), round(core[1])]
print("const GIANT = " + json.dumps(meta, separators=(",", ":")) + ";")
