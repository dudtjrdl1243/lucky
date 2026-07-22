# -*- coding: utf-8 -*-
"""새 회차 당첨번호가 확인되면 스레드·텔레그램에 즉시 알린다.
- 토요일 추첨(20:45) 직후 검색 수요가 몰리는 시간대를 노린다.
- 이미 알린 회차는 lotto-announced.json 으로 기억해 중복 발송하지 않는다.
  (따라서 하루 여러 번 실행돼도 안전하다.)
- 토큰이 없으면 해당 채널만 조용히 건너뛴다.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dudtjrdl1243.github.io/lucky/"
STATE = os.path.join(BASE, "lotto-announced.json")

TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
TH_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
TH_USER = os.environ.get("THREADS_USER_ID", "").strip()


def read_js_object(path, varname):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"const " + varname + r" = (.*?);\s*$", src, re.S | re.M)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


rounds = read_js_object(os.path.join(BASE, "lotto-data.js"), "LOTTO_ROUNDS")
if not rounds:
    print("lotto-data.js 를 읽지 못해 종료합니다.")
    sys.exit(0)
L = rounds[0]

# 이미 알린 회차인지 확인
last = 0
if os.path.exists(STATE):
    try:
        # utf-8-sig: 편집기가 붙인 BOM이 있어도 읽히도록
        last = json.load(open(STATE, encoding="utf-8-sig")).get("announced", 0)
    except Exception:
        last = 0
if L["round"] <= last:
    print("{}회는 이미 알렸습니다. 건너뜁니다.".format(L["round"]))
    sys.exit(0)

# 우리 추천번호 성적 (있으면 함께 알린다)
picks = read_js_object(os.path.join(BASE, "lotto-picks.js"), "LOTTO_PICKS") or {}
score_line = ""
for r in (picks.get("results") or []):
    if r.get("round") == L["round"]:
        best = max(g["hit"] for g in r["games"])
        top = [g for g in r["games"] if g["hit"] == best][0]
        score_line = "별별운세 추천번호는 최고 {}개 적중 ({})".format(best, top["label"])
        break

nums = " · ".join(str(n) for n in L["numbers"])
prize = L.get("firstPrize") or 0
prize_txt = "{:,}억원".format(round(prize / 100000000, 1)).replace(".0억", "억") if prize >= 100000000 else "{:,}만원".format(round(prize / 10000))


def post_telegram():
    """실제로 발송했으면 True. 설정이 없어 건너뛴 경우는 False."""
    if not TG_TOKEN or not TG_CHAT:
        print("텔레그램 설정 없음 — 건너뜀")
        return False
    lines = [
        "🎱 <b>로또 {}회 당첨번호</b>".format(L["round"]),
        "",
        "<b>{}</b>".format(nums),
        "보너스 {}".format(L["bonus"]),
        "",
        "1등 {}명 · 1인당 {}".format(L.get("firstWinners", 0), prize_txt),
    ]
    if score_line:
        lines += ["", score_line]
    lines += ["", "👉 " + SITE + "lotto-result.html"]
    data = urllib.parse.urlencode({
        "chat_id": TG_CHAT, "text": "\n".join(lines),
        "parse_mode": "HTML", "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request("https://api.telegram.org/bot{}/sendMessage".format(TG_TOKEN), data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        ok = json.loads(r.read().decode()).get("ok")
    print("텔레그램 발송:", "성공" if ok else "실패")
    return bool(ok)


def post_threads():
    """실제로 발송했으면 True. 설정이 없어 건너뛴 경우는 False."""
    if not TH_TOKEN:
        print("스레드 토큰 없음 — 건너뜀")
        return False
    uid = TH_USER
    if not uid:
        url = "https://graph.threads.net/v1.0/me?fields=id&access_token=" + urllib.parse.quote(TH_TOKEN)
        with urllib.request.urlopen(url, timeout=30) as r:
            uid = json.loads(r.read().decode())["id"]

    # 본문에는 링크를 넣지 않는다 (스레드는 외부 링크가 있으면 노출이 줄어드는 편)
    body = ["{}회 당첨번호 나왔다".format(L["round"]), "", nums + "  +  " + str(L["bonus"]), "",
            "1등 {}명 · 1인당 {}".format(L.get("firstWinners", 0), prize_txt)]
    if score_line:
        body += ["", score_line]
    text = "\n".join(body)
    reply_text = "회차별 당첨번호랑 추천 성적표\n👉 " + SITE + "lotto-result.html"

    def api(path, params):
        data = urllib.parse.urlencode(dict(params, access_token=TH_TOKEN)).encode()
        req = urllib.request.Request("https://graph.threads.net/v1.0/" + path, data=data)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    def publish(txt, reply_to=None):
        params = {"media_type": "TEXT", "text": txt}
        if reply_to:
            params["reply_to_id"] = reply_to
        c = api(uid + "/threads", params)
        time.sleep(3)
        return api(uid + "/threads_publish", {"creation_id": c["id"]})

    res = publish(text)
    pid = res.get("id")
    print("스레드 발송 성공:", pid)
    print(text)
    if pid:
        try:
            rep = publish(reply_text, reply_to=pid)
            print("첫 댓글 작성 성공:", rep.get("id"))
        except Exception as e:
            print("첫 댓글 작성 실패(본문은 정상 게시됨):", e)
    return True


sent = False
for fn in (post_telegram, post_threads):
    try:
        if fn():
            sent = True
    except Exception as e:
        print("{} 실패: {}".format(fn.__name__, e))

if not sent:
    print("어느 채널에도 발송하지 못해 상태를 저장하지 않습니다 (다음 실행에서 재시도).")

if sent:
    json.dump({"announced": L["round"], "at": time.strftime("%Y-%m-%d %H:%M", time.gmtime(time.time() + 9 * 3600))},
              open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
    print("{}회 발송 완료 — 상태 저장".format(L["round"]))
