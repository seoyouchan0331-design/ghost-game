#!/usr/bin/env bash
# 사용자가 main 브랜치에 새로 올린 파일을 꺼낸다.
# 기준: 진행 현황.md 의 "마지막으로 처리한 main 커밋" 줄. 그 뒤에 추가된 파일만 art/inbox/<커밋>/ 에 풀고, zip은 압축을 푼다.
# 사용: bash tools/new_uploads.sh        (목록과 꺼낸 위치를 출력)
set -euo pipefail
cd "$(dirname "$0")/.."
git fetch -q origin main
base=$(grep -o '마지막으로 처리한 main 커밋: `[0-9a-f]*`' "진행 현황.md" | grep -o '[0-9a-f]\{7,\}')
head=$(git rev-parse --short origin/main)
echo "기준 $base → 최신 $head"
[ "$base" = "$head" ] && { echo "새 업로드 없음"; exit 0; }
out="art/inbox/$head"; mkdir -p "$out"
git diff --name-only --diff-filter=AM "$base" origin/main | while IFS= read -r f; do
  dst="$out/$(basename "$f")"; git show "origin/main:$f" > "$dst"
  case "$f" in *.zip) python3 -I -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$dst" "$out" && rm "$dst";; esac
done
python3 -c "
import os,sys
from PIL import Image
d=sys.argv[1]
for n in sorted(os.listdir(d)):
    p=os.path.join(d,n)
    try: print(Image.open(p).size, n)
    except Exception: print('(그림 아님)', n)
" "$out"
echo "꺼낸 곳: $out   (처리 후 진행 현황.md 의 기준 커밋을 $head 로 바꿀 것)"
