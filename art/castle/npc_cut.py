# 늙은 망령(왼쪽 전신, 오른쪽 초상) → assets/elder.png (전신, 키 40) / assets/elder_portrait.png (초상, 높이 72)
import numpy as np
from PIL import Image
from scipy import ndimage
a = np.asarray(Image.open("npc_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0)
m = np.abs(a - bg).max(axis=2) > 28; lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3)); sizes = ndimage.sum(m, lab, range(1, n + 1)); objs = ndimage.find_objects(lab)
W = a.shape[1]
for side, name, h in ((0, "elder", 40), (1, "elder_portrait", 72)):
    ids = [i + 1 for i, sz in enumerate(sizes) if sz > 150 and ((objs[i][1].start + objs[i][1].stop) / 2 > W * 0.52) == bool(side)]
    sub = np.isin(lab, ids) & m; ys, xs = np.where(sub); y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    im = Image.fromarray(np.dstack([a[y0:y1 + 1, x0:x1 + 1].astype(np.uint8), (sub[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8)]), "RGBA")
    im = im.resize((round(im.width * h / im.height), h), Image.BOX); px = np.asarray(im).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0)
    Image.fromarray(px).save(f"../../assets/{name}.png"); print(name, im.size)
