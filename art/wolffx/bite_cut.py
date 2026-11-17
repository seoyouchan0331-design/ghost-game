# 서리 늑대 물기 이펙트 영상(마누스) → assets/gfx_wbitev.png. 옆모습 물기 구간(3.6~6.4초)만, 배경 남색을 빼서 빛으로 더하는(lighter) 그림으로.
# 실행: python3 art/wolffx/bite_cut.py  → GFX 좌표 JSON 출력
import subprocess, glob, os, json, numpy as np
from PIL import Image
T = "/tmp/wolf_bite_frames"; os.makedirs(T, exist_ok=True)
for f in glob.glob(T + "/*.png"): os.remove(f)
# 나타나기(3.75~4.2초) + 벌린 채 잠깐 + 닫힘·섬광·조각·서리 고리(5.0~6.3초). 벌리고 오래 기다리는 부분은 뺀다
fr = []
for a_, b_ in ((3.75, 4.25), (5.0, 6.3)):
    for f in glob.glob(T + "/*.png"): os.remove(f)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a_), "-to", str(b_), "-i", "art/wolffx/bite_source.mp4", "-vf", "fps=15", T + "/f%03d.png"], check=True)
    fr += [np.asarray(Image.open(f).convert("RGB")).astype(int) for f in sorted(glob.glob(T + "/*.png"))]
bg = np.median(np.concatenate([fr[0][:30].reshape(-1, 3), fr[0][-30:].reshape(-1, 3)]), axis=0)
lit = [np.clip(a - bg - 6, 0, 255) for a in fr]                     # 배경을 빼면 빛만 남는다 (검정 = 투명)
m = np.zeros(lit[0].shape[:2], bool)
for a in lit: m |= a.max(axis=2) > 18
ys, xs = np.where(m); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
K = 0.1                                                           # 게임 크기 (작게)
w, h = round((x1 - x0) * K), round((y1 - y0) * K); cols = max(1, 2048 // w)
sheet = Image.new("RGB", (cols * w, ((len(lit) + cols - 1) // cols) * h))
for i, a in enumerate(lit): sheet.paste(Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).resize((w, h), Image.LANCZOS), ((i % cols) * w, (i // cols) * h))
sheet.save("assets/gfx_wbitev.png", optimize=True)
# 기준점: 닫힌 턱 끝(오른쪽 가운데 쪽) — 물린 자리에 맞춘다
px, py = round((x1 - x0) * 0.72 * K), round((y1 - y0) * 0.5 * K)
print(json.dumps({"wbitev": {"w": w, "h": h, "cols": cols, "n": len(lit), "fps": 15, "px": px, "py": py}}))
