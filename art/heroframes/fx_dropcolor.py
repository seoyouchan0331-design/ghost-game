# 영상 공격 프레임에서 몸 밖의 특정 색 덩어리를 지운다 (예: 괴도 영상 속 날아가는 금화 — 금화는 게임이 따로 그린다)
# 실행: python3 art/heroframes/fx_dropcolor.py thief coin
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
LINE, KIND = sys.argv[1], sys.argv[2]
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, _ = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy(); done = set(); n = 0
for S in H["stages"]:
    if "attack" not in S: continue
    R = 260; U = np.zeros((2 * R, 2 * R), bool)
    for ci, ox, oy in S["idle"]["f"]:
        x, y, w, h = B[ci]; U[R + oy:R + oy + h, R + ox:R + ox + w] |= sheet[y:y + h, x:x + w, 3] > 0
    U = ndimage.binary_dilation(U, iterations=6)
    for ci, ox, oy in S["attack"]["f"]:
        if ci in done: continue
        done.add(ci); x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w].astype(int)
        r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
        m = (a > 0) & (r > 170) & (g > 100) & (b < 110) & (r > b + 80)   # 금화: 주황·노랑
        m = ndimage.binary_dilation(m, iterations=1) & (a > 0) & ~U[R + oy:R + oy + h, R + ox:R + ox + w]
        sheet[y:y + h, x:x + w, 3][m] = 0; n += int(m.sum())
Image.fromarray(sheet, "RGBA").save(f"assets/hero_{LINE}.png", optimize=True); print("removed px", n)
