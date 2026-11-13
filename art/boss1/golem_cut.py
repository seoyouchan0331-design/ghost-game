# 골렘 부위 시트(boss1_parts) → assets/golem.png 조각 묶음 + 좌표 JSON. 조각 번호는 화면 배치를 보고 정한 것
import json, numpy as np
from PIL import Image
from scipy import ndimage
a = np.asarray(Image.open("parts_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0)
m = np.abs(a - bg).max(axis=2) > 30
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=4)); objs = ndimage.find_objects(lab); sz = ndimage.sum(m, lab, range(1, n + 1))
big = [i for i in range(n) if sz[i] >= 2000]
NAMES = ["head", "towerB", "towerF", "torso", "armB", "armF", "foreF", "foreB", "pelvis", "legB", "legF", "core"]
K = 0.135; parts = {}
for name, i in zip(NAMES, big):
    s = objs[i]; sub = (lab[s] == i + 1) & m[s]
    im = Image.fromarray(np.dstack([a[s].astype(np.uint8), (sub * 255).astype(np.uint8)]), "RGBA"); im = im.crop(im.getbbox())
    im = im.resize((max(1, round(im.width * K)), max(1, round(im.height * K))), Image.BOX); px = np.asarray(im).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); parts[name] = Image.fromarray(px)
W = sum(p.width + 2 for p in parts.values()); H = max(p.height for p in parts.values()); at = Image.new("RGBA", (W, H)); x = 0; meta = {}
for k, p in parts.items(): at.paste(p, (x, 0)); meta[k] = [x, 0, p.width, p.height]; x += p.width + 2
at.save("../../assets/golem.png"); print("const GOLEM = " + json.dumps(meta, separators=(",", ":")) + ";")
