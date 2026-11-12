# 보이드 새 디자인 시안(흩어진 갑옷) → 게임용 조각. assets/void2.png + 좌표 JSON 출력.
# 시안은 5자세(대기, 달리기, 점프, 주먹, 대시). 투구·장화는 늘 따로, 장갑은 대개 몸통에 붙어 있다.
import json, numpy as np
from PIL import Image
from scipy import ndimage
K = 0.07                                                # 시안 → 게임 크기 (몸통 약 30px)
a = np.asarray(Image.open("concept_source.png").convert("RGB")).astype(int)
bg = np.median(a[:20, :20].reshape(-1, 3), axis=0); m = np.abs(a - bg).max(axis=2) > 28
lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=2)); objs = ndimage.find_objects(lab)
comps = [(i + 1, s, int((lab[s] == i + 1).sum())) for i, s in enumerate(objs)]
COLS = [(0, 480, "idle"), (480, 1100, "run"), (1100, 1500, "jump"), (1500, 2080, "punch"), (2080, 2752, "dash")]
def piece(i, s):
    msk = (lab[s] == i) & m[s]; p = Image.fromarray(np.dstack([a[s].astype(np.uint8), (msk * 255).astype(np.uint8)]), "RGBA")
    p = p.resize((max(1, round(p.width * K)), max(1, round(p.height * K))), Image.BOX)
    px = np.asarray(p).copy(); al = px[..., 3] > 100; px[..., 3] = np.where(al, 255, 0)
    out = Image.new("RGBA", (p.width + 2, p.height + 2)); out.paste(Image.fromarray(px, "RGBA"), (1, 1))
    o2 = np.asarray(out).copy(); al2 = o2[..., 3] > 0; e = np.zeros_like(al2); e[1:] |= al2[:-1]; e[:-1] |= al2[1:]; e[:, 1:] |= al2[:, :-1]; e[:, :-1] |= al2[:, 1:]; e &= ~al2; o2[e] = (10, 26, 34, 255)   # 바깥 1px 테두리만
    return Image.fromarray(o2, "RGBA")
parts = {}
for x0, x1, name in COLS:
    cs = [c for c in comps if x0 <= (c[1][1].start + c[1][1].stop) / 2 < x1 and c[2] > 4000]
    body = max(cs, key=lambda c: c[2]); rest = [c for c in cs if c is not body]
    helm = min(rest, key=lambda c: c[1][0].start); rest.remove(helm)
    boots = sorted(sorted(rest, key=lambda c: -c[1][0].stop)[:2], key=lambda c: c[1][1].start); rest = [c for c in rest if c not in boots]
    i, s, _ = body; sub = a[s]; wm = (sub.min(axis=2) > 225) & (lab[s] == i)   # 흰 눈 = 머리 기준점
    ys, xs = np.nonzero(wm); eye = [round(float(xs.mean()) * K) + 1, round(float(ys.mean()) * K) + 1]
    parts["body_" + name] = (piece(i, s), {"eye": eye})
    if name == "idle":
        parts["helmet"] = (piece(helm[0], helm[1]), {}); parts["boot_b"] = (piece(boots[0][0], boots[0][1]), {}); parts["boot_f"] = (piece(boots[1][0], boots[1][1]), {})
    if rest and name in ("punch", "run"):
        g = max(rest, key=lambda c: c[2]); parts["glove_" + name] = (piece(g[0], g[1]), {})
W = sum(p.width + 2 for p, _ in parts.values()); H = max(p.height for p, _ in parts.values()); at = Image.new("RGBA", (W, H)); x = 0; meta = {}
for k, (p, extra) in parts.items(): at.paste(p, (x, 0)); meta[k] = {"r": [x, 0, p.width, p.height], **extra}; x += p.width + 2
at.save("../../assets/void2.png")
print("const VOID2 = " + json.dumps(meta, separators=(",", ":")) + ";")
