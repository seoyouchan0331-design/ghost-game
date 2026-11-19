# (지금은 안 씀: 버튼은 코드로 그린 반투명 원 + 선 아이콘) 모바일 버튼 [ui_buttons]: 4x4 격자 → 칸마다 바탕(밝은 회색)과 다른 가장 큰 덩어리(둥근 버튼) → 96px로 줄여 assets/ui/btn_<이름>.png
import numpy as np
from PIL import Image
from scipy import ndimage
NAMES = ["attack", "jump", "dash", "skill1", "skill2", "swap", "soul", "menu", "ok", "back", "sound", "gear", "joy", "knob", "ring", "blank"]
a = np.asarray(Image.open("art/ui4/ui_buttons_source.png").convert("RGB")).astype(int); H, W, _ = a.shape
bg = np.median(np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3)]), axis=0)
for i, nm in enumerate(NAMES):
    r, c = divmod(i, 4); y0, y1, x0, x1 = r * H // 4, (r + 1) * H // 4, c * W // 4, (c + 1) * W // 4
    cell = a[y0:y1, x0:x1]; m = np.abs(cell - bg).max(2) > 28
    lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); m = ndimage.binary_fill_holes(lab == (int(np.argmax(sz)) + 1))
    ys, xs = np.nonzero(m); cy0, cy1, cx0, cx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([cell, m * 255]).astype(np.uint8)[cy0:cy1, cx0:cx1]
    im = Image.fromarray(rgba, "RGBA"); S = 96 if nm != "knob" else 72
    sm = np.asarray(im.resize((S, S), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
    Image.fromarray(sm, "RGBA").save(f"assets/ui/btn_{nm}.png", optimize=True)
print("ok")
