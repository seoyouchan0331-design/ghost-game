# 영상 공격 프레임의 이펙트(몸 밖의 청록 궤적)만 다른 색으로 바꾼다. 몸의 유령불(청록)은 그대로.
# 대기·달리기 때 유령불이 있던 자리(조금 넓힘) 밖의 청록 픽셀 = 이펙트로 본다. 셋째 인자 = 넓히는 칸 수 (기본 2)
# 실행: python3 art/heroframes/fx_recolor.py executioner 356   (색상각 356 = 붉은색). hero_cut.py로 다시 자르면 이것도 다시 돌린다
import sys, json, colorsys, numpy as np
from PIL import Image
from scipy import ndimage
LINE, HUE = sys.argv[1], float(sys.argv[2]) / 360
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, _ = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).astype(float); done = set(); n = 0
for S in H["stages"]:
    if "attack" not in S: continue
    R = 260; U = np.zeros((2 * R, 2 * R), bool)          # 대기·달리기 때 유령불(청록)이 있던 자리 = 몸의 불꽃. 거기 밖의 청록은 모두 이펙트
    for ci, ox, oy in S["idle"]["f"] + S["run"]["f"]:
        x, y, w, h = B[ci]; cc = sheet[y:y + h, x:x + w]; U[R + oy:R + oy + h, R + ox:R + ox + w] |= (cc[..., 3] > 0) & (cc[..., 1] > cc[..., 0] + 25) & (cc[..., 2] > cc[..., 0] + 10)
    U = ndimage.binary_dilation(U, iterations=int(sys.argv[3]) if len(sys.argv) > 3 else 2)
    for ci, ox, oy in S["attack"]["f"]:
        if ci in done: continue
        done.add(ci); x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]
        r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
        m = (a > 0) & (g > r + 25) & (b > r + 10) & ~U[R + oy:R + oy + h, R + ox:R + ox + w]
        tl = (a > 0) & (g > r + 25) & (b > r + 10); lab, nl = ndimage.label(tl, np.ones((3, 3)))   # 궤적 덩어리가 대부분 불꽃 자리 밖이면 덩어리째 (몸 위를 지나는 부분까지)
        if nl: tot = ndimage.sum(tl, lab, range(1, nl + 1)); out = ndimage.sum(m, lab, range(1, nl + 1)); m |= np.isin(lab, [i + 1 for i in range(nl) if tot[i] > 30 and out[i] / tot[i] > 0.35])
        ys, xs = np.nonzero(m)
        for yy, xx in zip(ys, xs):
            hh, ss, vv = colorsys.rgb_to_hsv(*(c[yy, xx, :3] / 255)); rr, gg, bb = colorsys.hsv_to_rgb(HUE, min(1, ss * 1.15), vv)
            c[yy, xx, :3] = [rr * 255, gg * 255, bb * 255]
        n += len(ys)
Image.fromarray(sheet.clip(0, 255).astype(np.uint8), "RGBA").save(f"assets/hero_{LINE}.png", optimize=True)
print("recolored px", n)
