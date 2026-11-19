# 금화 둘레에 남은 검은 테두리(영상 바탕이 덜 잘린 것)를 벗긴다: 금화 곁이면서 바깥(투명)에 닿은 어두운 픽셀을 두 겹 지운다
# 실행: python3 art/heroframes/fx_coinhalo.py thief 2 [동작,...]   (hero_cut.py로 다시 자르면 이것도 다시)
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
LINE, ST = sys.argv[1], int(sys.argv[2]); MV = sys.argv[3].split(",") if len(sys.argv) > 3 else None
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, _ = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy(); done = set(); n = 0
for mv, M in H["stages"][ST].items():
    if not isinstance(M, dict) or "f" not in M or (MV and mv not in MV): continue
    for ci, ox, oy in M["f"]:
        if ci in done: continue
        done.add(ci); x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]; rgb = c[..., :3].astype(int)
        for _ in range(3):
            m = c[..., 3] > 0; r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
            gold = m & (r > 140) & (g > 90) & (b < 100) & (r > b + 60)
            dark = m & (rgb.mean(2) < 60) & ~gold
            nearGold = ndimage.binary_dilation(gold, iterations=2); out = ndimage.binary_dilation(~np.pad(m, 1, constant_values=False))[1:-1, 1:-1]
            kill = dark & nearGold & out; n += int(kill.sum()); c[kill, 3] = 0
Image.fromarray(sheet).save(f"assets/hero_{LINE}.png", optimize=True); print("halo px", n)
