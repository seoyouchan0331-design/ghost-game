# 프레임마다 몸이 영상 속에서 얼마나 옮겨 갔는지(루트 이동, 대기 몸 가운데 기준 px)를 재서 HERO.<계보>.rx[칸 번호]에 넣는다
# 게임은 동작 중 이 값만큼 캐릭터를 실제로 옮기고, 그림은 제자리에 그린다 (그림과 판정·위치가 같이 간다)
# 몸 가운데 = 불꽃(청록)·금화·흰 빛을 뺀 불투명 픽셀 x의 중앙값. 동작마다 앞뒤 3장 중앙값으로 고른다
# 실행: python3 art/heroframes/hero_rx.py thief   (hero_cut.py나 fx_*로 프레임을 바꾸면 다시)
import sys, json, numpy as np
from PIL import Image
LINE = sys.argv[1]
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, end = json.JSONDecoder().raw_decode(s[k:]); B = H["boxes"]
sh = np.asarray(Image.open(f"assets/hero_{LINE}.png").convert("RGBA")).astype(int)
def med(ci, ox):
    x, y, w, h = B[ci]; c = sh[y:y + h, x:x + w]; r, g, b = c[..., 0], c[..., 1], c[..., 2]
    body = (c[..., 3] > 0) & ~((g > r + 25) & (b > r + 15)) & ~((r > 140) & (g > 90) & (b < 100)) & ~(c[..., :3].min(2) > 180)
    xs = np.nonzero(body)[1]
    return None if len(xs) < 20 else ox + float(np.median(xs))
RX = [0] * len(B)
for S in H["stages"]:
    base = float(np.median([med(ci, ox) for ci, ox, oy in S["idle"]["f"]]))
    for mv, M in S.items():
        if not isinstance(M, dict) or "f" not in M or mv in ("idle", "run"): continue
        v = [med(ci, ox) for ci, ox, oy in M["f"]]
        v = [base if q is None else q for q in v]
        for i, (ci, ox, oy) in enumerate(M["f"]):
            RX[ci] = round(float(np.median(v[max(0, i - 1):i + 2])) - base)
H["rx"] = RX
open("index.html", "w").write(s[:k] + json.dumps(H, separators=(",", ":")) + s[k + end:]); print("rx", min(RX), max(RX))
