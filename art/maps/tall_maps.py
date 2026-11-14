# 스컬식 세로 전투 방 만들기: 층 간격 4칸(2단 점프 약 5.5칸), 바닥 + 여러 층의 땅덩이(#)·발판(=), 층마다 적 자리
# python3 art/maps/tall_maps.py  → 지도 문자열과 도달 검사 결과 출력 (index.html LAYOUTS 에 붙여 넣음)
import json, sys
W, H = 46, 26
def new(): return [["."] * W for _ in range(H)]
def blk(g, r0, r1, c0, c1):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1): g[r][c] = "#"
def plat(g, r, c0, c1):
    for c in range(c0, c1 + 1): g[r][c] = "="
def put(g, ch, r, c): g[r][c] = ch                       # r = 서는 줄 (바로 아래가 # 또는 =)
def base(g): blk(g, H - 1, H - 1, 0, W - 1)
F = H - 2                                                 # 바닥에 서는 줄
MAPS = []
# A: 양쪽 둔덕 + 가운데로 올라가는 계단식 층
g = new(); base(g)
blk(g, 21, 24, 7, 12); blk(g, 21, 24, 29, 34); plat(g, 21, 17, 24)
plat(g, 17, 5, 12); blk(g, 17, 18, 26, 34)
plat(g, 13, 13, 21); plat(g, 13, 36, 43)
blk(g, 9, 10, 2, 10); plat(g, 9, 23, 31)
plat(g, 5, 11, 18); plat(g, 5, 33, 41)
for c in (15, 25, 38): put(g, "E", F, c)
put(g, "E", 20, 9); put(g, "E", 20, 31); put(g, "T", 20, 20); put(g, "E", 16, 30); put(g, "T", 16, 8)
put(g, "T", 12, 17); put(g, "E", 12, 40); put(g, "E", 8, 6); put(g, "T", 8, 27); put(g, "T", 4, 37)
MAPS.append(g)
# B: 가운데 큰 바위 기둥, 양옆으로 지그재그 발판
g = new(); base(g)
blk(g, 13, 24, 19, 26)
plat(g, 21, 3, 10); plat(g, 21, 35, 42)
plat(g, 17, 11, 17); plat(g, 17, 28, 34)
plat(g, 13, 2, 9); plat(g, 13, 36, 43)
blk(g, 9, 10, 10, 17); blk(g, 9, 10, 28, 35); plat(g, 9, 20, 25)
plat(g, 5, 3, 10); plat(g, 5, 18, 27); plat(g, 5, 35, 42)
for c in (6, 13, 32, 40): put(g, "E", F, c)
put(g, "E", 12, 22); put(g, "T", 20, 6); put(g, "T", 20, 39); put(g, "T", 16, 14); put(g, "T", 16, 31)
put(g, "E", 12, 5); put(g, "E", 12, 40); put(g, "E", 8, 13); put(g, "E", 8, 31); put(g, "T", 4, 22)
MAPS.append(g)
# C: 왼쪽에서 오른쪽 위로 크게 올라가는 비탈 (땅덩이 계단)
g = new(); base(g)
blk(g, 21, 24, 12, 19); blk(g, 17, 24, 22, 28); blk(g, 13, 24, 31, 37); blk(g, 9, 12, 40, 45)
plat(g, 20, 2, 9); plat(g, 16, 6, 13); plat(g, 12, 14, 22); plat(g, 8, 24, 32); plat(g, 4, 34, 43)
plat(g, 9, 2, 8)
for c in (4, 8): put(g, "E", F, c)
put(g, "E", 20, 15); put(g, "E", 16, 25); put(g, "E", 12, 34); put(g, "E", 8, 43)
put(g, "T", 19, 5); put(g, "T", 15, 9); put(g, "T", 11, 18); put(g, "T", 7, 28); put(g, "T", 3, 38); put(g, "E", 8, 5)
MAPS.append(g)
# D: 바닥에 구덩이 둘 + 위로 이어지는 층 (떨어지면 아래층)
g = new(); base(g)
for c in range(14, 18): g[H - 1][c] = "."
for c in range(29, 33): g[H - 1][c] = "."
plat(g, 21, 13, 19); plat(g, 21, 28, 34)
blk(g, 17, 18, 0, 7); blk(g, 17, 18, 38, 45); plat(g, 17, 18, 27)
plat(g, 13, 8, 15); plat(g, 13, 30, 37)
blk(g, 9, 10, 18, 27); plat(g, 9, 2, 9); plat(g, 9, 36, 43)
plat(g, 5, 10, 17); plat(g, 5, 28, 35)
for c in (5, 10, 23, 38, 42): put(g, "E", F, c)
put(g, "T", 20, 16); put(g, "T", 20, 31); put(g, "E", 16, 3); put(g, "E", 16, 42); put(g, "T", 16, 22)
put(g, "E", 8, 22); put(g, "T", 12, 11); put(g, "T", 12, 34); put(g, "T", 4, 13); put(g, "T", 4, 31)
MAPS.append(g)
# E: 오른쪽 위 높은 성벽 + 왼쪽 나무 발판 사다리
g = new(); base(g)
blk(g, 15, 17, 34, 45); blk(g, 11, 14, 38, 45)
plat(g, 21, 6, 13); plat(g, 21, 24, 31)
plat(g, 17, 1, 7); plat(g, 17, 15, 23)
plat(g, 13, 6, 13); plat(g, 13, 24, 31)
plat(g, 9, 14, 22); blk(g, 9, 10, 0, 5)
plat(g, 5, 4, 11); plat(g, 5, 24, 33); plat(g, 7, 34, 37)
for c in (4, 17, 22, 29): put(g, "E", F, c)
put(g, "E", 14, 36); put(g, "E", 10, 41); put(g, "T", 20, 9); put(g, "T", 20, 27); put(g, "T", 16, 19)
put(g, "E", 8, 2); put(g, "T", 12, 9); put(g, "T", 12, 27); put(g, "T", 8, 18); put(g, "T", 4, 28)
MAPS.append(g)

def check(g):
    solid = lambda r, c: 0 <= r < H and 0 <= c < W and g[r][c] in "#="
    stand = lambda r, c: 0 <= c < W and 0 <= r < H - 1 and g[r][c] not in "#=" and solid(r + 1, c)
    bad = [(r, c) for r in range(H) for c in range(W) if g[r][c] in "ET" and not solid(r + 1, c)]
    bad += [("corner", r, c) for r in range(F - 3, F + 1) for c in list(range(0, 4)) + list(range(38, W)) if g[r][c] == "#"]   # 시작 자리(왼쪽 아래)와 문 자리(오른쪽 아래)는 비워 둔다
    seen, todo = set(), [(F, 2)]
    while todo:
        r, c = todo.pop()
        if (r, c) in seen: continue
        seen.add((r, c))
        for dc in range(-6, 7):
            for dr in range(-5, H):
                r2, c2 = r + dr, c + dc
                if not stand(r2, c2) or (r2, c2) in seen: continue
                if dr < 0:   # 위로 점프: 머리 위가 #로 막혀 있으면 안 됨
                    if any(g[rr][c] == "#" for rr in range(r2, r)) and any(g[rr][c2] == "#" for rr in range(r2 + 1, r + 1)): continue
                todo.append((r2, c2))
    spots = [(r, c) for r in range(H) for c in range(W) if g[r][c] in "ET"]
    unreach = [s for s in spots if s not in seen]
    return bad, unreach, len(spots)
ok = True
for i, g in enumerate(MAPS):
    bad, un, n = check(g); print(f"map {i}: spots {n}, floating {bad}, unreachable {un}", file=sys.stderr); ok &= not bad and not un
print(json.dumps(["".join(r) for r in g] for g in MAPS) if False else "\n".join("  MAP(" + ",\n      ".join(json.dumps("".join(r)) for r in g) + ")," for g in MAPS))
sys.exit(0 if ok else 1)
