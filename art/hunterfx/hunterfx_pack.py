# 사냥꾼 화살 이펙트: pixelfx(저장소 Pixel/pixelfx: projectiles/emerald-arrow, emerald-power-arrow, emerald-release, --sheet) → assets/gfx_*.png
# art/golemfx/golemfx_pack.py와 같은 방식. 실행: python3 art/hunterfx/hunterfx_pack.py <render --out 폴더>
import sys, json
from PIL import Image
src = sys.argv[1]  # render --out 폴더
out = {}
for key, sid in [("harrow", "projectiles/emerald-arrow"), ("hpow", "projectiles/emerald-power-arrow"), ("hrel", "projectiles/emerald-release")]:
    name = sid.split("/")[1]; j = json.load(open(f"{src}/{sid}/{name}.json")); im = Image.open(f"{src}/{sid}/{name}.png").convert("RGBA")
    m = j["meta"]["pixelfx"]; fw, fh = m["frameSize"]; fr = [f["frame"] for f in j["frames"]]
    cells = [im.crop((f["x"], f["y"], f["x"] + fw, f["y"] + fh)) for f in fr]
    while cells and cells[-1].getbbox() is None: cells.pop()
    bb = [c.getbbox() for c in cells if c.getbbox()]; x0 = min(b[0] for b in bb); y0 = min(b[1] for b in bb); x1 = max(b[2] for b in bb); y1 = max(b[3] for b in bb)
    w, h = x1 - x0, y1 - y0; cols = max(1, 2048 // w); rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w, rows * h))
    for i, c in enumerate(cells): sheet.paste(c.crop((x0, y0, x1, y1)), ((i % cols) * w, (i // cols) * h))
    sheet.quantize(256, method=Image.FASTOCTREE).convert("RGBA").save(f"assets/gfx_{key}.png", optimize=True)
    out[key] = {"w": w, "h": h, "cols": cols, "n": len(cells), "fps": m["fps"], "px": m["pivot"][0] - x0, "py": m["pivot"][1] - y0}
print(json.dumps(out))
