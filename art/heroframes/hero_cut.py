# 한 영상에 나란히 있는 계보 3단계 → 단계·동작별 프레임 시트 (assets/hero_<계보>.png) + 좌표 JSON
# python3 art/heroframes/hero_cut.py <영상> <계보> <동작:시작초:끝초[:fps]> ...
#   예) art/heroframes/soldier_idle_run_source.mp4 soldier idle:0:4 run:4.6:9.6
# 첫 프레임에서 세 캐릭터 자리(가로 구간)와 바닥선을 잡고, 모든 프레임을 같은 자리·같은 배율로 자른다 (둥실거림이 그대로 남게)
import sys, os, json, glob, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
SRC, LINE, SEGS = sys.argv[1], sys.argv[2], sys.argv[3:]
H1 = 36                                                         # 1단계 키(불꽃 포함) px. 2·3단계는 같은 배율이라 더 크다
TMP = "/tmp/hero_frames"; os.makedirs(TMP, exist_ok=True)
def frames(t0, t1, fps):
    for f in glob.glob(TMP + "/*.png"): os.remove(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1), "-i", SRC, "-vf", f"fps={fps}", TMP + "/f%03d.png"], check=True)
    return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(TMP + "/*.png"))]
first = frames(0, 0.2, 10)[0]; m0 = key(first, thr=13, hole=10 ** 9); cols = m0.any(axis=0)
runs, x = [], 0
while x < len(cols):
    if cols[x]:
        s = x
        while x < len(cols) and cols[x]: x += 1
        if x - s > 15: runs.append([s, x])
    x += 1
merged = []
for r in runs:
    if merged and r[0] - merged[-1][1] < 25: merged[-1][1] = r[1]
    else: merged.append(r)
merged = sorted(merged, key=lambda r: -(r[1] - r[0]))[:3]; merged.sort()
assert len(merged) == 3, merged
chars = []
for x0, x1 in merged:
    ys = np.nonzero(m0[:, x0:x1].any(axis=1))[0]; chars.append({"cx": (x0 + x1) / 2, "gy": ys.max() + 1, "h": ys.max() + 1 - ys.min(), "w": x1 - x0})
s = H1 / chars[0]["h"]
mid = [(merged[i][1] + merged[i + 1][0]) / 2 for i in range(2)]; bounds = [(0, mid[0]), (mid[0], mid[1]), (mid[1], first.shape[1])]
cells, meta = [], {"stages": [{} for _ in range(3)]}
for seg in SEGS:
    nm, t0, t1, *fp = seg.split(":"); fps = int(fp[0]) if fp else 10
    fr = frames(float(t0), float(t1), fps)
    for st, (bx0, bx1) in enumerate(bounds):
        bx0, bx1 = int(bx0), int(bx1); c = chars[st]; top = 0; ids = []
        for a in fr:
            sub = a[:, bx0:bx1]; m = key(sub, thr=13, hole=10 ** 9)
            lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); m = np.isin(lab, [i + 1 for i in range(n) if sz[i] > 30])
            rgba = np.dstack([sub, m * 255]).astype(np.uint8); im = Image.fromarray(rgba, "RGBA")
            w, h = round(im.width * s), round(im.height * s); sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
            im2 = Image.fromarray(sm, "RGBA"); bb = im2.getbbox() or (0, 0, 1, 1)
            ax, gy = round((c["cx"] - bx0) * s), round(c["gy"] * s)        # 기준점: 첫 프레임의 발 가운데
            crop = im2.crop((bb[0], bb[1], bb[2], bb[3])); cells.append(crop); ids.append([len(cells) - 1, bb[0] - ax, bb[1] - gy])
        meta["stages"][st][nm] = {"fps": fps, "f": ids}
W = 2048; x = y = rowh = 0; boxes = []
for c in cells:
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    boxes.append([x, y, c.width, c.height]); x += c.width + 1; rowh = max(rowh, c.height)
sheet = Image.new("RGBA", (W, y + rowh + 1))
for c, b in zip(cells, boxes): sheet.paste(c, (b[0], b[1]))
sheet.save(f"assets/hero_{LINE}.png", optimize=True)
meta["boxes"] = boxes; print(json.dumps(meta))
