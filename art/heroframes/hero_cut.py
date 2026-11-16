# 한 영상에 나란히 있는 계보 3단계 → 단계·동작별 프레임 시트 (assets/hero_<계보>.png) + 좌표 JSON
# python3 art/heroframes/hero_cut.py <계보> src=<영상>[,zone=left] <동작:시작초:끝초[:fps][:pin]> ... (src= 여러 번 가능, 한 시트로 합침)
#   병사: soldier src=art/heroframes/soldier_idle_run_source.mp4 idle:1.1:4:10:pin run:4.6:9.6:10:pin src=art/heroframes/soldier_attack_source.mp4,zone=left attack:0.4:3.6:12 charge:5.4:8.8:12
# 첫 프레임에서 세 캐릭터 자리(가로 구간)와 바닥선을 잡고, 모든 프레임을 같은 자리·같은 배율로 자른다 (둥실거림이 그대로 남게)
import sys, os, json, glob, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
LINE, ARGS = sys.argv[1], sys.argv[2:]
H1 = 36                                                         # 1단계 키(불꽃 포함) px. 2·3단계는 같은 배율이라 더 크다
TMP = "/tmp/hero_frames"; os.makedirs(TMP, exist_ok=True)
def frames(src, t0, t1, fps):
    for f in glob.glob(TMP + "/*.png"): os.remove(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1), "-i", src, "-vf", f"fps={fps}", TMP + "/f%03d.png"], check=True)
    return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(TMP + "/*.png"))]
def setup(src, zone):
    first = frames(src, 0, 0.2, 10)[0]; m0 = key(first, thr=13, hole=10 ** 9); cols = m0.any(axis=0)
    runs, x = [], 0
    while x < len(cols):
        if cols[x]:
            s0 = x
            while x < len(cols) and cols[x]: x += 1
            if x - s0 > 15: runs.append([s0, x])
        x += 1
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < 25: merged[-1][1] = r[1]
        else: merged.append(r)
    merged = sorted(merged, key=lambda r: -(r[1] - r[0]))[:3]; merged.sort(); assert len(merged) == 3, merged
    chars = []
    for x0, x1 in merged:
        ys = np.nonzero(m0[:, x0:x1].any(axis=1))[0]; chars.append({"cx": (x0 + x1) / 2, "gy": ys.max() + 1, "h": ys.max() + 1 - ys.min()})
    Wd = first.shape[1]
    if zone == "left":                                          # 공격 영상: 캐릭터 왼쪽 넉넉히부터 다음 캐릭터 직전까지. 덩어리 주인은 아래에서 가린다
        L = [r[0] for r in merged]; bounds = [(max(0, L[0] - 220), L[1] - 10), (L[1] - 220, L[2] - 10), (L[2] - 220, Wd)]
        for c, l in zip(chars, L): c["left"] = l
    else:
        mid = [(merged[i][1] + merged[i + 1][0]) / 2 for i in range(2)]; bounds = [(0, mid[0]), (mid[0], mid[1]), (mid[1], Wd)]
    return chars, bounds
cells, meta = [], {"stages": [{} for _ in range(3)]}
src = None
for tok in ARGS:
    if tok.startswith("src="):                                  # src=영상[,zone=left]
        parts = tok[4:].split(","); src = parts[0]; zone = parts[1].split("=")[1] if len(parts) > 1 else "mid"
        chars, bounds = setup(src, zone); s = H1 / chars[0]["h"]; continue
    nm, t0, t1, *rest = tok.split(":"); fps = int(rest[0]) if rest else 10; pin = "pin" in rest   # pin: 발을 바닥에 붙인다 (대기·달리기)
    fr = frames(src, float(t0), float(t1), fps)
    for st, (bx0, bx1) in enumerate(bounds):
        bx0, bx1 = int(bx0), int(bx1); c = chars[st]; ids = []
        for a in fr:
            sub = a[:, bx0:bx1]; m = key(sub, thr=13, hole=10 ** 9)
            r_, g_, b_ = sub[..., 0], sub[..., 1], sub[..., 2]; lum = sub.mean(axis=2)
            bgl = np.median(np.concatenate([sub[:4].reshape(-1, 3), sub[-4:].reshape(-1, 3)]), axis=0).mean()
            halo = (b_ > r_ + 8) & (b_ >= g_) & (lum > bgl + 4) & (lum < 75) & ~((g_ > r_ + 30) & (g_ >= b_ - 10))   # 빛이 번져 바탕보다 밝아진 남색 (검은 테두리·청록 불꽃은 아님)
            lb, nb = ndimage.label(halo | ~m); edge = set(np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]]))) - {0}
            m &= ~np.isin(lb, list(edge))
            lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); objs = ndimage.find_objects(lab); keep = []
            for i in range(n):
                if sz[i] <= 30: continue
                x0c, x1c = objs[i][1].start, objs[i][1].stop
                if "left" in c:                                     # 공격 영상: 이 캐릭터 몸 왼쪽 끝보다 오른쪽으로 뻗은 덩어리만, 오른쪽 경계에 닿은 건(옆 캐릭터 것) 버림
                    if bx0 + x1c <= c["left"] + 5: continue
                    if st < 2 and x1c >= sub.shape[1] - 1: continue
                keep.append(i + 1)
            m = np.isin(lab, keep)
            rgba = np.dstack([sub, m * 255]).astype(np.uint8); im = Image.fromarray(rgba, "RGBA")
            w, h = round(im.width * s), round(im.height * s); sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
            im2 = Image.fromarray(sm, "RGBA"); bb = im2.getbbox() or (0, 0, 1, 1)
            ax, gy = round((c["cx"] - bx0) * s), round(c["gy"] * s)        # 기준점: 첫 프레임의 발 가운데
            if pin: gy = bb[3]                                              # 발(맨 아래)을 바닥에 붙여 대기 중에 뜨지 않게
            crop = im2.crop(bb); cells.append(crop); ids.append([len(cells) - 1, bb[0] - ax, bb[1] - gy])
        meta["stages"][st][nm] = {"fps": fps, "f": ids}
W = 2048; x = y = rowh = 0; boxes = []
for c in cells:
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    boxes.append([x, y, c.width, c.height]); x += c.width + 1; rowh = max(rowh, c.height)
sheet = Image.new("RGBA", (W, y + rowh + 1))
for c, b in zip(cells, boxes): sheet.paste(c, (b[0], b[1]))
sheet.save(f"assets/hero_{LINE}.png", optimize=True)
meta["boxes"] = boxes; print(json.dumps(meta))
