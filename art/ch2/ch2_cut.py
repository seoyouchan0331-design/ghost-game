# 챕터 2 기사단 요새 그림 → 게임용 그림. assets/ch2_*.png 저장, 좌표 JSON 출력 (art/ch1/ch1_cut.py와 같은 방식)
# 실행: cd art/ch2 && python3 ch2_cut.py
import json, numpy as np
from PIL import Image
from scipy import ndimage
def rgba(a, alpha): return Image.fromarray(np.dstack([a.astype(np.uint8), alpha.astype(np.uint8)]), "RGBA")
def hard(p):
    px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px, "RGBA")
meta = {}
for k in ("bg_a", "bg_b"):                    # 배경: 자르지 않고 통째로, 높이 340
    im = Image.open(f"{k}_source.png").convert("RGB"); im = im.resize((round(im.width * 340 / im.height), 340), Image.BOX); im.save(f"../../assets/ch2_{k}.png"); meta[k] = im.size
a = np.asarray(Image.open("front_source.png").convert("L")); m = a < 110   # 앞 실루엣 → 짙은 남색
fr = Image.fromarray(np.dstack([np.full(a.shape, 8, np.uint8), np.full(a.shape, 14, np.uint8), np.full(a.shape, 30, np.uint8), (m * 255).astype(np.uint8)]), "RGBA")
fr = hard(fr.resize((480, 270), Image.BOX)); fr.save("../../assets/ch2_front.png"); meta["front"] = fr.size
# 지형 6조각: 왼쪽 정사각형 2개(위 = 땅 속, 아래 = 뒷벽), 가로 띠 3개(위부터 윗면·아랫면·발판), 세로 띠 1개(옆면)
a = np.asarray(Image.open("terrain_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 22
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4)); boxes = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 20000]
asp = lambda s: (s[1].stop - s[1].start) / (s[0].stop - s[0].start)
sq = sorted([s for s in boxes if 0.6 < asp(s) < 1.6], key=lambda s: s[0].start)
hz = sorted([s for s in boxes if asp(s) >= 2.2], key=lambda s: s[0].start)
vt = [s for s in boxes if asp(s) <= 0.45]
print("pieces", len(sq), len(hz), len(vt))
cut = lambda s: rgba(a[s], m[s] * 255)
def full(s):
    h, w = s[0].stop - s[0].start, s[1].stop - s[1].start; s = (slice(s[0].start + h * 6 // 100, s[0].stop - h * 6 // 100), slice(s[1].start + w * 6 // 100, s[1].stop - w * 6 // 100))
    return rgba(a[s], np.full((s[0].stop - s[0].start, s[1].stop - s[1].start), 255))
out = {"fill": (full(sq[0]), (64, 64)), "back": (full(sq[1]), (64, 64))}
for name, s, h in (("top", hz[0], 18), ("under", hz[1], 18), ("plank", hz[2], 12)):
    p = cut(s); p = p.crop(p.getbbox()); out[name] = (p, (round(p.width * h / p.height), h))
p = cut(vt[0]); p = p.crop(p.getbbox()); out["side"] = (p, (10, round(p.height * 10 / p.width)))
W = sum(sz[0] + 2 for _, sz in out.values()); H = max(sz[1] for _, sz in out.values()); at = Image.new("RGBA", (W, H)); x = 0; tm = {}
for k, (p, sz) in out.items():
    q = p.resize(sz, Image.BOX); q = hard(q) if k not in ("fill", "back") else q.convert("RGB").convert("RGBA"); at.paste(q, (x, 0)); tm[k] = [x, 0, sz[0], sz[1]]; x += sz[0] + 2
at.save("../../assets/ch2_terrain.png"); meta["terrain"] = tm
# 소품 12개: 4x3 격자
a = np.asarray(Image.open("props_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 22
NAMES = ["rack", "armor", "torch", "balls", "banner", "dummy", "cage", "brazier", "spikes", "crates", "pillar", "chain"]
HGT = [30, 34, 18, 14, 40, 28, 30, 22, 12, 22, 34, 30]
CH, CW = a.shape[0] // 3, a.shape[1] // 4; ps = []; pm = {}
for i, nm in enumerate(NAMES):
    r, c = divmod(i, 4); s = (slice(r * CH, (r + 1) * CH), slice(c * CW, (c + 1) * CW)); p = rgba(a[s], m[s] * 255); p = p.crop(p.getbbox())
    ps.append(hard(p.resize((max(1, round(p.width * HGT[i] / p.height)), HGT[i]), Image.BOX)))
x = 0; at = Image.new("RGBA", (sum(p.width + 2 for p in ps), max(HGT)))
for nm, p in zip(NAMES, ps): at.paste(p, (x, 0)); pm[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/ch2_props.png"); meta["props"] = pm
# 쌍둥이 기사단장: 2x2 (위: 투구 쓴 은기사·흑기사, 아래: 분노). 몸 키 56
import sys, os; sys.path.insert(0, "../adv"); from keying import key
a = np.asarray(Image.open("boss2_source.png").convert("RGB")).astype(int); m = key(a, 22)
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=6)); objs = ndimage.find_objects(lab); sizes = ndimage.sum(m, lab, range(1, n + 1))
big = sorted([i for i in range(n) if sizes[i] > 5000], key=lambda i: -sizes[i])[:4]
big = sorted(big, key=lambda i: ((objs[i][0].start + objs[i][0].stop) / 2 > a.shape[0] // 2, objs[i][1].start))   # 위 줄 왼→오, 아래 줄 왼→오
tw = {}; ims = []
for nm, i in zip(["s", "b", "s_rage", "b_rage"], big):
    s = objs[i]; sub = (lab[s] == i + 1) & m[s]; im = rgba(a[s], sub * 255); im = im.crop(im.getbbox())
    k = 60 / im.height; im = hard(im.resize((round(im.width * k), 60), Image.BOX)); ims.append((nm, im))
x = 0; at = Image.new("RGBA", (sum(im.width + 2 for _, im in ims), 60))
for nm, im in ims: at.paste(im, (x, 0)); tw[nm] = [x, 0, im.width, im.height]; x += im.width + 2
at.save("../../assets/ch2_twins.png"); meta["twins"] = tw
print("const CH2 = " + json.dumps(meta, separators=(",", ":")) + ";")
