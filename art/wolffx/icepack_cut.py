# 얼음 공격 모음 GIF(어두운 바탕, 50프레임 반복)에서 쓸 칸을 잘라 assets/gfx_<key>.png 로. 출력 JSON은 index.html GFX에 넣는다
# wice 얼음에 갇힘(자라서 멈춤) / wbreak 금 가고 깨짐 / wring 땅에서 솟는 가시 고리(눈보라 포효) / wstar 번쩍 별(깨질 때) / wwind 찬바람(서리 질주)
import json, numpy as np
from PIL import Image, ImageSequence
src = Image.open("art/wolffx/icepack_source.gif"); F = [np.asarray(f.convert("RGB")).astype(int) for f in ImageSequence.Iterator(src)]
BG = np.array([11, 14, 20])
CUT = {  # 칸 (y0, y1, x0, x1), 프레임 구간, 크기 비율, 기준점("bottom" 발밑 / "mid" 가운데)
    "wice":   ((29, 144, 250, 380), range(31, 46), 0.55, "bottom"),
    "wbreak": ((29, 144, 250, 380), range(46, 65), 0.55, "bottom"),
    "wring":  ((175, 308, 30, 250), range(53, 78), 0.6, "bottom"),
    "wstar":  ((338, 434, 328, 508), range(29, 37), 0.5, "mid"),
    "wwind":  ((29, 144, 390, 600), range(0, 24), 0.42, "mid"),
}
out = {}
for key, ((y0, y1, x0, x1), rng, K, piv) in CUT.items():
    fr, last = [], None
    for t in rng:
        c = F[t][y0:y1, x0:x1]
        if last is not None and np.array_equal(c, last): continue          # 같은 프레임이 두 번씩 들어 있다
        last = c; a = ((np.abs(c - BG).sum(2) > 30) & (c.max(2) > 60)) * 255   # 어두운 번짐은 뺀다
        fr.append(Image.fromarray(np.dstack([c, a]).astype(np.uint8), "RGBA"))
    bb = None
    for f in fr:
        b = f.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    W, H = round((bb[2] - bb[0]) * K), round((bb[3] - bb[1]) * K); sheet = Image.new("RGBA", (W * len(fr), H))
    for i, f in enumerate(fr):
        f = f.crop(bb).resize((W, H), Image.BOX); al = np.asarray(f.getchannel("A")); f.putalpha(Image.fromarray(np.where(al < 110, 0, 255).astype(np.uint8)))
        sheet.paste(f, (i * W, 0))
    sheet.save(f"assets/gfx_{key}.png", optimize=True)
    out[key] = {"w": W, "h": H, "cols": len(fr), "n": len(fr), "fps": 14, "px": W // 2, "py": H - 2 if piv == "bottom" else H // 2}
print(json.dumps(out, separators=(",", ":")))
