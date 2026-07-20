# -*- coding: utf-8 -*-
"""로또 당첨번호 -> lotto-data.js 생성 (최신 회차 + 최근 5회)
데이터 소스: smok95/lotto GitHub Pages 미러 (동행복권 직접 API는 봇 차단됨)
실패 시 기존 데이터 유지하고 정상 종료.
"""
import json, os, sys, urllib.request

BASE = "https://smok95.github.io/lotto/results/"

def fetch(name):
    req = urllib.request.Request(BASE + name, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print("fetch error:", name, e)
        return None

latest = fetch("latest.json")
if not latest:
    print("최신 회차 조회 실패, 기존 데이터 유지")
    sys.exit(0)

rounds = [latest]
for rnd in range(latest["draw_no"] - 1, latest["draw_no"] - 5, -1):
    d = fetch(str(rnd) + ".json")
    if d:
        rounds.append(d)

def pack(d):
    div1 = (d.get("divisions") or [{}])[0]
    return {
        "round": d["draw_no"],
        "date": d["date"][:10],
        "numbers": d["numbers"],
        "bonus": d["bonus_no"],
        "firstPrize": div1.get("prize", 0),
        "firstWinners": div1.get("winners", 0),
    }

out = "const LOTTO_ROUNDS = " + json.dumps([pack(d) for d in rounds], ensure_ascii=False) + ";\n"
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(base, "lotto-data.js"), "w", encoding="utf-8") as f:
    f.write(out)

# lotto-result.html의 정적 SEO 텍스트(제목/설명 속 회차 번호)도 최신 회차로 교체
import re
page_path = os.path.join(base, "lotto-result.html")
if os.path.exists(page_path):
    html = open(page_path, encoding="utf-8").read()
    latest_no = str(rounds[0]["draw_no"])
    new_html = re.sub(r"로또( ?)\d+회", lambda m: "로또" + m.group(1) + latest_no + "회", html)
    if new_html != html:
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(new_html)

print("lotto-data.js OK:", rounds[0]["draw_no"], "회차,", len(rounds), "rounds")
