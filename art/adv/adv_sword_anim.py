# 검사 베기 영상(art/adv/sword_slash_source.mp4, 960x960 24fps)에서 프레임 10장을 골라 assets/adv_sword_anim.png 로 만든다.
# 실행: python3 art/adv/adv_sword_anim.py   (ffmpeg 필요)
import subprocess, tempfile, os, json
import numpy as np
from PIL import Image
SRC = "art/adv/sword_slash_source.mp4"
PICK = [0, 10, 30, 45, 60, 76, 78, 80, 86, 108]   # 대기, 준비 4, 휘두름 3, 뻗은 끝, 돌아오기
K = 0.073                                        # 몸 높이 약 40px
BG = np.array([33, 30, 47])
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, f"{tmp}/a%03d.png"], check=True)
S = round(960 * K); out = Image.new("RGBA", (S * len(PICK), S))
for j, i in enumerate(PICK):
    a = np.asarray(Image.open(f"{tmp}/a{i + 1:03d}.png").convert("RGB")).astype(int)
    al = (np.abs(a - BG).sum(2) > 45).astype(np.uint8) * 255
    im = Image.fromarray(np.dstack([a.astype(np.uint8), al]), "RGBA").resize((S, S), Image.BOX)
    s = np.asarray(im).copy(); s[..., 3] = np.where(s[..., 3] > 120, 255, 0)
    out.paste(Image.fromarray(s), (j * S, 0))
out.save("assets/adv_sword_anim.png")
print(json.dumps({"size": S, "n": len(PICK), "footX": round(470 * K), "footY": round(797 * K)}))
