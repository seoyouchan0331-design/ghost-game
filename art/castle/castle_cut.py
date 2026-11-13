# 성채 로비 그림(Higgsfield) → 게임용 그림. assets/castle_*.png 저장, 좌표 JSON 출력. ch1_cut.py와 같은 방식
import json, numpy as np
from PIL import Image
from scipy import ndimage
def rgba(a, alpha): return Image.fromarray(np.dstack([a.astype(np.uint8), alpha.astype(np.uint8)]), "RGBA")
def hard(p):
    px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px, "RGBA")
meta = {}
im = Image.open("bg_source.png").convert("RGB"); sky = [int(v) for v in np.asarray(im)[:8].reshape(-1, 3).mean(0)]
im = im.resize((round(im.width * 340 / im.height), 340), Image.BOX); im.save("../../assets/castle_bg.png"); meta["bg"] = list(im.size); meta["sky"] = "#%02x%02x%02x" % tuple(sky)
a = np.asarray(Image.open("front_source.png").convert("L")); m = a < 110          # 앞 실루엣 → 짙은 남보라
fr = Image.fromarray(np.dstack([np.full(a.shape, 12, np.uint8), np.full(a.shape, 9, np.uint8), np.full(a.shape, 24, np.uint8), (m * 255).astype(np.uint8)]), "RGBA")
fr = hard(fr.resize((480, 270), Image.BOX)); fr.save("../../assets/castle_front.png"); meta["front"] = list(fr.size)
# 지형 6조각 (맨 위의 흐릿한 잔해 띠 두 개는 버린다)
a = np.asarray(Image.open("terrain_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 22
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4)); boxes = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 20000 and s[0].start > 300]
asp = lambda s: (s[1].stop - s[1].start) / (s[0].stop - s[0].start)
sq = sorted([s for s in boxes if 0.6 < asp(s) < 1.6], key=lambda s: s[1].start); hz = sorted([s for s in boxes if asp(s) >= 2.2], key=lambda s: s[0].start); vt = [s for s in boxes if asp(s) <= 0.45]
print("pieces", len(sq), len(hz), len(vt))
cut = lambda s: rgba(a[s], m[s] * 255)
def full(s):
    h, w = s[0].stop - s[0].start, s[1].stop - s[1].start; s = (slice(s[0].start + h * 6 // 100, s[0].stop - h * 6 // 100), slice(s[1].start + w * 6 // 100, s[1].stop - w * 6 // 100))
    return rgba(a[s], np.full((s[0].stop - s[0].start, s[1].stop - s[1].start), 255))
out = {"fill": (full(sq[0]), (64, 64)), "back": (full(sq[1]), (64, 64))}
for name, s, h in (("top", hz[0], 22), ("under", hz[1], 18), ("plank", hz[2], 12)):
    p = cut(s); p = p.crop(p.getbbox()); out[name] = (p, (round(p.width * h / p.height), h))
p = cut(vt[0]); p = p.crop(p.getbbox()); out["side"] = (p, (12, round(p.height * 12 / p.width)))
W = sum(sz[0] + 2 for _, sz in out.values()); H = max(sz[1] for _, sz in out.values()); at = Image.new("RGBA", (W, H)); x = 0; tm = {}
for k, (p, sz) in out.items():
    q = p.resize(sz, Image.BOX); q = hard(q) if k not in ("fill", "back") else q.convert("RGB").convert("RGBA"); at.paste(q, (x, 0)); tm[k] = [x, 0, sz[0], sz[1]]; x += sz[0] + 2
at.save("../../assets/castle_terrain.png"); meta["terrain"] = tm
# 시설·소품 12개: 4x3 격자, 칸 테두리(짙은 선)는 안쪽 6%를 잘라서 뺀다
a = np.asarray(Image.open("props_source.png").convert("RGB")).astype(int)
px = a.reshape(-1, 3); lum = px.mean(1); GREY = np.median(px[(lum > 150) & (px.max(1) - px.min(1) < 12)], axis=0)   # 칸 바탕 회색
NAMES = ["gate", "altar", "helmrack", "dummy", "armor", "helmpile", "candles", "statue", "banner", "chandelier", "bench", "pedestal"]
HGT = [60, 18, 26, 36, 36, 16, 20, 30, 48, 36, 12, 16]
CH, CW = a.shape[0] // 3, a.shape[1] // 4; ps = []; pm = {}
for i, nm in enumerate(NAMES):
    r, c = divmod(i, 4); y0, x0 = r * CH + CH * 6 // 100, c * CW + CW * 6 // 100; s = (slice(y0, (r + 1) * CH - CH * 6 // 100), slice(x0, (c + 1) * CW - CW * 6 // 100))
    cell = a[s]; mm = np.abs(cell - GREY).max(axis=2) > 26
    lb, nn = ndimage.label(mm); edge = set(np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]]))) - {0}   # 칸 테두리에 닿는 조각(틀)은 버린다
    for e in edge: mm[lb == e] = False
    p = rgba(cell, mm * 255); p = p.crop(p.getbbox()); ps.append(hard(p.resize((max(1, round(p.width * HGT[i] / p.height)), HGT[i]), Image.BOX)))
x = 0; at = Image.new("RGBA", (sum(p.width + 2 for p in ps), max(HGT)))
for nm, p in zip(NAMES, ps): at.paste(p, (x, 0)); pm[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/castle_props.png"); meta["props"] = pm
print("const CASTLE = " + json.dumps(meta, separators=(",", ":")) + ";")
