# 땅에 놓인 투구·Tab 창 투구 그림: 사용자가 직접 머리만 떼어 온 그림(art/heads/<계보>_heads_source.png, 투명 바탕)을 게임 크기로.
# 없는 계보(병사)는 head_cut.py가 라인업에서 자른 칸을 그대로 쓴다. 순서: 위쪽 줄 먼저, 같은 줄은 왼쪽부터 = 1·2·3단계
# 크기: head_cut.py 칸 너비(몸만)와 새 그림의 몸(불꽃·금화 뺀) 너비를 맞춘다.  실행: python3 art/heads/head_cut.py > /tmp/h.json; python3 art/heads/heads_pack.py /tmp/h.json
import sys, json, os, numpy as np
from PIL import Image
from scipy import ndimage
old = json.load(open(sys.argv[1])); oldimg = Image.open("assets/hero_heads.png").convert("RGBA")
cells, lines = [], {}
for ln, idx in old["lines"].items():
    src = f"art/heads/{ln}_heads_source.png"
    if not os.path.exists(src):
        lines[ln] = []
        for i in idx: x, y, w, h = old["boxes"][i]; cells.append(oldimg.crop((x, y, x + w, y + h))); lines[ln].append(len(cells) - 1)
        continue
    im = Image.open(src).convert("RGBA"); a = np.asarray(im).astype(int); al = a[..., 3] > 40
    lab, n = ndimage.label(ndimage.binary_dilation(al, iterations=25)); sz = ndimage.sum(al, lab, range(1, n + 1))
    big = [i + 1 for i in np.argsort(sz)[::-1][:3]]; objs = [ndimage.find_objects(lab)[i - 1] for i in big]
    low = min(o[0].stop for o in objs); objs.sort(key=lambda o: (o[0].start > low, o[1].start))   # 다른 그림보다 완전히 아래에 있으면 아랫줄 → 같은 줄은 왼쪽부터
    lines[ln] = []
    for st, o in enumerate(objs):
        crop = a[o[0], o[1]].copy(); crop[..., 3] = np.where((lab[o[0], o[1]] == big[[ndimage.find_objects(lab)[b - 1] for b in big].index(o)]) & (crop[..., 3] > 40), 255, 0)
        r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]; body = (crop[..., 3] > 0) & ~((g > r + 40) & (b > r + 15) & (g > 100)) & ~((r > 170) & (g > 120) & (b < 110))
        xs = np.nonzero(body.sum(0) > 2)[0]; bw = xs.max() - xs.min() + 1
        tw = old["boxes"][idx[min(st, len(idx) - 1)]][2]; sc = tw / bw
        ys, xs2 = np.nonzero(crop[..., 3] > 0); crop = crop[ys.min():ys.max() + 1, xs2.min():xs2.max() + 1]
        pim = Image.fromarray(crop.astype(np.uint8), "RGBA"); sc = min(sc, 46 / pim.height)   # 단두대처럼 아주 큰 것은 키 46px까지
        w, h = max(1, round(pim.width * sc)), max(1, round(pim.height * sc))
        sm = np.asarray(pim.resize((w, h), Image.BOX)).copy(); sm[..., 3] = np.where(sm[..., 3] > 110, 255, 0)
        cells.append(Image.fromarray(sm, "RGBA")); lines[ln].append(len(cells) - 1)
x = 0; boxes = []; H2 = max(c.height for c in cells); sheet = Image.new("RGBA", (sum(c.width + 1 for c in cells), H2))
for c in cells: sheet.paste(c, (x, 0)); boxes.append([x, 0, c.width, c.height]); x += c.width + 1
sheet.save("assets/hero_heads.png", optimize=True); print(json.dumps({"boxes": boxes, "lines": lines}, separators=(",", ":")))
