# 영상 프레임 바탕 지우기: 테두리와 이어진 바탕만 지운다 (몸 안쪽의 어두운 색·외곽선은 남김). 몸 안에 갇힌 큰 바탕 구멍(다리 사이 등)은 지운다
import numpy as np
from scipy import ndimage
def key(a, thr=20, hole=1500):
    bg = np.median(np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)]), axis=0)
    back = np.abs(a - bg).max(axis=2) <= thr
    lab, n = ndimage.label(back); sizes = ndimage.sum(back, lab, range(1, n + 1))
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    drop = [i + 1 for i in range(n) if (i + 1) in edge or sizes[i] > hole]
    return ~np.isin(lab, drop)
