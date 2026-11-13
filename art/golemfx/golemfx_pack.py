# pixelfx 시트(저장소 Pixel/pixelfx: fire/golem-meteor, nature/lava-crater, nature/lava-spire, --sheet --fps 15)를
# 게임용으로: 모든 프레임의 공통 바깥 상자로 잘라 한 장에 다시 깔고, 256색으로 줄인다. 좌표는 index.html GFX 상수로.
import sys, json
from PIL import Image
src = sys.argv[1]  # render --out 폴더
out = {}
for key, sid in [("meteor", "fire/golem-meteor"), ("crater", "nature/lava-crater"), ("spire", "nature/lava-spire")]:
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
