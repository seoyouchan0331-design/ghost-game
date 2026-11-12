# 렌더 결과(id + lit)를 도트 스프라이트 시트로 바꾼다: 재질별 색 단계(팔레트 제한) + 1픽셀 테두리
# 실행: python3 void_pixelate.py <렌더폴더> <출력폴더>
import sys
from PIL import Image
SRC, OUT = sys.argv[1], sys.argv[2]
ANIMS = [("idle", 4), ("run", 6), ("punch", 4), ("jump", 2), ("dash", 1), ("slam", 2)]
h = lambda s: tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
# 재질별 색 단계 (어두움 → 밝음), 참고 그림의 색감에 맞춤
RAMPS = {
    "iron": ["#2a2531", "#433c4b", "#62596b", "#8a8094", "#b0a8ba"],
    "back": ["#1c1822", "#2a2531", "#3a3442", "#544c5e"],
    "rust": ["#6e3418", "#9a4f28", "#c9783a", "#e8a860"],
    "gold": ["#8a6a2a", "#d1aa4e", "#ffe9a0"],
    "cape": ["#143c40", "#1d5459", "#2f8188", "#44a3a6"],
    "flame": ["#2f8fb8", "#63c8ea", "#63c8ea", "#b5efff"],
    "core": ["#b5efff", "#ffffff"],
    "eye": ["#ffffff"],
    "dark": ["#0c0a10"],
}
IDS = {"iron": (255, 0, 0), "back": (188, 0, 0), "rust": (255, 255, 0), "gold": (255, 188, 0), "cape": (0, 255, 0), "flame": (0, 0, 255),
       "core": (0, 255, 255), "eye": (255, 255, 255), "dark": (255, 0, 255)}
LINE = (23, 19, 28, 255)
def mat_of(c): return min(IDS, key=lambda k: sum((a - b) ** 2 for a, b in zip(IDS[k], c)))
def convert(name, f, var):
    idi = Image.open(f"{SRC}/{name}_{f}_{var}_id.png").convert("RGBA"); lit = Image.open(f"{SRC}/{name}_{f}_{var}_lit.png").convert("RGBA")
    W, H = idi.size; out = Image.new("RGBA", (W, H)); ip, lp, op = idi.load(), lit.load(), out.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = ip[x, y]
            if a < 128: continue
            m = mat_of((r, g, b)); ramp = RAMPS[m]; lum = sum(lp[x, y][:3]) / 765
            k = min(len(ramp) - 1, int(max(0, (lum - 0.26) / 0.58) * len(ramp)))
            op[x, y] = (*h(ramp[k]), 255)
    src = out.copy(); sp = src.load()                       # 바깥 테두리
    for y in range(H):
        for x in range(W):
            if sp[x, y][3]: continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and sp[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): op[x, y] = LINE
    return out
cols = max(c for _, c in ANIMS)
for var in ("full", "body"):
    frames = {n: [convert(n, f, var) for f in range(c)] for n, c in ANIMS}
    S = frames["idle"][0].size[0]
    sheet = Image.new("RGBA", (S * cols, S * len(ANIMS)))
    for r, (n, c) in enumerate(ANIMS):
        for f in range(c): sheet.paste(frames[n][f], (f * S, r * S))
    sheet.save(f"{OUT}/void_{var}.png")
    Z = 5; prev = Image.new("RGBA", (sheet.width * Z, sheet.height * Z), (36, 32, 48, 255))   # 확대 미리보기
    prev.alpha_composite(sheet.resize(prev.size, Image.NEAREST)); prev.save(f"{OUT}/void_{var}_preview.png")
print("sheet", sheet.size)
