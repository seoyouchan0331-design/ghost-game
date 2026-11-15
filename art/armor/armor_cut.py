# 갑옷 빙의 조각: 시트마다 줄·칸으로 조각을 찾아 게임 크기로 줄이고 assets/armor.png 한 장 + 좌표 JSON
#  void_parts_source.png   : 1줄 몸통 6자세, 2줄 앞장갑(편)·뒷장갑(편)·주먹·앞장화·뒷장화·망토
#  soldier_body_source.png : 3줄(단계) x 몸통 6자세
#  soldier_gear_source.png : 3줄(단계) x 앞장갑·뒷장갑·앞장화·뒷장화·창·방패
# 몸통마다 "목"(불꽃이 끝나고 갑옷이 시작하는 곳) 위치를 같이 적는다: 투구를 얹는 기준
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
TORSO_H = 30                                                     # 게임 속 몸통(불꽃 포함) 높이 px
POSES = ["idle", "run", "jump", "windup", "attack", "hurt"]
def items(path, rows):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int); m = key(a, thr=20, hole=10 ** 9)
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3)); objs = ndimage.find_objects(lab)
    comps = []
    for i, sl in enumerate(objs):
        mm = (lab[sl] == i + 1) & m[sl]; sz = int(mm.sum())
        if sz < 60: continue
        comps.append({"i": i + 1, "sl": sl, "sz": sz, "cy": (sl[0].start + sl[0].stop) / 2, "cx": (sl[1].start + sl[1].stop) / 2})
    big = sorted(comps, key=lambda c: -c["sz"])[: sum(rows)]
    ys = sorted(c["cy"] for c in big); out = []
    # 줄 나누기: 큰 조각들의 세로 중심을 줄 수만큼 묶는다
    order = sorted(big, key=lambda c: c["cy"]); k = 0
    for cnt in rows:
        row = sorted(order[k:k + cnt], key=lambda c: c["cx"]); k += cnt; out.append(row)
    for c in comps:                                            # 작은 조각(불꽃 부스러기)은 가장 가까운 큰 조각에 붙인다
        if c in big: continue
        best = min(big, key=lambda b: (b["cx"] - c["cx"]) ** 2 + (b["cy"] - c["cy"]) ** 2); best.setdefault("extra", []).append(c["i"])
    def crop(c):
        mm = np.isin(lab, [c["i"]] + c.get("extra", [])) & m; ys_, xs_ = np.nonzero(mm)
        y0, y1, x0, x1 = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
        rgba = np.dstack([a, mm * 255]).astype(np.uint8)[y0:y1, x0:x1]; return Image.fromarray(rgba, "RGBA")
    return [[crop(c) for c in row] for row in out]
def neck(im):                                                   # 위에서부터 청록 불꽃이 아닌 갑옷 픽셀이 처음 많이 나오는 줄
    a = np.asarray(im).astype(int); al = a[..., 3] > 0; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    teal = (g > r + 30) & (b > r + 20); arm = al & ~teal
    for y in range(a.shape[0]):
        if arm[y].sum() >= max(3, a.shape[1] * 0.15): return y
    return 0
cells, meta = [], {}
SIZE = {"glove": ("h", 10), "fist": ("h", 9), "boot": ("h", 12), "cape": ("h", 14), "weapon": ("w", 38), "shield": ("h", 18)}   # 조각 종류마다 게임 속 크기 (시트마다 그려진 크기가 제각각이라)
def fit(im, kind): ax, v = SIZE[kind]; return v / (im.height if ax == "h" else im.width)
def add(im, s):
    w, h = max(1, round(im.width * s)), max(1, round(im.height * s))
    sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0); cells.append(Image.fromarray(sm, "RGBA")); return len(cells) - 1
def torso_set(row, s):
    out = {}
    for nm, im in zip(POSES, row): idx = add(im, s); out[nm] = [idx, round(neck(im) * s)]
    return out
V = items("art/armor/void_parts_source.png", [6, 6]); sV = TORSO_H / V[0][0].height
P = V[1]; meta["void"] = {"torso": torso_set(V[0], sV), "glove_f": add(P[0], fit(P[0], "glove")), "glove_b": add(P[1], fit(P[1], "glove")), "fist": add(P[2], fit(P[2], "fist")), "boot_f": add(P[3], fit(P[3], "boot")), "boot_b": add(P[4], fit(P[4], "boot")), "cape": add(P[5], fit(P[5], "cape"))}
B = items("art/armor/soldier_body_source.png", [6, 6, 6]); sB = TORSO_H / B[0][0].height
G = items("art/armor/soldier_gear_source.png", [6, 6, 6])
# 장비는 1단계 크기에 맞춘 배율을 2·3단계에도 그대로 써서, 진화할수록 커진 만큼 커 보이게
k1 = {n: fit(G[0][i], kd) for i, (n, kd) in enumerate([("glove_f", "glove"), ("glove_b", "glove"), ("boot_f", "boot"), ("boot_b", "boot"), ("weapon", "weapon"), ("shield", "shield")])}
meta["soldier"] = [{"torso": torso_set(B[st], sB), **{n: add(G[st][i], k1[n]) for i, n in enumerate(["glove_f", "glove_b", "boot_f", "boot_b", "weapon", "shield"])}} for st in range(3)]
W = sum(c.width + 1 for c in cells); Hm = max(c.height for c in cells)
sheet = Image.new("RGBA", (W, Hm)); boxes = []; x = 0
for c in cells: sheet.paste(c, (x, 0)); boxes.append([x, 0, c.width, c.height]); x += c.width + 1
sheet.save("assets/armor.png")
print(json.dumps({"sets": meta, "boxes": boxes}))
