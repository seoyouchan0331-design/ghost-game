# 땅에 놓인 투구 그림: 라인업 그림(art/heroframes/<계보>_lineup_source.*)의 세 단계 캐릭터에서 머리(투구)만 떼어 게임 크기로 줄인다
# 바탕(어두운 남색)과의 차이로 투명 처리 → 청록 유령불·금화 빼기 → 캐릭터 3명을 가로로 나누기 → 몸 높이 위쪽 HEAD 비율만 → 가장 큰 덩어리 → 게임 대기 키에 맞춰 BOX 축소
# 실행: python3 art/heads/head_cut.py   → assets/hero_heads.png, 출력 JSON을 index.html의 HEADS에
import json, numpy as np
from PIL import Image
from scipy import ndimage
LINES = ["soldier", "hunter", "frostwolf", "executioner", "thief"]
HEAD = {"soldier": 0.46, "hunter": 0.5, "frostwolf": 0.5, "executioner": 0.48, "thief": 0.52}
SKIP = {("executioner", 2): 0.3}   # 단두대 틀처럼 머리 위에 솟은 것은 위에서 이만큼 건너뛴다
s = open("index.html").read()
out, cells = {}, []
for ln in LINES:
    import glob
    src = glob.glob(f"art/heroframes/{ln}_lineup_source.*")[0]
    a = np.asarray(Image.open(src).convert("RGB")).astype(int); H, W, _ = a.shape
    bg = np.median(np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3)]), axis=0)
    m = ndimage.binary_fill_holes(ndimage.binary_opening(np.abs(a - bg).max(2) > 14, iterations=1))   # 어두운 모자도 바탕과 나뉘게 문턱을 낮추고 구멍을 메운다
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    teal = (g > r + 40) & (b > r + 15) & (g > 100)
    gold = (r > 170) & (g > 120) & (b < 110) & (r > b + 70)
    body = ndimage.binary_opening(ndimage.binary_fill_holes(m & ~teal & ~gold), iterations=2)   # 몸(불꽃·금화 뺀 것). 눈처럼 안쪽 청록은 구멍 메우기로 돌아온다
    cs = np.convolve(body.sum(0), np.ones(31) / 31, "same")                # 캐릭터 3명: 몸이 가장 적은 세로줄 두 곳에서 나눈다
    c1 = int(W * 0.18) + int(np.argmin(cs[int(W * 0.18):int(W * 0.45)])); c2 = int(W * 0.48) + int(np.argmin(cs[int(W * 0.48):int(W * 0.75)]))
    runs = [(0, c1), (c1, c2), (c2, W)]
    k = json.JSONDecoder().raw_decode(s[s.index(f"{ln}: ", s.index("const HERO = {")) + len(ln) + 2:])[0]
    out[ln] = []
    for st, (x0, x1) in enumerate(runs):
        core = ndimage.binary_opening(body[:, x0:x1], iterations=7)            # 창·칼처럼 가는 것은 빼고 머리 꼭대기를 찾는다
        ys = np.nonzero(core.sum(1) > 2)[0]; y0, y1 = ys.min(), ys.max() + 1
        y0 += int((y1 - y0) * SKIP.get((ln, st), 0)); hy = y0 + int((y1 - y0) * HEAD[ln])
        cx = np.nonzero(core[y0:hy].any(0))[0]; x0, x1 = x0 + max(0, cx.min() - 6), x0 + cx.max() + 7   # 머리 둘레만 (옆 무기 빼기)
        part = body[y0:hy, x0:x1] & ~gold[y0:hy, x0:x1]
        pl, pn = ndimage.label(part)                                          # 떨어진 작은 조각(불꽃 끝·반짝이)만 지운다
        if pn > 1: ps = ndimage.sum(part, pl, range(1, pn + 1)); part = np.isin(pl, [j + 1 for j in range(pn) if ps[j] >= part.sum() * 0.02])
        ys, xs = np.nonzero(part); py0, py1, px0, px1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([a[y0:hy, x0:x1], part * 255]).astype(np.uint8)[py0:py1, px0:px1]
        # 게임 크기: 그 단계 대기 그림 높이(불꽃 포함) / 라인업 몸 높이(불꽃 포함 덩어리)
        S = k["stages"][min(st, len(k["stages"]) - 1)]; ih = max(k["boxes"][c][3] for c, _, _ in S["idle"]["f"])
        full = np.nonzero(m[:, x0:x1].sum(1) > 3)[0]; sc = ih / (full.max() - full.min() + 1)
        im = Image.fromarray(rgba, "RGBA"); w, h = max(1, round(im.width * sc)), max(1, round(im.height * sc))
        sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 120, 255, 0)
        cells.append(Image.fromarray(sm, "RGBA")); out[ln].append(len(cells) - 1)
x = 0; boxes = []; H2 = max(c.height for c in cells)
sheet = Image.new("RGBA", (sum(c.width + 1 for c in cells), H2))
for c in cells: sheet.paste(c, (x, 0)); boxes.append([x, 0, c.width, c.height]); x += c.width + 1
sheet.save("assets/hero_heads.png", optimize=True)
print(json.dumps({"boxes": boxes, "lines": out}, separators=(",", ":")))
