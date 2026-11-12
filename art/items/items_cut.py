# Higgsfield 아이템 시트(5x4 격자, 기획서 순서)를 잘라 배경을 지우고 두 크기로 묶는다.
# assets/items48.png: 캐릭터 창용 (48px) / assets/items16.png: 게임 화면 상점 진열대용 (16px)
import numpy as np
from PIL import Image
src = Image.open("items_source.png").convert("RGB"); a = np.asarray(src).astype(int)
bg = np.median(a[:30, :30].reshape(-1, 3), axis=0)
CW, CH = src.width // 5, src.height // 4
out = {48: Image.new("RGBA", (48 * 20, 48)), 16: Image.new("RGBA", (16 * 20, 16))}
for i in range(20):
    r, c = divmod(i, 5); cell = a[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW]
    m = np.abs(cell - bg).max(axis=2) > 16
    rgba = Image.fromarray(np.dstack([cell.astype(np.uint8), (m * 255).astype(np.uint8)]), "RGBA")
    rgba = rgba.crop(rgba.getbbox()); s = max(rgba.size); sq = Image.new("RGBA", (s, s)); sq.paste(rgba, ((s - rgba.width) // 2, (s - rgba.height) // 2))
    for n, img in out.items():
        t = sq.resize((n, n), Image.BOX); px = np.asarray(t).copy(); px[..., 3] = np.where(px[..., 3] > 110, 255, 0)
        img.paste(Image.fromarray(px, "RGBA"), (i * n, 0))
for n, img in out.items(): img.save(f"../../assets/items{n}.png")
print("ok")
