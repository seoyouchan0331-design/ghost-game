# Higgsfield로 뽑은 문 8종 · 각인 6개 · 글씨 판 시트를 잘라 배경을 지운다.
# assets/doors.png (게임 화면용, 문 하나 44x56) / assets/engraves.png (각인, 48px) / assets/panels.png (글씨 판, 화면 해상도) + 좌표 출력
import json, numpy as np
from PIL import Image
from scipy import ndimage
def load(f):
    a = np.asarray(Image.open(f).convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0)
    return a, np.abs(a - bg).max(axis=2) > 16
def piece(a, m, s, size=None, fit=None):
    p = Image.fromarray(np.dstack([a[s].astype(np.uint8), (m[s] * 255).astype(np.uint8)]), "RGBA"); p = p.crop(p.getbbox())
    if fit: k = min(fit[0] / p.width, fit[1] / p.height); size = (max(1, round(p.width * k)), max(1, round(p.height * k)))
    p = p.resize(size, Image.BOX); px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); return Image.fromarray(px, "RGBA")
def grid(f, cols, rows, fit):
    a, m = load(f); H, W = m.shape; out = []
    for r in range(rows):
        for c in range(cols): out.append(piece(a, m, (slice(r * H // rows, (r + 1) * H // rows), slice(c * W // cols, (c + 1) * W // cols)), fit=fit))
    return out
def strip(ps, name, cw, ch):
    im = Image.new("RGBA", (cw * len(ps), ch))
    for i, p in enumerate(ps): im.paste(p, (i * cw + (cw - p.width) // 2, ch - p.height))
    im.save(f"../../assets/{name}.png")
strip(grid("doors_source.png", 4, 2, (44, 56)), "doors", 44, 56)
strip(grid("engraves_source.png", 3, 2, (48, 48)) + grid("engraves2_source.png", 3, 2, (48, 48)), "engraves", 48, 48)   # 각인 12개: 화약·서리·피·유령·질풍·황금 + 독·번개·철벽·사냥·영혼·시계
a, m = load("panels_source.png")
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=6))
boxes = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) * (s[1].stop - s[1].start) > 5000]
boxes.sort(key=lambda s: (0 if s[1].start < 300 else 1, s[0].start // 120, s[1].start))
names = ["window", "header", "nameplate", "banner", "tooltip", "slot", "slotOn", "gradeR", "gradeT", "gradeL"]
assert len(boxes) == len(names), len(boxes)
ps = [piece(a, m, s, fit=((s[1].stop - s[1].start) * 0.3, (s[0].stop - s[0].start) * 0.3)) for s in boxes]
W = sum(p.width + 2 for p in ps); H = max(p.height for p in ps); atlas = Image.new("RGBA", (W, H)); x = 0; out = {}
for nm, p in zip(names, ps): atlas.paste(p, (x, 0)); out[nm] = [x, 0, p.width, p.height]; x += p.width + 2
atlas.save("../../assets/panels.png"); print("const PANELS = " + json.dumps(out, separators=(",", ":")) + ";")
