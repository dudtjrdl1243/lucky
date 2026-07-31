# -*- coding: utf-8 -*-
"""로또 통계 + 주간 추천번호 생성/채점
1) 과거 회차를 모아 lotto-history.json 에 누적 (최초 1회만 대량 수집, 이후 증분)
2) 지난주 추천번호를 새 당첨번호와 대조해 채점
3) 다음 회차 추천번호 5게임 생성
   - 실제 당첨번호의 통계 분포(번호별 출현 빈도, 미출현 기간, 홀짝/고저 비율, 합계 구간)를 따름
   - 회차 번호를 시드로 쓰므로 같은 회차면 항상 같은 번호가 나온다(사후 조작 불가)
※ 통계로 뽑아도 당첨 확률은 올라가지 않는다. 오락용 기능임.
"""
import json, os, random, sys, urllib.request
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(BASE, "lotto-history.json")
OUT = os.path.join(BASE, "lotto-picks.js")
MIRROR = "https://smok95.github.io/lotto/results/"
RECENT_WINDOW = 50  # 최근 N회 기준으로 핫/콜드 판정


def fetch(name):
    req = urllib.request.Request(MIRROR + name, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def load_history():
    if os.path.exists(HIST):
        try:
            return json.load(open(HIST, encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_history(h):
    json.dump(h, open(HIST, "w", encoding="utf-8"), ensure_ascii=False, sort_keys=True)


def sync_history(latest_no, hist, max_new=400):
    """없는 회차를 채운다. 최초 실행 시 과거를 훑고, 이후에는 새 회차만 추가."""
    added = 0
    for rnd in range(latest_no, 0, -1):
        if added >= max_new:
            break
        if str(rnd) in hist:
            continue
        d = fetch(str(rnd) + ".json")
        if not d:
            continue
        hist[str(rnd)] = {"numbers": d["numbers"], "bonus": d["bonus_no"], "date": d["date"][:10]}
        added += 1
    return added


# ── 통계 계산 ──────────────────────────────────────────
def build_stats(hist):
    rounds = sorted((int(k) for k in hist), reverse=True)
    freq_all = Counter()
    freq_recent = Counter()
    last_seen = {}
    for i, rnd in enumerate(rounds):
        for n in hist[str(rnd)]["numbers"]:
            freq_all[n] += 1
            if i < RECENT_WINDOW:
                freq_recent[n] += 1
            if n not in last_seen:
                last_seen[n] = i  # 몇 회차 전에 마지막으로 나왔는지
    total = len(rounds)
    sums = [sum(hist[str(r)]["numbers"]) for r in rounds]
    odd_counts = [sum(1 for n in hist[str(r)]["numbers"] if n % 2) for r in rounds]
    return {
        "total": total,
        "freqAll": freq_all,
        "freqRecent": freq_recent,
        "lastSeen": last_seen,
        "sumMin": int(sorted(sums)[int(len(sums) * 0.15)]),
        "sumMax": int(sorted(sums)[int(len(sums) * 0.85)]),
        "oddMode": Counter(odd_counts).most_common(1)[0][0],
    }


def ac_value(nums):
    """AC값(산술복잡도) = 두 수 차이의 가짓수 - 5. 번호가 고르게 흩어질수록 커진다(최대 10)."""
    diffs = {abs(a - b) for i, a in enumerate(nums) for b in nums[i + 1:]}
    return len(diffs) - (len(nums) - 1)


def build_patterns(hist):
    """당첨번호에 실제로 나타나는 패턴 지표. 전부 과거 회차에서 계산한 사실이다."""
    rounds = sorted((int(k) for k in hist), reverse=True)
    carry, consec, tails, acs, lows = [], 0, [], [], []
    zones = [0] * 5
    for i, r in enumerate(rounds):
        ns = sorted(hist[str(r)]["numbers"])
        tails.append(sum(n % 10 for n in ns))
        acs.append(ac_value(ns))
        lows.append(sum(1 for n in ns if n <= 22))
        if any(ns[k + 1] - ns[k] == 1 for k in range(len(ns) - 1)):
            consec += 1
        for n in ns:
            zones[min((n - 1) // 10, 4)] += 1
        if i + 1 < len(rounds):  # 직전 회차와 겹치는 번호 = 이월수
            carry.append(len(set(ns) & set(hist[str(rounds[i + 1])]["numbers"])))
    n = len(rounds)
    pct = lambda v, p: sorted(v)[min(len(v) - 1, int(len(v) * p))]
    return {
        "carryAvg": round(sum(carry) / len(carry), 2) if carry else 0,
        "carryAnyPct": round(sum(1 for c in carry if c) / len(carry) * 100) if carry else 0,
        "consecPct": round(consec / n * 100),
        "tailRange": [pct(tails, 0.15), pct(tails, 0.85)],
        "acRange": [pct(acs, 0.15), pct(acs, 0.85)],
        "acMode": Counter(acs).most_common(1)[0][0],
        "lowMode": Counter(lows).most_common(1)[0][0],
        "zoneAvg": [round(z / n, 2) for z in zones],
    }


def build_exclude(hist, window=7, min_hit=2):
    """제외수 — 최근 window회에서 min_hit회 이상 나온 '단기 과출현' 번호.
    이월수 평균이 1개 남짓인 걸 감안한 것으로, 실제로 조합에서 뺀다(표시만 하는 게 아니다).
    window=7이면 대략 10개 안팎이 걸린다. 더 넓히면 후보 풀이 너무 줄어든다."""
    rounds = sorted((int(k) for k in hist), reverse=True)[:window]
    c = Counter()
    for r in rounds:
        for n in hist[str(r)]["numbers"]:
            c[n] += 1
    return sorted(n for n, v in c.items() if v >= min_hit)


def pick_games(stats, seed, exclude=(), games=5):
    """전략을 나눠 5게임 생성 — 각 게임의 근거가 서로 다르다."""
    rng = random.Random(seed)
    freq_r, last_seen = stats["freqRecent"], stats["lastSeen"]
    pool = list(range(1, 46))

    hot = sorted(pool, key=lambda n: (-freq_r.get(n, 0), n))[:15]          # 최근 자주 나온 번호
    cold = sorted(pool, key=lambda n: (-last_seen.get(n, 999), n))[:15]    # 오래 안 나온 번호
    mid = sorted(pool, key=lambda n: abs(freq_r.get(n, 0) - (6 * RECENT_WINDOW / 45)))[:20]

    # 제외수를 실제로 뺀다. 단 '핫넘버 중심'은 과출현 번호를 일부러 쓰는 전략이라 그대로 둔다.
    ex = set(exclude)
    cut = lambda lst: [n for n in lst if n not in ex] or lst
    cold_x, mid_x, pool_x = cut(cold), cut(mid), cut(pool)

    strategies = [
        ("핫넘버 중심", lambda: rng.sample(hot, 4) + rng.sample([n for n in pool if n not in hot], 2)),
        ("콜드넘버 중심", lambda: rng.sample(cold_x, 4) + rng.sample([n for n in pool_x if n not in cold_x], 2)),
        ("핫·콜드 반반", lambda: rng.sample(hot, 3) + rng.sample(cold_x, 3)),
        ("출현 평균대", lambda: rng.sample(mid_x, 6)),
        ("전 구간 균형", lambda: [rng.choice([n for n in pool_x if lo <= n <= hi] or [n for n in pool if lo <= n <= hi])
                                 for lo, hi in [(1, 9), (10, 18), (19, 27), (28, 36), (37, 45), (1, 45)]]),
    ]

    out = []
    for label, gen in strategies[:games]:
        for _ in range(300):  # 합계·홀짝 조건을 만족할 때까지 재시도
            nums = sorted(set(gen()))
            if len(nums) != 6:
                continue
            s = sum(nums)
            odd = sum(1 for n in nums if n % 2)
            if stats["sumMin"] <= s <= stats["sumMax"] and abs(odd - stats["oddMode"]) <= 1:
                break
        out.append({"label": label, "numbers": sorted(nums), "sum": sum(nums),
                    "odd": sum(1 for n in nums if n % 2)})
    return out


def main():
    latest = fetch("latest.json")
    if not latest:
        print("최신 회차 조회 실패 — 기존 데이터 유지")
        return
    latest_no = latest["draw_no"]

    hist = load_history()
    added = sync_history(latest_no, hist)
    save_history(hist)
    print("history: 총 {}회차 (이번에 {}회 추가)".format(len(hist), added))

    if len(hist) < 30:
        print("통계에 쓸 회차가 부족합니다. 다음 실행에서 계속 수집합니다.")
        return

    stats = build_stats(hist)

    # 이전 실행에서 저장해둔 추천번호 불러와 채점
    prev = {}
    if os.path.exists(OUT):
        try:
            src = open(OUT, encoding="utf-8").read()
            import re
            m = re.search(r"const LOTTO_PICKS = (\{.*?\});", src, re.S)
            if m:
                prev = json.loads(m.group(1))
        except Exception:
            prev = {}

    history_log = prev.get("results", [])
    target_prev = prev.get("targetRound")
    if target_prev == latest_no and prev.get("games"):
        win = set(latest["numbers"])
        bonus = latest["bonus_no"]
        scored = []
        for g in prev["games"]:
            hit = len(set(g["numbers"]) & win)
            has_bonus = bonus in set(g["numbers"])
            rank = (1 if hit == 6 else 2 if (hit == 5 and has_bonus) else 3 if hit == 5
                    else 4 if hit == 4 else 5 if hit == 3 else 0)
            scored.append({"label": g["label"], "numbers": g["numbers"], "hit": hit, "rank": rank})
        history_log.insert(0, {"round": latest_no, "date": latest["date"][:10],
                               "win": latest["numbers"], "bonus": bonus, "games": scored})
        history_log = history_log[:20]
        print("{}회 채점 완료: 최고 {}개 적중".format(latest_no, max(s["hit"] for s in scored)))

    target = latest_no + 1
    patterns = build_patterns(hist)
    exclude = build_exclude(hist)
    games = pick_games(stats, seed=target, exclude=exclude)

    data = {
        "targetRound": target,
        "basedOn": {"rounds": stats["total"], "recentWindow": RECENT_WINDOW,
                    "sumRange": [stats["sumMin"], stats["sumMax"]], "oddMode": stats["oddMode"]},
        "exclude": exclude,
        "patterns": patterns,
        "games": games,
        "results": history_log,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("const LOTTO_PICKS = " + json.dumps(data, ensure_ascii=False) + ";\n")
    print("lotto-picks.js 생성: {}회차 추천 {}게임".format(target, len(games)))


if __name__ == "__main__":
    main()
