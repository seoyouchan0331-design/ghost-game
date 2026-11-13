# 1챕터 적 4종 시트(가로 한 줄 4자세: 대기·걷기·준비·공격)를 잘라 assets/enemies.png 로 묶는다. 좌표 JSON 출력
# 자세마다 발(아래 20% 줄)의 가운데를 기준점으로 맞춘다. 크기는 대기 자세 키로 맞춤
import json, numpy as np
from PIL import Image
from scipy import ndimage
SHEETS = {"militia": 30, "torch": 30, "shield": 30, "hound": 16}   # 대기 자세 게임 속 키(px)
cells, meta = {}, {}
for name, H in SHEETS.items():
    a = np.asarray(Image.open(f"{name}_source.png").convert("RGB")).astype(int); bg = np.median(a[:20, :20].reshape(-1, 3), axis=0)
    m = np.abs(a - bg).max(axis=2) > 30; m = ndimage.binary_opening(m, iterations=1)
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3)); sizes = ndimage.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 300]) & m
    W = a.shape[1]; poses = []
    # 가장 큰 덩어리 4개가 몸통. 나머지 조각(창끝·불꽃·튄 점)은 가장 가까운 몸통에 붙인다
    ids = [i + 1 for i, sz in sorted(enumerate(sizes), key=lambda t: -t[1]) if sz > 300]; objs = ndimage.find_objects(lab)
    bodies = sorted(ids[:4], key=lambda i: objs[i - 1][1].start); cxs = [(objs[i - 1][1].start + objs[i - 1][1].stop) / 2 for i in bodies]
    owner = {b: k for k, b in enumerate(bodies)}
    for i in ids[4:]: c = (objs[i - 1][1].start + objs[i - 1][1].stop) / 2; owner[i] = int(np.argmin([abs(c - x) for x in cxs]))
    for k in range(4):
        sub = np.isin(lab, [i for i, o in owner.items() if o == k]) & m; ys, xs = np.where(sub); y0, y1 = ys.min(), ys.max()
        foot = sub[y1 - (y1 - y0) // 5:y1 + 1]; fx = np.where(foot.any(0))[0]; cx = (fx.min() + fx.max()) / 2
        poses.append((0, sub, y0, y1, xs.min(), xs.max(), cx))
    k = H / (poses[0][3] - poses[0][2]); frames = []
    for (ox, sub, y0, y1, x0, x1, cx) in poses:
        crop = a[y0:y1 + 1, ox + x0:ox + x1 + 1]; al = sub[y0:y1 + 1, x0:x1 + 1]
        im = Image.fromarray(np.dstack([crop.astype(np.uint8), (al * 255).astype(np.uint8)]), "RGBA")
        w2, h2 = max(1, round(im.width * k)), max(1, round(im.height * k)); im = im.resize((w2, h2), Image.BOX)
        px = np.asarray(im).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0); frames.append((Image.fromarray(px), round((cx - x0) * k), h2))
    L = max(f[1] for f in frames) + 2; R = max(f[0].width - f[1] for f in frames) + 2; T = max(f[2] for f in frames) + 2
    cells[name] = (frames, L, R, T); meta[name] = {"w": L + R, "h": T, "ax": L, "ay": T}
W = max(v["w"] for v in meta.values()) * 4; Hh = sum(v["h"] for v in meta.values()); at = Image.new("RGBA", (W, Hh)); y = 0
for name, (frames, L, R, T) in cells.items():
    for i, (im, fx, h2) in enumerate(frames): at.paste(im, (i * meta[name]["w"] + L - fx, y + T - h2))
    meta[name]["y"] = y; y += T
at.save("../../assets/enemies.png"); print("const ENSPR = " + json.dumps(meta, separators=(",", ":")) + ";")
