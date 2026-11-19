# 한 영상에 나란히 있는 계보 3단계 → 단계·동작별 프레임 시트 (assets/hero_<계보>.png) + 좌표 JSON
# python3 art/heroframes/hero_cut.py <계보> src=<영상>[,zone=left] <동작:시작초:끝초[:fps][:pin]> ... (src= 여러 번 가능, 한 시트로 합침)
#   병사: soldier src=art/heroframes/soldier_idle_run_source.mp4 idle:1.1:4:10:pin run:4.6:9.6:10:pin src=art/heroframes/soldier_attack_source.mp4,zone=left,only=2 attack:0.4:3.6:12 charge:5.4:8.8:12 src=art/heroframes/soldier_s12_attack_source.mp4,zone=half,n=2,st=0,white=0 attack:0.2:4.4:12 charge:4.6:9.4:12
#   괴도: thief src=art/heroframes/thief_idle_run_source.mp4 idle:2.583:3.99:20 run:6.3:10.1:10:pin src=art/heroframes/thief_s12_attack_source.mp4,zone=own,n=2,st=0 attack:0:10.1:12 src=art/heroframes/thief_s3_pickpocket_source.mp4,zone=own,n=1,st=2 pick:0:10.1:12 src=art/heroframes/thief_s3_cuts_source.mp4,zone=own,n=1,st=2 cuts:0.3:4.6:12 src=art/heroframes/thief_s3_attack_source.mp4,zone=own,n=1,st=2 attack:0:10.1:12
#     그다음: 대기 fps 17, seg·pseg 넣고, fx_dropcolor.py thief coin, fx_recolor.py thief drop 2 cuts, fx_recolor.py thief drop 2 pick (원 궤적 지움), fx_recolor.py thief drop 2 attack, fx_clean.py thief 2 attack 0-40,48-85 / 86-101 bright / 30-37 teal (연기·흰 궤적), 3단계 seg 넣기
#   처형인: executioner h1=43 src=art/heroframes/executioner_idle_run_source.mp4 idle:0.2:2.6:10:pin run:2.9:5.15:10:pin src=art/heroframes/executioner_s12_attack_source.mp4,zone=own,n=2,st=0 attack:0:10.1:12 src=art/heroframes/executioner_s3_attack_source.mp4,zone=own,n=1,st=2 attack:0:10.1:12  (그다음 seg 넣고 fx_recolor.py executioner 356 으로 궤적을 붉게)
#   서리 늑대: frostwolf src=art/heroframes/frostwolf_idle_run_source.mp4 idle:1.0:5.3:10:pin run:6.0:8.5:10:pin src=art/heroframes/frostwolf_s12_attack_source.mp4,zone=own,n=2,st=0 attack:0:10:12 src=art/heroframes/frostwolf_s3_attack_source.mp4,zone=own,n=1,st=2 attack:0:10:12
#   지금: 둘째 src = art/heroframes/soldier_s3_attack_source.mp4,zone=half,n=1,st=2 attack:0.2:4.4:12 charge:5.2:9.0:12
# 첫 프레임에서 세 캐릭터 자리(가로 구간)와 바닥선을 잡고, 모든 프레임을 같은 자리·같은 배율로 자른다 (둥실거림이 그대로 남게)
import sys, os, json, glob, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
LINE, ARGS = sys.argv[1], sys.argv[2:]
H1 = next((int(a[3:]) for a in ARGS if a.startswith("h1=")), 36); ARGS = [a for a in ARGS if not a.startswith("h1=")]   # h1=43: 이 계보만 더 크게 (처형인은 불꽃·단두대가 커서 몸이 작아 보였다)                                                         # 1단계 키(불꽃 포함) px. 2·3단계는 같은 배율이라 더 크다
TMP = "/tmp/hero_frames"; os.makedirs(TMP, exist_ok=True)
def frames(src, t0, t1, fps):
    for f in glob.glob(TMP + "/*.png"): os.remove(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1), "-i", src, "-vf", f"fps={fps}", TMP + "/f%03d.png"], check=True)
    return [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(TMP + "/*.png"))]
def setup(src, zone, n=3):
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
    merged = sorted(merged, key=lambda r: -(r[1] - r[0]))[:n]; merged.sort(); assert len(merged) == n, merged
    chars = []
    for x0, x1 in merged:
        ys = np.nonzero(m0[:, x0:x1].any(axis=1))[0]; chars.append({"cx": (x0 + x1) / 2, "gy": ys.max() + 1, "h": ys.max() + 1 - ys.min()})
    Wd = first.shape[1]
    if zone == "own":                                           # 넓게 잘라 두고, 덩어리마다 가장 가까운 캐릭터 것으로 (이펙트가 가운데 선을 넘는 영상)
        bounds = [(0, Wd)] if n == 1 else [(max(0, int(c["cx"] - 360)), min(Wd, int(c["cx"] + 460))) for c in chars]   # 혼자 나오는 영상은 화면 전체 (멀리 뻗는 이펙트가 잘리지 않게)
        for c in chars: c["own"] = [d["cx"] for d in chars]
    elif zone == "half":                                          # 화면을 캐릭터 수만큼 똑같이 나눈 영상
        bounds = [(Wd * i // n, Wd * (i + 1) // n) for i in range(n)]
    elif zone == "left":                                          # 공격 영상: 캐릭터 왼쪽 넉넉히부터 다음 캐릭터 직전까지. 덩어리 주인은 아래에서 가린다
        L = [r[0] for r in merged]; bounds = [(max(0, L[0] - 220), L[1] - 10), (L[1] - 220, L[2] - 10), (L[2] - 220, Wd)]
        for c, l in zip(chars, L): c["left"] = l
    else:
        mid = [(merged[i][1] + merged[i + 1][0]) / 2 for i in range(2)]; bounds = [(0, mid[0]), (mid[0], mid[1]), (mid[1], Wd)]
    return chars, bounds
cells, meta = [], {"stages": [{} for _ in range(3)]}
src = None; idleH = {}
for tok in ARGS:
    if tok.startswith("src="):                                  # src=영상[,zone=left|half][,n=2][,st=0-1][,only=2][,white=0]
        parts = tok[4:].split(","); src = parts[0]; opt = dict(p.split("=") for p in parts[1:])
        zone = opt.get("zone", "mid"); n = int(opt.get("n", 3)); st0 = int(opt.get("st", "0").split("-")[0])
        only = [int(x) for x in opt["only"].split("-")] if "only" in opt else None; white = [int(x) for x in opt["white"].split("-")] if "white" in opt else []
        chars, bounds = setup(src, zone, n)
        # 배율: 앞 영상에서 자른 대기 키에 맞춘다 (없으면 1단계 = H1)
        scales = [(idleH.get(st0 + i) or H1) / c["h"] for i, c in enumerate(chars)] if idleH else [H1 / chars[0]["h"]] * n
        continue
    nm, t0, t1, *rest = tok.split(":"); fps = int(rest[0]) if rest else 10; pin = "pin" in rest   # pin: 발을 바닥에 붙인다 (대기·달리기)
    fr = frames(src, float(t0), float(t1), fps)
    for ci, (bx0, bx1) in enumerate(bounds):
        st = st0 + ci; s = scales[ci]
        if only is not None and st not in only: continue
        bx0, bx1 = int(bx0), int(bx1); c = chars[ci]; ids = []
        for a in fr:
            sub = a[:, bx0:bx1]; m = key(sub, thr=13, hole=10 ** 9)
            r_, g_, b_ = sub[..., 0], sub[..., 1], sub[..., 2]; lum = sub.mean(axis=2)
            bgl = np.median(np.concatenate([sub[:4].reshape(-1, 3), sub[-4:].reshape(-1, 3)]), axis=0).mean()
            halo = (b_ > r_ + 8) & (b_ >= g_) & (lum > bgl + 4) & (lum < 75) & ~((g_ > r_ + 30) & (g_ >= b_ - 10))   # 빛이 번져 바탕보다 밝아진 남색 (검은 테두리·청록 불꽃은 아님)
            lb, nb = ndimage.label(halo | ~m); edge = set(np.unique(np.concatenate([lb[0], lb[-1], lb[:, 0], lb[:, -1]]))) - {0}
            m &= ~np.isin(lb, list(edge))
            near = (np.abs(sub - np.median(np.concatenate([sub[:4].reshape(-1, 3), sub[-4:].reshape(-1, 3)]), axis=0)).max(axis=2) < 40) & (lum >= bgl - 7) & (b_ > r_ + 6) & ~((g_ > r_ + 30) & (g_ >= b_ - 10))   # 고리 안쪽처럼 둘러싸인 넓은 남색 빛도 지운다 (검은 테두리보다는 밝은 것만)
            ln, nn = ndimage.label(near); szn = ndimage.sum(near, ln, range(1, nn + 1)); m &= ~np.isin(ln, [i + 1 for i in range(nn) if szn[i] > 400])
            lab, n = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, n + 1)); objs = ndimage.find_objects(lab); keep = []
            for i in range(n):
                if sz[i] <= 30: continue
                x0c, x1c = objs[i][1].start, objs[i][1].stop
                if "own" in c:                                      # 덩어리 가운데가 다른 캐릭터에 더 가까우면 그 캐릭터 것
                    mx = bx0 + (x0c + x1c) / 2
                    if min(c["own"], key=lambda q: abs(q - mx)) != c["cx"]: continue
                if "left" in c:                                     # 공격 영상: 이 캐릭터 몸 왼쪽 끝보다 오른쪽으로 뻗은 덩어리만, 오른쪽 경계에 닿은 건(옆 캐릭터 것) 버림
                    if bx0 + x1c <= c["left"] + 5: continue
                    if st < 2 and x1c >= sub.shape[1] - 1: continue
                keep.append(i + 1)
            m = np.isin(lab, keep)
            if st in white:                                         # 이 단계는 이펙트를 흰색으로: 몸에서 떨어진 큰 청록 덩어리만 (몸의 불꽃·눈은 그대로)
                rr, gg, bb2 = sub[..., 0], sub[..., 1], sub[..., 2]; teal = m & (gg > rr + 25) & (bb2 > rr + 15)
                lt, nt = ndimage.label(teal); ot = ndimage.find_objects(lt); szt = ndimage.sum(teal, lt, range(1, nt + 1))
                core = (c["cx"] - bx0 - c["h"] * 0.45, c["gy"] - c["h"] * 1.05, c["cx"] - bx0 + c["h"] * 0.45, c["gy"])
                sub = sub.copy()
                for i in range(nt):
                    y0c, y1c, x0c, x1c = ot[i][0].start, ot[i][0].stop, ot[i][1].start, ot[i][1].stop; cy_, cx_ = (y0c + y1c) / 2, (x0c + x1c) / 2
                    inside = core[0] <= cx_ <= core[2] and core[1] <= cy_ <= core[3]
                    big = (x1c - x0c) > c["h"] * 0.7 or (y1c - y0c) > c["h"] * 0.9          # 몸을 감싸는 큰 반달처럼 캐릭터보다 큰 덩어리도 이펙트
                    if szt[i] > 120 and (not inside or big):
                        mm = lt == i + 1; v = sub[..., :3].max(axis=2); sub[mm] = np.stack([v * 0.93, v * 0.95, v], axis=-1)[mm].astype(int)
            rgba = np.dstack([sub, m * 255]).astype(np.uint8); im = Image.fromarray(rgba, "RGBA")
            w, h = round(im.width * s), round(im.height * s); sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
            im2 = Image.fromarray(sm, "RGBA"); bb = im2.getbbox() or (0, 0, 1, 1)
            ax, gy = round((c["cx"] - bx0) * s), round(c["gy"] * s)        # 기준점: 첫 프레임의 발 가운데
            if pin: gy = bb[3]                                              # 발(맨 아래)을 바닥에 붙여 대기 중에 뜨지 않게
            crop = im2.crop(bb); cells.append(crop); ids.append([len(cells) - 1, bb[0] - ax, bb[1] - gy])
        meta["stages"][st][nm] = {"fps": fps, "f": ids}
        if nm == "idle": idleH[st] = max(cells[i].height for i, _, _ in ids)
W = 2048; x = y = rowh = 0; boxes = []
for c in cells:
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    boxes.append([x, y, c.width, c.height]); x += c.width + 1; rowh = max(rowh, c.height)
sheet = Image.new("RGBA", (W, y + rowh + 1))
for c, b in zip(cells, boxes): sheet.paste(c, (b[0], b[1]))
sheet.save(f"assets/hero_{LINE}.png", optimize=True)
meta["boxes"] = boxes; print(json.dumps(meta))
