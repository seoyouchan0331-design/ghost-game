# 방 소품 (이벤트 4종·상자 3종·투구 무덤) 4x2 격자 → assets/room_objects.png + 좌표 JSON
# 실행: cd art/room && python3 room_cut.py
import json, numpy as np
from PIL import Image
a = np.asarray(Image.open("room_objects_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 22
NAMES = ["altar", "gamble", "spring", "armor", "chest", "chest_open", "chest_red", "grave"]
HGT = [30, 40, 30, 22, 18, 22, 18, 28]
CH, CW = a.shape[0] // 2, a.shape[1] // 4; ps = []; meta = {}
for i, nm in enumerate(NAMES):
    r, c = divmod(i, 4); s = (slice(r * CH, (r + 1) * CH), slice(c * CW, (c + 1) * CW))
    p = Image.fromarray(np.dstack([a[s].astype(np.uint8), (m[s] * 255).astype(np.uint8)]), "RGBA"); p = p.crop(p.getbbox())
    p = p.resize((max(1, round(p.width * HGT[i] / p.height)), HGT[i]), Image.BOX); px = np.asarray(p).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); ps.append(Image.fromarray(px))
x = 0; at = Image.new("RGBA", (sum(p.width + 2 for p in ps), max(HGT)))
for nm, p in zip(NAMES, ps): at.paste(p, (x, 0)); meta[nm] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/room_objects.png"); print("const ROOMOBJ = " + json.dumps(meta, separators=(",", ":")) + ";")
