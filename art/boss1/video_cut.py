# 골렘 영상 → 게임 프레임 시트. python3 art/boss1/video_cut.py <영상> <출력 png> <몸통 그림 body|body2> [초당 프레임] [시작 초] [끝 초]
#   무너짐: art/boss1/collapse_source.mp4 assets/giant_collapse.png body2 10
#   포효:   art/boss1/roar_source.mp4 assets/giant_roar.png body 10 0.3 4.6
#   숨쉬기: art/boss1/breath_source.mp4 assets/giant_breath.png body 8 1.7   (1.7초 앞은 팔 끝이 막혀 있어서 뺀다: 반복할 때 구멍이 막혔다 뚫렸다 함)
# 첫 프레임의 골렘을 게임 몸통과 같은 크기·같은 자리에 맞춘다: 폭을 맞추고 아래 가운데를 맞춘다.
import sys, json, subprocess, glob, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
SRC, OUT, REF = sys.argv[1], sys.argv[2], sys.argv[3]; FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 10
T0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0; T1 = float(sys.argv[6]) if len(sys.argv) > 6 else 999
TMP = "/tmp/collapse_frames"; os.makedirs(TMP, exist_ok=True)
for f in glob.glob(TMP + "/*.png"): os.remove(f)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-to", str(T1), "-i", SRC, "-vf", f"fps={FPS}", TMP + "/f%03d.png"], check=True)
files = sorted(glob.glob(TMP + "/*.png"))
GI = json.loads(open("index.html").read().split("const GIANT = ")[1].split(";")[0])
gi = Image.open("assets/giant.png").convert("RGBA"); b2 = GI[REF]; body = gi.crop((b2[0], b2[1], b2[0] + b2[2], b2[1] + b2[3]))
bx0, by0, bx1, by1 = body.getbbox()
from scipy import ndimage
def key2(a, hole=600):
    # 바탕: 회색 바탕과 거의 같은 색 + 핵 빛을 받아 밝아진 바탕(밝고 색이 옅은 곳). 테두리와 이어진 것과, 몸 사이에 갇힌 덩어리(hole 이상)를 지운다
    bg = np.median(np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)]), axis=0)
    lum = a.mean(axis=2); sat = a.max(axis=2) - a.min(axis=2)
    strict = np.abs(a - bg).max(axis=2) <= 16
    back = ndimage.binary_opening(strict | ((lum >= bg.mean() - 8) & (sat <= 48)), iterations=1)
    lab, n = ndimage.label(back)                              # 넓은 기준: 테두리와 이어진 것만 (빛 번진 바탕)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = ~np.isin(lab, list(edge))
    ls, ns = ndimage.label(strict & m); ss = ndimage.sum(strict, ls, range(1, ns + 1))   # 좁은 기준(진짜 회색)만 갇힌 구멍으로 지운다
    m &= ~np.isin(ls, [i + 1 for i in range(ns) if ss[i] > hole])
    # 남은 조각 중 아주 작은 것(빛줄기 부스러기)은 버린다
    l2, n2 = ndimage.label(m); s2 = ndimage.sum(m, l2, range(1, n2 + 1)); return np.isin(l2, [i + 1 for i in range(n2) if s2[i] >= 40])
masks = []
for f in files:
    a = np.asarray(Image.open(f).convert("RGB")).astype(int); m = key2(a); masks.append((a, m))
ys, xs = np.nonzero(masks[0][1]); vx0, vx1, vy1 = xs.min(), xs.max() + 1, ys.max() + 1
s = (bx1 - bx0) / (vx1 - vx0)                              # 영상 px → 게임 px
# 모든 프레임의 공통 상자 (영상 좌표)
U = [np.nonzero(m) for _, m in masks]; ux0 = min(u[1].min() for u in U); ux1 = max(u[1].max() for u in U) + 1; uy0 = min(u[0].min() for u in U); uy1 = max(u[0].max() for u in U) + 1
W, H = round((ux1 - ux0) * s), round((uy1 - uy0) * s)
cells = []
for a, m in masks:
    rgba = np.dstack([a, m * 255]).astype(np.uint8)[uy0:uy1, ux0:ux1]
    im = Image.fromarray(rgba, "RGBA").resize((W, H), Image.BOX); arr = np.asarray(im).copy(); arr[..., 3] = np.where(arr[..., 3] > 127, 255, 0); cells.append(Image.fromarray(arr, "RGBA"))
cols = max(1, 2048 // W); rows = (len(cells) + cols - 1) // cols; sheet = Image.new("RGBA", (cols * W, rows * H))
for i, c in enumerate(cells): sheet.paste(c, ((i % cols) * W, (i // cols) * H))
sheet.quantize(256, method=Image.FASTOCTREE).convert("RGBA").save(OUT, optimize=True)
# 기준점: 영상 첫 프레임 골렘의 아래 가운데 = 몸통 그림의 아래 가운데 (body2 그림 기준 bx, by)
ax = ((vx0 + vx1) / 2 - ux0) * s; ay = (vy1 - uy0) * s
print(json.dumps({"w": W, "h": H, "cols": cols, "n": len(cells), "fps": FPS, "ax": round(ax), "ay": round(ay), "bodyCx": (bx0 + bx1) / 2 - b2[2] / 2, "bodyBottom": by1 - b2[3]}))
