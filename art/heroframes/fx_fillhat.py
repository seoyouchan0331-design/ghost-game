# 검은 모자 속처럼 바탕색과 비슷해 키잉에서 뚫린 자리를 메운다 (괴도 3단계 실크햇). hero_cut.py로 다시 자르면 이것도 다시 돌린다
# 프레임 위쪽 절반에서 알파를 닫고(closing) 구멍을 채운 뒤, 불꽃 곁이 아닌 자리만 모자색으로 칠한다 (불꽃 사이 틈은 그대로)
# 실행: python3 art/heroframes/fx_fillhat.py thief 2
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
LINE, ST = sys.argv[1], int(sys.argv[2]); IT = int(sys.argv[3]) if len(sys.argv) > 3 else 2
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, _ = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy(); done = set(); n = 0
HAT = np.array([28, 24, 40])
for mv, M in H["stages"][ST].items():
    if not isinstance(M, dict) or "f" not in M: continue
    for ci, ox, oy in M["f"]:
        if ci in done: continue
        done.add(ci); x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]; m = c[..., 3] > 0
        P = 3; mp = np.pad(m, P); cl = ndimage.binary_fill_holes(ndimage.binary_closing(mp, iterations=IT))[P:-P, P:-P]
        add = cl & ~m; add[h // 2:] = False
        r_, g_, b_ = [c[..., i].astype(int) for i in range(3)]; teal = m & (g_ > r_ + 25) & (b_ > r_ + 15)
        tl = ndimage.uniform_filter(teal.astype(float), 5, mode="constant"); opq = ndimage.uniform_filter(m.astype(float), 5, mode="constant")
        add &= (tl / np.maximum(opq, 1e-3)) < 0.3                       # 불꽃(청록) 사이 틈은 메우지 않는다
        c[add, :3] = HAT; c[add, 3] = 255; n += int(add.sum())
Image.fromarray(sheet).save(f"assets/hero_{LINE}.png", optimize=True); print("filled px", n)
