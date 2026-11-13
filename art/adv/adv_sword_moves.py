# 검사 영상 3개(달리기·그로기+포션·점프 내려찍기)에서 프레임을 골라 assets/adv_sword_moves.png 로 만든다.
# 베기 영상(adv_sword_anim.py)과 같은 크기(K=0.073, 70x70 칸, 발 34,58)로 맞춘다. 실행: python3 art/adv/adv_sword_moves.py (ffmpeg 필요)
import subprocess, tempfile, json
import numpy as np
from PIL import Image
K = 0.073; S = round(960 * K)
SRC = {"run": "art/adv/sword_run_source.mp4", "groggy": "art/adv/sword_groggy_source.mp4", "jump": "art/adv/sword_jump_source.mp4"}
# (이름, 영상, 프레임, 위치 맞춤): "feet"=영상 속 발 높이 그대로, "head"=공중 프레임은 머리를 서 있을 때 높이로 내린다
PICK = [("run", "run", i, "feet") for i in range(12, 28, 2)] + [
  ("crouch", "jump", 16, "feet"), ("air", "jump", 32, "head"), ("air", "jump", 44, "head"),
  ("slam", "jump", 64, "feet"), ("slam", "jump", 80, "feet"), ("rise", "jump", 104, "feet"),
  ("groggy", "groggy", 32, "feet"), ("groggy", "groggy", 48, "feet"),
  ("potion", "groggy", 88, "feet"), ("potion", "groggy", 96, "feet"), ("potion", "groggy", 104, "feet")]
FEET = {"run": 767, "groggy": 796, "jump": 796}; HAIRX = {"run": 520, "groggy": 512, "jump": 517}
tmp = tempfile.mkdtemp(); out = Image.new("RGBA", (S * len(PICK), S)); anims = {}
for v, path in SRC.items(): subprocess.run(["ffmpeg", "-v", "error", "-i", path, f"{tmp}/{v}_%03d.png"], check=True)
for j, (name, v, i, mode) in enumerate(PICK):
    a = np.asarray(Image.open(f"{tmp}/{v}_{i + 1:03d}.png").convert("RGB")).astype(int); bg = a[5, 5]
    al = (np.abs(a - bg).sum(2) > 45).astype(np.uint8) * 255
    dy = 796 - FEET[v]
    if mode == "head": hy = np.where((a[..., 0] > 150) & (a[..., 1] < 90) & (a[..., 2] < 90))[0]; dy = 250 - int(hy.min())
    dx = 523 - HAIRX[v]
    rgba = Image.fromarray(np.dstack([a.astype(np.uint8), al]), "RGBA"); big = Image.new("RGBA", (960, 960)); big.paste(rgba, (dx, dy))
    s = np.asarray(big.resize((S, S), Image.BOX)).copy(); s[..., 3] = np.where(s[..., 3] > 120, 255, 0)
    out.paste(Image.fromarray(s), (j * S, 0)); anims.setdefault(name, []).append(j)
out.save("assets/adv_sword_moves.png"); print(json.dumps(anims))
