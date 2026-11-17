# 영상 공격 프레임에서 이펙트를 지우고 몸동작만 남긴다 (이펙트는 pixelfx로 따로 그린다).
# 같은 단계 대기 프레임들의 모양(발 기준으로 겹친 것)을 조금 넓힌 자리 밖은 지우고(고리·빔·화살·잎),
# 그 안에서도 대기 때 없던 아주 밝은 색(빛 덩어리)은 지운다. 마지막으로 몸에서 떨어진 조각을 지운다.
# 실행: python3 art/heroframes/fx_strip.py <계보>   (index.html의 HERO.<계보>와 assets/hero_<계보>.png를 고친다)
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
LINE = sys.argv[1]; MOVES = sys.argv[2].split(",") if len(sys.argv) > 2 else ["attack"]
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, end = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy()
q = lambda px: (px[..., 0] >> 4).astype(int) * 256 + (px[..., 1] >> 4).astype(int) * 16 + (px[..., 2] >> 4).astype(int)
done = set()
for st, S in enumerate(H["stages"]):
    if "idle" not in S: continue
    pal = set(); R = 220; U = np.zeros((2 * R, 2 * R), bool)          # 발 기준 좌표 (R, R)
    for ci, ox, oy in S["idle"]["f"]:
        x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]; pal |= set(np.unique(q(c)[c[..., 3] > 0]).tolist()); U[R + oy:R + oy + h, R + ox:R + ox + w] |= c[..., 3] > 0
    U = ndimage.binary_dilation(U, iterations=2)
    for mv in MOVES:
        for ci, ox, oy in S.get(mv, {"f": []})["f"]:
            if ci in done: continue
            done.add(ci); x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]
            a = (c[..., 3] > 0) & U[R + oy:R + oy + h, R + ox:R + ox + w]    # 대기 모양을 넓힌 자리 안만
            lum = c[..., :3].mean(axis=2); a &= ~(~np.isin(q(c), list(pal)) & (lum > 120))   # 대기 때 없던 아주 밝은 색 = 빛
            lab, n = ndimage.label(ndimage.binary_dilation(a, iterations=1))  # 몸(가장 큰 덩어리)과 떨어진 조각은 지운다
            if n > 1:
                sz = ndimage.sum(a, lab, range(1, n + 1)); a &= lab == (int(np.argmax(sz)) + 1)
            c[..., 3] = np.where(a, 255, 0)
Image.fromarray(sheet).save(f"assets/hero_{LINE}.png", optimize=True); print("stripped", len(done))
