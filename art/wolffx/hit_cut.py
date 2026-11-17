# 서리 송곳니 피격 이펙트: 밝은 회색 바탕 GIF(보라) → 투명 + 푸른 계열로 바꿔 assets/gfx_whit.png
import json, numpy as np, colorsys
from PIL import Image, ImageSequence
K = 0.32; BG = 242.0
src = Image.open("art/wolffx/hit_source.gif"); frames = []
for f in ImageSequence.Iterator(src):
    c = np.asarray(f.convert("RGB")).astype(float)
    a = np.clip(np.maximum((c.max(2) - BG) * 16, (BG - c.min(2)) * 2.4), 0, 255) / 255
    t = np.clip((c - BG * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0, 255) / 255   # 바탕을 빼서 원래 색
    r, g, b = t[..., 0], t[..., 1], t[..., 2]; mx = t.max(2); mn = t.min(2); d = mx - mn + 1e-6
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    s = np.where(mx > 0, d / (mx + 1e-6), 0); v = mx
    h = (200 + (h * 360 - 255) * 0.35) / 360 % 1                                     # 보라~파랑 → 하늘~파랑
    s = np.clip(s * 1.1, 0, 1); v = np.where(v > 0.55, v ** 0.45, v); s = np.where(v > 0.55, np.maximum(s, 0.12), s)   # 밝은 곳은 더 밝고 살짝 푸르게
    s = np.where(v < 0.55, np.maximum(s, 0.45), s)                                    # 어두운 조각은 짙은 남색으로
    hi = (h * 6).astype(int) % 6; fr = h * 6 - np.floor(h * 6)
    p_, q_, t_ = v * (1 - s), v * (1 - fr * s), v * (1 - (1 - fr) * s)
    rgb = np.select([hi[..., None] == i for i in range(6)], [np.dstack(x) for x in [(v, t_, p_), (q_, v, p_), (p_, v, t_), (p_, q_, v), (t_, p_, v), (v, p_, q_)]])
    frames.append(Image.fromarray(np.dstack([rgb * 255, a * 255]).clip(0, 255).astype(np.uint8), "RGBA"))
bb = None
for f in frames:
    b = f.getchannel("A").point(lambda x: 255 if x > 20 else 0).getbbox()
    if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
W, H = round((bb[2] - bb[0]) * K), round((bb[3] - bb[1]) * K); out = Image.new("RGBA", (W * len(frames), H))
for i, f in enumerate(frames):
    f = f.crop(bb).resize((W, H), Image.BOX); al = np.asarray(f.getchannel("A")); f.putalpha(Image.fromarray(np.where(al < 24, 0, al).astype(np.uint8)))
    out.paste(f, (i * W, 0))
out.save("assets/gfx_whit.png", optimize=True)
print(json.dumps({"whit": {"w": W, "h": H, "cols": len(frames), "n": len(frames), "fps": 16, "px": W // 2, "py": H // 2}}))
