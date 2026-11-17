# 영상 프레임 중 한 동작 구간을 '몸'과 '이펙트'로 나눈다: 대기 모양(발 기준으로 겹친 것)을 조금 넓힌 자리 안 = 몸, 밖 = 이펙트.
# 이펙트는 assets/hero_<계보>_fx.png 로 따로 모으고, 게임은 그것만 크게 그릴 수 있다 (예: 서리 늑대 빙하 발톱이 커질 때).
# 실행: python3 art/heroframes/fx_split.py frostwolf claw   → index.html HERO.<계보>.stages[*].cfx, fxBoxes 를 고치고 시트에서 이펙트를 뺀다
# hero_cut.py 로 시트를 다시 만들면 fx_strip.py, 이 스크립트도 다시 돌려야 한다.
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
LINE, SEG = sys.argv[1], sys.argv[2]
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, end = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sheet = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).copy()
cells, fxb = [], []
for st, S in enumerate(H["stages"]):
    if "seg" not in S or SEG not in S["seg"]: continue
    R = 220; U = np.zeros((2 * R, 2 * R), bool)
    for ci, ox, oy in S["idle"]["f"]:
        x, y, w, h = B[ci]; U[R + oy:R + oy + h, R + ox:R + ox + w] |= sheet[y:y + h, x:x + w, 3] > 0
    U = ndimage.binary_dilation(U, iterations=3)
    a0, a1 = S["seg"][SEG]; S["cfx"] = {}
    for fi in range(a0, min(a1 + 1, len(S["attack"]["f"]))):
        ci, ox, oy = S["attack"]["f"][fi]; x, y, w, h = B[ci]; c = sheet[y:y + h, x:x + w]
        body = (c[..., 3] > 0) & U[R + oy:R + oy + h, R + ox:R + ox + w]; fx = (c[..., 3] > 0) & ~body
        if fx.sum() > 20:
            im = Image.fromarray(np.dstack([c[..., :3], fx * 255]).astype(np.uint8), "RGBA"); bb = im.getbbox()
            cells.append(im.crop(bb)); S["cfx"][str(fi)] = [len(cells) - 1, ox + bb[0], oy + bb[1]]
            c[..., 3] = np.where(body, 255, 0)                     # 시트에는 몸만 남긴다
W = 2048; x = y = rowh = 0
for c in cells:
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    fxb.append([x, y, c.width, c.height]); x += c.width + 1; rowh = max(rowh, c.height)
out = Image.new("RGBA", (W, y + rowh + 1))
for c, b in zip(cells, fxb): out.paste(c, (b[0], b[1]))
out.save(f"assets/hero_{LINE}_fx.png", optimize=True); Image.fromarray(sheet).save(f"assets/hero_{LINE}.png", optimize=True)
H["fxBoxes"] = fxb; s = s[:k] + json.dumps(H, separators=(",", ":")) + s[k + end:]; open("index.html", "w").write(s)
print("fx cells", len(cells))
