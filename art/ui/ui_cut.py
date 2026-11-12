# Higgsfield로 뽑은 UI 시트(ui_source.png)를 부품별로 잘라 배경을 지우고, 게임용 한 장(assets/ui.png)으로 묶는다.
# 실행: python3 ui_cut.py   → assets/ui.png 저장, 부품 좌표(JSON)를 출력
import json, numpy as np
from PIL import Image
from scipy import ndimage
SCALE = 0.18
im = np.asarray(Image.open("ui_source.png").convert("RGB")).astype(int)
bg = np.median(im[:40, :40].reshape(-1, 3), axis=0)
mask = np.abs(im - bg).max(axis=2) > 13
lab, n = ndimage.label(ndimage.binary_dilation(mask, iterations=7))
boxes = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 6000]
def band(s): cy = (s[0].start + s[0].stop) / 2; return 0 if cy < 400 else 1 if cy < 790 else 2 if cy < 980 else 3
boxes.sort(key=lambda s: (band(s), s[1].start))
names = ["hp", "main", "sub", "skillA", "skillS", "pipOn", "pipOff", "gold", "scrap", "chest", "helm", "rest", "shop"]
assert len(boxes) == len(names), len(boxes)
pieces = {}
for name, s in zip(names, boxes):
    rgb = im[s].astype(np.uint8); a = (mask[s] * 255).astype(np.uint8)
    p = Image.fromarray(np.dstack([rgb, a]), "RGBA")
    p = p.resize((max(1, round(p.width * SCALE)), max(1, round(p.height * SCALE))), Image.NEAREST)
    bb = p.getbbox(); pieces[name] = p.crop(bb)
def window(p):                                   # 틀 안쪽의 빈 창: 가운데에서 네 방향으로 넓혀 찾는다
    a = np.asarray(p)[:, :, 3] > 0; h, w = a.shape; cy, cx = int(h * 0.55), w // 2
    x0 = cx; x1 = cx; y0 = cy; y1 = cy
    while x0 > 0 and not a[cy, x0 - 1]: x0 -= 1
    while x1 < w - 1 and not a[cy, x1 + 1]: x1 += 1
    while y0 > 0 and not a[y0 - 1, cx]: y0 -= 1
    while y1 < h - 1 and not a[y1 + 1, cx]: y1 += 1
    return [x0, y0, x1 - x0 + 1, y1 - y0 + 1]
W = sum(p.width + 2 for p in pieces.values()); H = max(p.height for p in pieces.values())
atlas = Image.new("RGBA", (W, H)); x = 0; out = {}
for name, p in pieces.items():
    atlas.paste(p, (x, 0)); out[name] = [x, 0, p.width, p.height] + (window(p) if name in ("hp", "main", "sub", "skillA", "skillS") else []); x += p.width + 2
atlas.save("../../assets/ui.png")
print(atlas.size); print("const UI = " + json.dumps(out, separators=(",", ":")) + ";")
prev = Image.new("RGBA", (W * 2, H * 2), (60, 50, 80, 255)); prev.alpha_composite(atlas.resize((W * 2, H * 2), Image.NEAREST)); prev.save("/tmp/ui_prev.png")
