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
# 추가 자세 6개(poses2_source.jpg): 낙하, 착지, 피격, 어퍼컷, 대기2, 웅크림. 투구·장화를 뺀 나머지 조각을 모두 몸통으로 합친다
b = np.asarray(Image.open("poses2_source.jpg").convert("RGB")).astype(int)
bgb = np.median(b[:20, :20].reshape(-1, 3), axis=0); mb = np.abs(b - bgb).max(axis=2) > 34
mb = ndimage.binary_opening(mb, iterations=1); labb, _ = ndimage.label(mb)
cb = [(i + 1, s2, int((labb[s2] == i + 1).sum())) for i, s2 in enumerate(ndimage.find_objects(labb))]
cb = [c for c in cb if c[2] > 1200]
WB = b.shape[1]; EDGES = [0, 400, 720, 1090, 1380, 1665, 2000]           # 자세 칸 경계 (시안 너비 2000 기준)
cx = lambda c: (c[1][1].start + c[1][1].stop) / 2 * 2000 / WB
K2 = K * 2752 / WB                                      # 두 번째 그림은 해상도가 달라 같은 게임 크기가 되게 맞춘다
# 낙하·대기2는 투구가 망토/불꽃에 붙어 있어 떼어낼 수 없어 뺀다. 착지·웅크림은 장화가 몸통에 붙어 있어 장화째 쓴다(noBoots)
for k, name in [(1, "land"), (2, "hit"), (3, "upper"), (5, "crouch")]:
    mine = [c for c in cb if EDGES[k] <= cx(c) < EDGES[k + 1]]
    helm = min(mine, key=lambda c: c[1][0].start); mine.remove(helm)
    big = max(mine, key=lambda c: c[2]); low = max(c[1][0].stop for c in mine)
    boots = [] if big[1][0].stop >= low - 10 else sorted([c for c in mine if c is not big], key=lambda c: -c[1][0].stop)[:2]
    rest = [c for c in mine if c not in boots]
    y0 = min(c[1][0].start for c in rest); y1 = max(c[1][0].stop for c in rest); x0 = min(c[1][1].start for c in rest); x1 = max(c[1][1].stop for c in rest)
    s2 = (slice(y0, y1), slice(x0, x1)); msk = np.isin(labb[s2], [c[0] for c in rest]) & mb[s2]
    wm = (b[s2].min(axis=2) > 225) & msk; ys, xs = np.nonzero(wm)
    p = Image.fromarray(np.dstack([b[s2].astype(np.uint8), (msk * 255).astype(np.uint8)]), "RGBA").resize((max(1, round((x1 - x0) * K2)), max(1, round((y1 - y0) * K2))), Image.BOX)
    px = np.asarray(p).copy(); al = px[..., 3] > 100; px[..., 3] = np.where(al, 255, 0)
    out = Image.new("RGBA", (p.width + 2, p.height + 2)); out.paste(Image.fromarray(px, "RGBA"), (1, 1))
    o2 = np.asarray(out).copy(); al2 = o2[..., 3] > 0; e = np.zeros_like(al2); e[1:] |= al2[:-1]; e[:-1] |= al2[1:]; e[:, 1:] |= al2[:, :-1]; e[:, :-1] |= al2[:, 1:]; e &= ~al2; o2[e] = (10, 26, 34, 255)
    parts["body_" + name] = (Image.fromarray(o2, "RGBA"), {"eye": [round(float(xs.mean()) * K2) + 1, round(float(ys.mean()) * K2) + 1], **({"noBoots": 1} if not boots else {})})
W = sum(p.width + 2 for p, _ in parts.values()); H = max(p.height for p, _ in parts.values()); at = Image.new("RGBA", (W, H)); x = 0; meta = {}
for k, (p, extra) in parts.items(): at.paste(p, (x, 0)); meta[k] = {"r": [x, 0, p.width, p.height], **extra}; x += p.width + 2
at.save("../../assets/void2.png")
print("const VOID2 = " + json.dumps(meta, separators=(",", ":")) + ";")
