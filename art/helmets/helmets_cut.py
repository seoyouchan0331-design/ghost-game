# 투구 그림 두 장 → assets/helmets.png (칸마다 투구 하나, 같은 계보는 같은 배율) + 좌표 JSON
#  helmets_v2_side_source.png : 4열 x 3줄 (병사 3, 사냥꾼 3, 마법사 4)
#  helmets_line1_side_source.png : 3열 x 4줄 (대장장이 3, 좀도둑 3, 나무꾼 3, 방패병 2)
import sys, os, json, base64, io
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "adv")); from keying import key
H_OUT = 22                                                  # 게임 속 기본(1단계) 투구 높이 px
SHEETS = [("art/helmets/helmets_v2_side_source.png", 4, 3, {"soldier": (0, 3), "hunter": (1, 3), "mage": (2, 4)}),
          ("art/helmets/helmets_line1_side_source.png", 3, 4, {"smith": (0, 3), "thief": (1, 3), "wood": (2, 3), "shield": (3, 2)})]
cells, meta = [], {}
for path, cols, rows, lines in SHEETS:
    a = np.asarray(Image.open(path).convert("RGB")).astype(int); Hh, Ww = a.shape[:2]
    m = key(a, thr=22, hole=10 ** 9)
    lab, n = ndimage.label(m); sizes = ndimage.sum(m, lab, range(1, n + 1)); objs = ndimage.find_objects(lab)
    groups = {}
    for i, sl in enumerate(objs):
        if sizes[i] < 30: continue
        cy, cx = (sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2
        groups.setdefault((int(cy / (Hh / rows)), int(cx / (Ww / cols))), []).append(i + 1)
    for name, (r, cnt) in lines.items():
        crops = []
        for c in range(cnt):
            ids = groups[(r, c)]; mm = np.isin(lab, ids); ys, xs = np.nonzero(mm)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            rgba = np.dstack([a, mm * 255]).astype(np.uint8)[y0:y1, x0:x1]; crops.append(Image.fromarray(rgba, "RGBA"))
        s = H_OUT / crops[0].height                          # 계보 안에서는 같은 배율 (진화할수록 커 보이게)
        meta[name] = []
        for im in crops:
            w, h = max(1, round(im.width * s)), max(1, round(im.height * s))
            sm = np.asarray(im.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
            meta[name].append(len(cells)); cells.append(Image.fromarray(sm, "RGBA"))
W = sum(c.width + 1 for c in cells); Hm = max(c.height for c in cells)
sheet = Image.new("RGBA", (W, Hm)); boxes = []; x = 0
for c in cells: sheet.paste(c, (x, Hm - c.height)); boxes.append([x, Hm - c.height, c.width, c.height]); x += c.width + 1
sheet.save("assets/helmets.png")
buf = io.BytesIO(); sheet.save(buf, "PNG", optimize=True)
json.dump({"lines": meta, "boxes": boxes}, open("art/helmets/helmets.json", "w"))
open("art/helmets/helmets_datauri.txt", "w").write("data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())
print(json.dumps({"lines": meta, "boxes": boxes}), len(buf.getvalue()))
