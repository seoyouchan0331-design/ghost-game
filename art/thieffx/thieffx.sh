# 괴도 이펙트: pixelfx(저장소 Pixel/pixelfx)로 렌더 → art/hunterfx/hunterfx_pack.py로 assets/gfx_t*.png
# 실행: bash art/thieffx/thieffx.sh <pixelfx 폴더> <임시 폴더>   (ghost-game 폴더에서)
PF=$1; O=$2
G7='["#3a1e08","#7a4a12","#c07a1a","#ffb02a","#ffd24a","#fff0a0","#ffffff"]'
G8='["#2a1404","#5a3208","#8a5410","#c07a1a","#ffb02a","#ffd24a","#fff0a0","#ffffff"]'
R() { (cd "$PF" && node tools/render.mjs "$1" --sheet --bg none --no-actor --opts "$2" --out "$O/$3"); }
R impacts/hit-spark "{\"palette\":$G7}" hit
R impacts/crit-hit "{\"palette\":$G8}" crit
R melee/dagger-flurry "{\"palette\":$G7}" fl
R pickups/collect-burst "{\"palette\":$G8}" cb
R spawn/poof '{"palette":["#1a1626","#34304a","#555068","#77728a","#9b97ac","#c4c0d2"]}' pd
python3 art/hunterfx/hunterfx_pack.py thit=$O/hit:impacts/hit-spark tcrit=$O/crit:impacts/crit-hit tflurry=$O/fl:melee/dagger-flurry tboom=$O/cb:pickups/collect-burst tpoof=$O/pd:spawn/poof
R melee/sword-slash "{\"palette\":$G7}" sl
(cd "$PF" && node tools/render.mjs explosions/smoke-bomb --sheet --bg none --no-actor --out "$O/sm")
python3 art/hunterfx/hunterfx_pack.py tslash=$O/sl:melee/sword-slash tcloud=$O/sm:explosions/smoke-bomb@84
