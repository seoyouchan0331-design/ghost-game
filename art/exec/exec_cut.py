# 처형인 그림: 처형 마크 6칸(3x2 격자) → assets/exec_marks.png, 단두대 부품 5개(연결 성분) → assets/exec_guillo.png. 좌표 JSON 출력
import json, numpy as np
from PIL import Image
from scipy import ndimage
def cutout(a, bg, thr=38):
    d = np.abs(a[..., :3].astype(int) - bg).max(2); al = np.clip((d - thr * 0.6) * 255 / max(1, thr * 0.4), 0, 255)
    return np.dstack([a[..., :3], al]).astype(np.uint8)
def shrink(im, w, h):
    im = im.resize((w, h), Image.BOX); a = np.asarray(im).copy(); a[..., 3] = np.where(a[..., 3] > 100, 255, 0); return Image.fromarray(a, "RGBA")
out = {}
# 마크: 3x2, 각 칸을 18px 안에
m = np.asarray(Image.open("art/exec/marks_source.png").convert("RGB")); bg = m[5, 5].astype(int); H, W = m.shape[:2]; cells = []
for r in range(2):
    for c in range(3):
        a = m[r * H // 2:(r + 1) * H // 2, c * W // 3:(c + 1) * W // 3].astype(float)   # 바탕을 빼서 빛 번짐까지 반투명으로 살린다 (작은 아이콘이라 테두리가 날아가지 않게)
        al = np.clip((np.abs(a - bg).max(2) - 8) / 60, 0, 1); col = np.clip((a - bg * (1 - al[..., None])) / np.maximum(al[..., None], 0.05), 0, 255)
        sub = Image.fromarray(np.dstack([col, al * 255]).astype(np.uint8), "RGBA"); bb = sub.getbbox(); sub = sub.crop(bb)
        k = 22 / max(sub.size); cells.append(sub.resize((max(1, round(sub.width * k)), max(1, round(sub.height * k))), Image.BOX))   # 부드러운 알파 그대로
S = 22; sheet = Image.new("RGBA", (S * 6, S))
for i, c in enumerate(cells): sheet.paste(c, (i * S + (S - c.width) // 2, (S - c.height) // 2))
sheet.save("assets/exec_marks.png", optimize=True); out["marks"] = {"s": S, "n": 6}
# 단두대: 연결 성분 5개 (왼쪽부터 틀, 칼날, 떨어지는 칼날, 목판, 부서진 조각)
g = np.asarray(Image.open("art/exec/guillotine_source.png").convert("RGB")); bg = g[5, 5].astype(int)
mask = np.abs(g.astype(int) - bg).max(2) > 22; mask = ndimage.binary_closing(mask, iterations=6)
lab, n = ndimage.label(mask); objs = ndimage.find_objects(lab); sz = ndimage.sum(mask, lab, range(1, n + 1))
big = sorted([i for i in range(n) if sz[i] > 3000], key=lambda i: objs[i][1].start)
# 떨어지는 칼날의 흐림 선, 조각 구름이 여러 덩어리로 나뉠 수 있어 x 구간으로 다시 묶는다
spans = []
for i in big:
    x0, x1 = objs[i][1].start, objs[i][1].stop
    if spans and x0 < spans[-1][1] + 20: spans[-1][1] = max(spans[-1][1], x1)
    else: spans.append([x0, x1])
assert len(spans) == 5, spans
K = 0.15; parts, boxes = [], []
for x0, x1 in spans:
    sub = cutout(g[:, max(0, x0 - 6):x1 + 6], bg, 30); im = Image.fromarray(sub, "RGBA"); bb = im.getbbox(); im = im.crop(bb)
    parts.append(shrink(im, round(im.width * K), round(im.height * K)))
x = 0; sh = Image.new("RGBA", (sum(p.width + 1 for p in parts), max(p.height for p in parts)))
for p in parts: sh.paste(p, (x, 0)); boxes.append([x, 0, p.width, p.height]); x += p.width + 1
sh.save("assets/exec_guillo.png", optimize=True); out["guillo"] = boxes
print(json.dumps(out, separators=(",", ":")))
