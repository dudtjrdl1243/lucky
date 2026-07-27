# -*- coding: utf-8 -*-
"""오늘의 띠별·별자리 순위 계산 — myeongri.js / astro.js 와 같은 규칙.

스레드 글에 "오늘 1위는 OO띠" 라고 쓰려면 사이트가 보여주는 순위와
글에 쓰는 순위가 반드시 같아야 한다. 그래서 JS 엔진의 계산식을 그대로 옮겼다.
한쪽만 고치면 글과 사이트가 어긋나므로 바꿀 때는 양쪽 다 고칠 것.
"""
import math, time, calendar
from datetime import date

# ── 명리 (myeongri.js) ──────────────────────────────
STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
ANIMALS = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]
ELEM = ["목", "화", "토", "금", "수"]
STEM_ELEM = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
BRANCH_ELEM = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4]

GOD_SCORE = {
    "비겁": [2, -3, -5, 3, 7],
    "식상": [7, 12, 4, -2, 4],
    "재성": [9, 6, 16, 3, -3],
    "관성": [3, 4, 3, 14, -7],
    "인성": [8, -1, -2, 9, 9],
}
REL_SCORE = {"육합": 8, "삼합": 6, "동일": 3, "무관": 0, "충": -9}

DAY0 = date(1900, 1, 1).toordinal()  # 갑술일(index 10)


def _jround(x):
    """JS Math.round 는 .5를 올림한다. 파이썬 round()는 짝수로 붙어서 결과가 달라짐."""
    return int(math.floor(x + 0.5))


def day_pillar(y, m, d):
    i = (10 + (date(y, m, d).toordinal() - DAY0)) % 60
    return i % 10, i % 12  # (천간, 지지)


def ten_god(me, t):
    if t == me:
        return "비겁"
    if t == (me + 1) % 5:
        return "식상"
    if t == (me + 2) % 5:
        return "재성"
    if me == (t + 2) % 5:
        return "관성"
    return "인성"


def branch_rel(a, b):
    if a == b:
        return "동일"
    if abs(a - b) == 6:
        return "충"
    if (a + b) % 12 == 1:
        return "육합"
    if a % 4 == b % 4:
        return "삼합"
    return "무관"


def tti_total(branch_idx, day_stem_elem, day_branch):
    god = ten_god(BRANCH_ELEM[branch_idx], day_stem_elem)
    bonus = REL_SCORE[branch_rel(branch_idx, day_branch)]
    base = GOD_SCORE[god]
    s = [max(41, min(99, 62 + base[i] + bonus)) for i in range(5)]
    return _jround(sum(s) / 5.0)


# ── 점성술 (astro.js) ───────────────────────────────
# (이름, 시작월, 시작일, 원소 0불/1흙/2공기/3물, 특질)
SIGNS = [
    ("양자리", 3, 21, 0, 0), ("황소자리", 4, 20, 1, 1),
    ("쌍둥이자리", 5, 21, 2, 2), ("게자리", 6, 22, 3, 0),
    ("사자자리", 7, 23, 0, 1), ("처녀자리", 8, 23, 1, 2),
    ("천칭자리", 9, 24, 2, 0), ("전갈자리", 10, 23, 3, 1),
    ("사수자리", 11, 23, 0, 2), ("염소자리", 12, 22, 1, 0),
    ("물병자리", 1, 20, 2, 1), ("물고기자리", 2, 19, 3, 2),
]
ASP_SCORE = {
    0: [8, 6, 4, 6, 6], 1: [2, 2, 3, 2, 2], 2: [7, 9, 6, 6, 4],
    3: [-4, -3, -1, 3, -6], 4: [10, 9, 8, 7, 8], 5: [-2, -4, -3, -1, -3],
    6: [-3, -6, -1, 4, -5],
}
MOON_BONUS = [1, 2, 3, 4, 5, 3, 1, 0]
MOON_NAMES = ["신월(삭)", "초승달", "상현달", "차오르는 달",
              "보름달", "기우는 달", "하현달", "그믐달"]


def sun_sign(m, d):
    for i in range(12):
        sm, sd = SIGNS[i][1], SIGNS[i][2]
        nm, nd = SIGNS[(i + 1) % 12][1], SIGNS[(i + 1) % 12][2]
        after = (m > sm) or (m == sm and d >= sd)
        before = (m < nm) or (m == nm and d < nd)
        if (after and before) if sm < nm else (after or before):
            return i
    return 0


def moon_phase(epoch_sec):
    """0~7. 기준 2000-01-06 18:14 UTC 신월, 삭망월 29.530588853일"""
    ref = calendar.timegm((2000, 1, 6, 18, 14, 0, 0, 1, 0))
    days = (epoch_sec - ref) / 86400.0
    p = (days % 29.530588853) / 29.530588853
    return int(p * 8) % 8


def zodiac_total(i, sun, moon_idx):
    asp = min(abs(i - sun) % 12, 12 - abs(i - sun) % 12)
    elem, sun_elem = SIGNS[i][3], SIGNS[sun][3]
    if elem == sun_elem:
        eb = 4
    elif (elem, sun_elem) in ((0, 2), (2, 0), (1, 3), (3, 1)):
        eb = 2  # 불-공기, 흙-물은 상성
    else:
        eb = 0
    base = ASP_SCORE[asp]
    mb = MOON_BONUS[moon_idx]
    s = [max(41, min(99, 62 + base[k] + eb + mb)) for k in range(5)]
    return _jround(sum(s) / 5.0)


# ── 오늘의 사실 묶음 ────────────────────────────────
def today_facts(now=None):
    """스레드 글에 그대로 넣어 쓸 오늘의 계산 결과."""
    t = now if now is not None else time.time()
    kst = time.gmtime(t + 9 * 3600)
    y, m, d = kst.tm_year, kst.tm_mon, kst.tm_mday

    stem, branch = day_pillar(y, m, d)
    day_elem = STEM_ELEM[stem]
    tti = sorted(((tti_total(i, day_elem, branch), i) for i in range(12)),
                 key=lambda x: (-x[0], x[1]))

    sun = sun_sign(m, d)
    moon = moon_phase(t)
    zod = sorted(((zodiac_total(i, sun, moon), i) for i in range(12)),
                 key=lambda x: (-x[0], x[1]))

    return {
        "day_name": STEMS[stem] + BRANCHES[branch],
        "day_elem": ELEM[day_elem],
        "tti": [(ANIMALS[i], s) for s, i in tti],        # 1위부터
        "zodiac": [(SIGNS[i][0], s) for s, i in zod],    # 1위부터
        "sun_sign": SIGNS[sun][0],
        "moon": MOON_NAMES[moon],
    }


if __name__ == "__main__":
    f = today_facts()
    print("일진:", f["day_name"], "/", f["day_elem"], "/ 달:", f["moon"],
          "/ 태양궁:", f["sun_sign"])
    print("띠  :", " ".join("{}.{}({})".format(i + 1, n, s)
                            for i, (n, s) in enumerate(f["tti"])))
    print("별자리:", " ".join("{}.{}({})".format(i + 1, n, s)
                              for i, (n, s) in enumerate(f["zodiac"])))
