# 영상 공격 프레임에서 몸 밖 이펙트 덩어리를 지운다: 회색 연기, 흰·청록 궤적과 섬광 (몸·단검은 남긴다)
# 연기 = 채도 낮은 중간 밝기 덩어리(크기 MIN 이상), 궤적·섬광 = 밝은 흰/청록 덩어리 중 크고 몸에 거의 안 붙은 것 또는 떨어진 것
# 실행: python3 art/heroframes/fx_clean.py <계보> <단계> <동작> <프레임범위,...> [all|bright|teal]  예: fx_clean.py thief 2 attack 0-40,63-101
import sys, json, colorsys, numpy as np
from PIL import Image
from scipy import ndimage
LINE, ST, MV = sys.argv[1], int(sys.argv[2]), sys.argv[3]
RG = [tuple(map(int, r.split("-"))) for r in sys.argv[4].split(",")]
MODE = sys.argv[5] if len(sys.argv) > 5 else "all"   # all | bright (연기는 두고 밝은 것만) | teal (청록은 크기 상관없이 다 지움: 칼에 붙은 청록 궤적)
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, _ = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy(); n = 0
for fi, (ci, ox, oy) in enumerate(H["stages"][ST][MV]["f"]):
    if not any(a <= fi <= b for a, b in RG): continue
    x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]; op = c[..., 3] > 0
    rgb = c[..., :3].astype(float); mx = rgb.max(2); mn = rgb.min(2); lum = rgb.mean(2); sat = (mx - mn) / np.maximum(mx, 1)
    teal = (rgb[..., 1] > rgb[..., 0] + 40) & (rgb[..., 2] > rgb[..., 0] + 30)
    smoke = op & (sat < 0.2) & (lum > 55) & (lum < 150) & (MODE == "all")
    bright = op & (((sat < 0.22) & (lum > 175)) | (teal & (lum > 150)))
    kill = (op & teal & (lum > 90)) if MODE == "teal" else np.zeros_like(op)
    lab, m = ndimage.label(smoke)
    for i in range(1, m + 1):
        r = lab == i
        if r.sum() >= 12: kill |= r
    lab, m = ndimage.label(bright); other = op & ~bright & ~smoke
    for i in range(1, m + 1):
        r = lab == i; edge = ndimage.binary_dilation(r) & ~r; touch = (edge & other).sum() / max(1, edge.sum())
        if touch == 0 or (r.sum() > 22 and touch < 0.3): kill |= r
    keep = op & ~kill
    lab, m = ndimage.label(ndimage.binary_dilation(keep))   # 떨어진 부스러기 지우기
    if m > 1:
        sz = ndimage.sum(keep, lab, range(1, m + 1)); keep &= lab == (int(np.argmax(sz)) + 1)
    n += int((op & ~keep).sum()); c[..., 3] = np.where(keep, 255, 0)
Image.fromarray(sheet).save(f"assets/hero_{LINE}.png", optimize=True); print("cleaned px", n)
