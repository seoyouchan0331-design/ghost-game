# 골렘 무너짐 영상 → 게임 프레임 시트 (assets/giant_collapse.png)
# 첫 프레임의 골렘을 게임 몸통(body2)과 같은 크기·같은 자리에 맞춘다: 폭을 맞추고 아래 가운데를 맞춘다.
import sys, json, subprocess, glob, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
FPS = 10; TMP = "/tmp/collapse_frames"; os.makedirs(TMP, exist_ok=True)
for f in glob.glob(TMP + "/*.png"): os.remove(f)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "art/boss1/collapse_source.mp4", "-vf", f"fps={FPS}", TMP + "/f%03d.png"], check=True)
files = sorted(glob.glob(TMP + "/*.png"))
GI = json.loads(open("index.html").read().split("const GIANT = ")[1].split(";")[0])
gi = Image.open("assets/giant.png").convert("RGBA"); b2 = GI["body2"]; body = gi.crop((b2[0], b2[1], b2[0] + b2[2], b2[1] + b2[3]))
bx0, by0, bx1, by1 = body.getbbox()
masks = []
for f in files:
    a = np.asarray(Image.open(f).convert("RGB")).astype(int); m = key(a, thr=14, hole=4000); masks.append((a, m))
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
sheet.quantize(256, method=Image.FASTOCTREE).convert("RGBA").save("assets/giant_collapse.png", optimize=True)
# 기준점: 영상 첫 프레임 골렘의 아래 가운데 = 몸통 그림의 아래 가운데 (body2 그림 기준 bx, by)
ax = ((vx0 + vx1) / 2 - ux0) * s; ay = (vy1 - uy0) * s
print(json.dumps({"w": W, "h": H, "cols": cols, "n": len(cells), "fps": FPS, "ax": round(ax), "ay": round(ay), "bodyCx": (bx0 + bx1) / 2 - b2[2] / 2, "bodyBottom": by1 - b2[3]}))
