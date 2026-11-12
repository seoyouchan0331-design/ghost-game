# 챕터 1 맵 그림(Higgsfield) → 게임용 그림. assets/ch1_*.png 저장, 좌표 JSON 출력.
import json, numpy as np
from PIL import Image
from scipy import ndimage
def rgba(a, alpha): return Image.fromarray(np.dstack([a.astype(np.uint8), alpha.astype(np.uint8)]), "RGBA")
def hard(p):
    px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px, "RGBA")
meta = {}
# 먼 배경: 높이 300으로
far = Image.open("far_source.png").convert("RGB"); far = far.resize((round(far.width * 340 / far.height), 340), Image.BOX); far.save("../../assets/ch1_far.png"); meta["far"] = far.size
# 중간 배경: 검은 바탕을 부드럽게 빼고 너비 960으로
a = np.asarray(Image.open("mid_source.png").convert("RGB")).astype(int); d = a.max(axis=2)
alpha = np.clip((d - 14) * 8, 0, 255); mid = rgba(a, alpha); mid = mid.resize((960, round(mid.height * 960 / mid.width)), Image.BOX)
al = np.asarray(mid)[..., 3]; rows = np.where((al > 128).sum(axis=1) > mid.width * 0.5)[0]; mid = mid.crop((0, 0, 960, int(rows.max()) + 6)); mid.save("../../assets/ch1_mid.png"); meta["mid"] = mid.size
# 앞 전경: 자홍 바탕 빼고 높이 270으로
a = np.asarray(Image.open("front_source.png").convert("RGB")).astype(int); mg = (a[..., 0] > 180) & (a[..., 1] < 90) & (a[..., 2] > 180)
fr = hard(rgba(a, np.where(mg, 0, 255)).resize((round(a.shape[1] * 270 / a.shape[0]), 270), Image.BOX)); fr.save("../../assets/ch1_front.png"); meta["front"] = fr.size
# 지형 질감: 조각 6개를 모양으로 가린다
a = np.asarray(Image.open("terrain_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 18
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4)); boxes = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 20000]
def cut(s): return rgba(a[s], m[s] * 255)
sq = sorted([s for s in boxes if 0.7 < (s[1].stop - s[1].start) / (s[0].stop - s[0].start) < 1.4], key=lambda s: s[0].start)
hz = sorted([s for s in boxes if (s[1].stop - s[1].start) / (s[0].stop - s[0].start) >= 2.5], key=lambda s: s[0].start)
vt = [s for s in boxes if (s[0].stop - s[0].start) / (s[1].stop - s[1].start) >= 2.5]
print("pieces", len(sq), len(hz), len(vt))
full = lambda s: rgba(a[s], np.full(m[s].shape, 255))   # 질감은 구멍 없이 통째로
out = {"fill": (full(sq[0]), (64, 64)), "back": (full(sq[1]), (64, 64))}
for name, s, h in (("top", hz[0], 22), ("under", hz[1], 18), ("plank", hz[2], 9)):
    p = cut(s); out[name] = (p, (round(p.width * h / p.height), h))
p = cut(vt[0]); out["side"] = (p, (10, round(p.height * 10 / p.width)))
W = sum(sz[0] + 2 for _, sz in out.values()); H = max(sz[1] for _, sz in out.values()); at = Image.new("RGBA", (W, H)); x = 0; tm = {}
for k, (p, sz) in out.items():
    q = p.resize(sz, Image.BOX); q = hard(q) if k not in ("fill", "back") else q.convert("RGB").convert("RGBA"); at.paste(q, (x, 0)); tm[k] = [x, 0, sz[0], sz[1]]; x += sz[0] + 2
at.save("../../assets/ch1_terrain.png"); meta["terrain"] = tm
# 소품 12개: 4x3 격자, 소품마다 게임 속 높이로
a = np.asarray(Image.open("props_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 16
NAMES = ["barrel", "crates", "cart", "lamp", "banner", "debris", "fence", "well", "lantern", "rubble", "bush", "sign"]
HGT = [20, 22, 24, 46, 40, 18, 18, 34, 22, 13, 20, 30]
CH, CW = a.shape[0] // 3, a.shape[1] // 4; ps = []; pm = {}
for i, nm in enumerate(NAMES):
    r, c = divmod(i, 4); s = (slice(r * CH, (r + 1) * CH), slice(c * CW, (c + 1) * CW)); p = rgba(a[s], m[s] * 255); p = p.crop(p.getbbox())
    ps.append(hard(p.resize((max(1, round(p.width * HGT[i] / p.height)), HGT[i]), Image.BOX)))
x = 0; at = Image.new("RGBA", (sum(p.width + 2 for p in ps), max(HGT)))
for nm, p in zip(NAMES, ps): at.paste(p, (x, 0)); pm[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/ch1_props.png"); meta["props"] = pm
print("const CH1 = " + json.dumps(meta, separators=(",", ":")) + ";")
