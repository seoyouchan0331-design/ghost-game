# 따로 자른 시트(hero_cut.py <계보>tmp ...)의 앞 프레임들을 본 시트 아래에 붙이고 HERO.<계보>.stages[단계][이름]으로 넣는다
# 실행: python3 art/heroframes/hero_addmove.py <계보> <단계> <이름> <hero_cut 출력 json> <첫:끝> <fps>
import sys, json
from PIL import Image
LINE, ST, NM, JS, RG, FPS = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6])
a0, a1 = map(int, RG.split(":"))
t = open(JS).read(); T, _ = json.JSONDecoder().raw_decode(t[t.index('{"stages"'):])
F = T["stages"][ST]["attack"]["f"][a0:a1 + 1]; ts = Image.open(f"assets/hero_{LINE}tmp.png").convert("RGBA")
s = open("index.html").read(); k = s.index(f"{LINE}: ", s.index("const HERO = {")) + len(LINE) + 2
H, end = json.JSONDecoder().raw_decode(s[k:]); sh = Image.open(f"assets/hero_{LINE}.png").convert("RGBA")
crops = [ts.crop((T["boxes"][c][0], T["boxes"][c][1], T["boxes"][c][0] + T["boxes"][c][2], T["boxes"][c][1] + T["boxes"][c][3])) for c, _, _ in F]
W = sh.width; x = 0; y = sh.height + 1; rows = []; rowh = 0; pos = []
for c in crops:
    if x + c.width > W: x = 0; y += rowh + 1; rowh = 0
    pos.append((x, y)); x += c.width + 1; rowh = max(rowh, c.height)
new = Image.new("RGBA", (W, y + rowh)); new.paste(sh, (0, 0)); fr = []
for c, (px, py), (_, ox, oy) in zip(crops, pos, F):
    new.paste(c, (px, py)); H["boxes"].append([px, py, c.width, c.height]); fr.append([len(H["boxes"]) - 1, ox, oy])
H["stages"][ST][NM] = {"fps": FPS, "f": fr}
new.save(f"assets/hero_{LINE}.png", optimize=True); open("index.html", "w").write(s[:k] + json.dumps(H, separators=(",", ":")) + s[k + end:]); print(NM, len(fr), new.size)
