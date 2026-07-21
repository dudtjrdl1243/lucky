# -*- coding: utf-8 -*-
"""스레드(Threads) 자동 포스팅 — 요일별 콘텐츠 로테이션
  월·수·금 : 운세 티저 (사이트 링크)
  화·목    : 오늘의 가성비템 (쿠팡 파트너스, [광고] 표기)
  토       : 로또 (사이트 링크)
  일       : 일상·공감글 (링크 없음, 순수 도달용)
말투는 계정 톤(짧고 건조한 반말 혼잣말)에 맞춤. 하루 1개만 게시.
THREADS_ACCESS_TOKEN 없으면 조용히 건너뜀. USER_ID는 토큰으로 자동 조회.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
USER_ID = os.environ.get("THREADS_USER_ID", "")
SITE = "https://dudtjrdl1243.github.io/lucky/"

if not TOKEN:
    print("스레드 토큰 없음 - 건너뜁니다.")
    sys.exit(0)

if not USER_ID:
    try:
        url = "https://graph.threads.net/v1.0/me?fields=id&access_token=" + urllib.parse.quote(TOKEN)
        with urllib.request.urlopen(url, timeout=30) as r:
            USER_ID = json.loads(r.read().decode())["id"]
        print("스레드 사용자 ID 자동 조회:", USER_ID)
    except Exception as e:
        print("스레드 사용자 ID 조회 실패:", e)
        sys.exit(0)

kst = time.gmtime(time.time() + 9 * 3600)
week = int(time.strftime("%W", kst))  # 주차 → 같은 요일이라도 매주 다른 문구

# ── 운세 티저 (월·수·금) ─────────────────────────────
FORTUNE = [
    "오늘 12간지 중에 1위인 띠가 있다는데\n내 띠는 몇 위려나\n\n👉 " + SITE + "tti.html",
    "출근길에 오늘 운세 한 번 보고 가는 사람\n나만 그런 거 아니지\n\n👉 " + SITE + "today.html",
    "행운의 시간이랑 방향까지 알려주더라\n오늘은 좀 믿어보려고\n\n👉 " + SITE + "today.html",
    "별자리 운세 오늘 순위 나왔는데\n1위 아니면 안 보는 걸로\n\n👉 " + SITE + "saju.html",
    "이름이랑 생년월일만 넣으면 30초컷\n금전운만 보고 나올 예정\n\n👉 " + SITE + "today.html",
    "띠별 순위 매일 바뀌는 거 알고 있었나\n어제 꼴찌였는데 오늘은 좀\n\n👉 " + SITE + "tti.html",
]

# ── 로또 (토) ────────────────────────────────────────
LOTTO = [
    "토요일이다\n번호는 뽑았고 이제 기다리면 된다\n\n👉 " + SITE + "lotto.html",
    "이번 주도 조용히 번호 하나 뽑고 감\n되면 좋고 아니면 말고\n\n👉 " + SITE + "lotto.html",
    "당첨번호 확인은 밤에\n번호 뽑는 건 지금\n\n👉 " + SITE + "lotto.html",
    "로또는 사는 게 아니라 일주일치 상상을 사는 거라던데\n오늘도 상상 결제 완료\n\n👉 " + SITE + "lotto.html",
]

# ── 일상·공감 (일) : 링크 없음 ───────────────────────
DAILY = [
    "방구석에서 제일 자주 하는 말\n\"이거 진작 살걸\"\n\n다들 진작 살걸 1위는 뭐임",
    "살림템은 늦게 알수록 손해더라\n요즘 늦게 알아서 억울한 거 하나씩 있지 않나",
    "일요일 밤에 제일 하기 싫은 일 1위\n1. 설거지\n2. 빨래 개기\n3. 내일 생각하기\n\n난 3번",
    "돈 쓰는 것보다 안 쓰는 게 어려운 요즘\n이번 주 참은 거 하나씩 자랑해보자",
    "방 정리하다가 안 쓰는 물건 나오면\n왜 산 건지 기억도 안 남\n\n나만 그런 거 아니지?",
    "요즘 만원으로 살 수 있는 게 진짜 없다\n그래도 하나 건지면 그날 하루 기분 좋음",
    "장바구니에 담아두고 일주일 묵히면\n절반은 안 사게 되더라\n지금 내 장바구니엔 4개 있음",
]

# ── 가성비템 (화·목) : 쿠팡 파트너스 ─────────────────
DEAL_HOOKS = [
    "이거 필요한 시기가 되었나",
    "가격 보고 좀 놀람",
    "이 가격이면 그냥 사는 게 맞지",
    "고민하다 결국 담음",
    "이런 건 있으면 확실히 편하더라",
    "쟁여두면 마음이 편한 종류",
]

def pick(pool):
    # 날짜 기준으로 골라야 같은 주의 월·수·금이 서로 다른 문구가 됨
    return pool[kst.tm_yday % len(pool)]

def load_deal():
    """deals-data.js에서 로켓배송 상품 하나 고르기 (주차별로 다른 상품)"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "deals-data.js")
    if not os.path.exists(path):
        return None
    m = re.search(r"const DEALS = (\[.*?\]);", open(path, encoding="utf-8").read(), re.S)
    if not m:
        return None
    deals = [d for d in json.loads(m.group(1)) if d.get("url")]
    if not deals:
        return None
    rockets = [d for d in deals if d.get("rocket")] or deals
    return rockets[(week + kst.tm_yday) % len(rockets)]

def build_text():
    # 수동 실행 시 THREADS_FORCE_TYPE 로 콘텐츠 종류 지정 가능
    forced = os.environ.get("THREADS_FORCE_TYPE", "").strip().lower()
    wd = kst.tm_wday  # 0=월
    if forced == "fortune" or (not forced and wd in (0, 2, 4)):
        return pick(FORTUNE)
    if forced == "lotto" or (not forced and wd == 5):
        return pick(LOTTO)
    if forced == "daily" or (not forced and wd == 6):
        return pick(DAILY)
    # 화·목 (또는 forced == "deal") : 가성비템
    deal = load_deal()
    if not deal:
        return pick(FORTUNE)
    name = deal["name"]
    if len(name) > 40:
        name = name[:40] + "…"
    return "[광고] {}\n\n{}\n{:,}원{}\n\n{}\n\n쿠팡 파트너스 활동의 일환으로 수수료를 제공받습니다.".format(
        pick(DEAL_HOOKS), name, deal["price"],
        " · 로켓배송" if deal.get("rocket") else "", deal["url"])

text = build_text()

def api(path, params):
    data = urllib.parse.urlencode(dict(params, access_token=TOKEN)).encode()
    req = urllib.request.Request("https://graph.threads.net/v1.0/" + path, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

try:
    container = api(USER_ID + "/threads", {"media_type": "TEXT", "text": text})
    time.sleep(3)
    result = api(USER_ID + "/threads_publish", {"creation_id": container["id"]})
    print("스레드 포스팅 성공:", result.get("id"))
    print("--- 내용 ---")
    print(text)
except Exception as e:
    print("스레드 포스팅 실패:", e)
    sys.exit(0)
