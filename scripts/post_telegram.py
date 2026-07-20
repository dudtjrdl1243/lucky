# -*- coding: utf-8 -*-
"""골드박스 특가를 텔레그램 채널에 자동 포스팅.
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 환경변수가 없으면 조용히 건너뜀.
deals-data.js(update_deals.py가 먼저 생성)를 읽어서 상위 8개를 올린다.
"""
import json, os, re, sys, time, urllib.request, urllib.parse

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TOKEN or not CHAT_ID:
    print("텔레그램 설정 없음 — 건너뜁니다.")
    sys.exit(0)

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(base, "deals-data.js"), encoding="utf-8").read()
m = re.search(r"const DEALS = (\[.*?\]);", src, re.S)
if not m:
    print("deals-data.js 파싱 실패")
    sys.exit(1)
deals = json.loads(m.group(1))[:8]

kst = time.gmtime(time.time() + 9 * 3600)
lines = ["🔥 <b>오늘의 쿠팡 골드박스 특가</b> ({}/{})".format(kst.tm_mon, kst.tm_mday), ""]
for n, d in enumerate(deals, 1):
    name = d["name"][:45] + ("…" if len(d["name"]) > 45 else "")
    rocket = " 🚀" if d.get("rocket") else ""
    lines.append('{}. <a href="{}">{}</a>\n   💰 {:,}원{}'.format(n, d["url"], name, d["price"], rocket))
lines.append("")
lines.append("🔮 무료 운세도 보고 가세요 → https://dudtjrdl1243.github.io/lucky/")
lines.append("")
lines.append("<i>이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</i>")

payload = urllib.parse.urlencode({
    "chat_id": CHAT_ID,
    "text": "\n".join(lines),
    "parse_mode": "HTML",
    "disable_web_page_preview": "true",
}).encode()
req = urllib.request.Request("https://api.telegram.org/bot{}/sendMessage".format(TOKEN), data=payload)
with urllib.request.urlopen(req, timeout=30) as r:
    resp = json.loads(r.read().decode())
print("텔레그램 전송:", "성공" if resp.get("ok") else resp)
