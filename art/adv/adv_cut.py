# 모험가 6명 (Higgsfield, 한 장에 대기 자세 하나) → assets/adv.png + 좌표 JSON.
# 바탕(검정 또는 흰색)은 가장자리와 이어진 부분만 지운다 (안쪽의 어두운 테두리는 남긴다).
import json, numpy as np
from PIL import Image
from scipy import ndimage
LIST = [("adv_sword", 38, -1), ("adv_archer", 36, -1), ("adv_cleric", 38, 1), ("adv_mage", 38, 1), ("adv_thief", 34, -1), ("adv_warrior", 42, -1)]   # 이름, 게임 속 키, 그림이 보는 방향
parts = []; meta = {}
for name, h, face in LIST:
    a = np.asarray(Image.open(f"{name[4:]}_source.png").convert("RGB")).astype(int)
    bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)]), axis=0)
    near = np.abs(a - bg).max(axis=2) < 24; lab, n = ndimage.label(near)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(near, lab, range(1, n + 1)); edge |= {i + 1 for i, v in enumerate(sizes) if v > 2500}   # 활 안쪽처럼 갇힌 큰 바탕도 지운다
    fg = ~np.isin(lab, list(edge))
    fg = ndimage.binary_opening(fg, iterations=2)
    ys, xs = np.nonzero(fg); s = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    p = Image.fromarray(np.dstack([a[s].astype(np.uint8), (fg[s] * 255).astype(np.uint8)]), "RGBA")
    p = p.resize((round(p.width * h / p.height), h), Image.BOX); px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0)
    parts.append((name, Image.fromarray(px, "RGBA"), face))
W = sum(p.width + 2 for _, p, _ in parts); H = max(p.height for _, p, _ in parts); at = Image.new("RGBA", (W, H)); x = 0
for name, p, face in parts: at.paste(p, (x, 0)); meta[name] = {"r": [x, 0, p.width, p.height], "face": face}; x += p.width + 2
at.save("../../assets/adv.png"); print("const ADV_SPR = " + json.dumps(meta, separators=(",", ":")) + ";")
