# 1챕터 마무리 그림: 강화 아이콘 12 · 영혼 8 · 암시장 상인 4 · 숲 문 10 → assets/ 와 좌표 JSON
import json, sys, os, numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "adv")); from keying import key
def hard(p): px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px)
def cells(f, cols, rows, inset=0.04):
    a = np.asarray(Image.open(f).convert("RGB")).astype(int); H, W = a.shape[:2]; out = []
    for r in range(rows):
        for c in range(cols):
            y0, y1, x0, x1 = r * H // rows, (r + 1) * H // rows, c * W // cols, (c + 1) * W // cols; dy, dx = int((y1 - y0) * inset), int((x1 - x0) * inset)
            cell = a[y0 + dy:y1 - dy, x0 + dx:x1 - dx]; m = key(cell, 26, 10 ** 9)                 # 칸 테두리와 이어진 바탕만 지운다
            lb, n = ndimage.label(m); sz = ndimage.sum(m, lb, range(1, n + 1)); keep = [i + 1 for i, s in enumerate(sz) if s > 80]
            m = np.isin(lb, keep); ys, xs = np.where(m)
            out.append(Image.fromarray(np.dstack([cell.astype(np.uint8), (m * 255).astype(np.uint8)])).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)))
    return out
def fit(p, w, h): k = min(w / p.width, h / p.height); return hard(p.resize((max(1, round(p.width * k)), max(1, round(p.height * k))), Image.BOX))
def strip(ps, name, cw, ch, bottom=True):
    im = Image.new("RGBA", (cw * len(ps), ch))
    for i, p in enumerate(ps): im.paste(p, (i * cw + (cw - p.width) // 2, ch - p.height if bottom else (ch - p.height) // 2))
    im.save(f"../../assets/{name}.png")
strip([fit(p, 32, 32) for p in cells("tree_source.png", 4, 3)], "tree_icons", 32, 32, False)       # 강화 칸 아이콘 32px
strip([fit(p, 24, 28) for p in cells("souls_source.png", 4, 2)], "souls", 24, 28, False)            # 영혼 구슬
strip([fit(p, 46, 58) for p in cells("doors_source.png", 5, 2, 0.06)], "ch1_doors", 46, 58)         # 숲 문 (바닥 맞춤)
# 상인 4명: 한 줄, 칸 테두리 없음 → 덩어리 4개
a = np.asarray(Image.open("npcs_source.png").convert("RGB")).astype(int); m = key(a, 22, 4000)   # 무기걸이 안쪽 같은 갇힌 바탕도 지운다
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=6)); objs = ndimage.find_objects(lab); sz = ndimage.sum(m, lab, range(1, n + 1))
big = sorted(sorted(range(n), key=lambda i: -sz[i])[:4], key=lambda i: objs[i][1].start); meta = {}
ps = []
for i in big:
    s = objs[i]; sub = (lab[s] == i + 1) & m[s]; ps.append(fit(Image.fromarray(np.dstack([a[s].astype(np.uint8), (sub * 255).astype(np.uint8)])), 60, 46))
x = 0; im = Image.new("RGBA", (sum(p.width + 2 for p in ps), 46))
for nm, p in zip(["cook", "merchant", "spirit", "smith"], ps): im.paste(p, (x, 46 - p.height)); meta[nm] = [x, 46 - p.height, p.width, p.height]; x += p.width + 2
im.save("../../assets/shop_npcs.png"); print("const SHOPNPC = " + json.dumps(meta, separators=(",", ":")) + ";")
