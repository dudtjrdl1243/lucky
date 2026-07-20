# -*- coding: utf-8 -*-
"""쿠팡 골드박스(오늘의 특가) → deals-data.js 생성
GitHub Actions에서 매일 실행. API 키는 환경변수로 주입.
"""
import hmac, hashlib, json, os, sys, time, urllib.request

ACCESS_KEY = os.environ.get("COUPANG_ACCESS_KEY", "")
SECRET_KEY = os.environ.get("COUPANG_SECRET_KEY", "")
DOMAIN = "https://api-gateway.coupang.com"
PATH = "/v2/providers/affiliate_open_api/apis/openapi/products/goldbox"

if not ACCESS_KEY or not SECRET_KEY:
    print("COUPANG_ACCESS_KEY / COUPANG_SECRET_KEY 환경변수가 없습니다.")
    sys.exit(1)

# 일시적 API 오류(429/5xx/타임아웃)가 전체 파이프라인을 죽이지 않도록,
# 최대 3회 재시도하고 그래도 실패하면 기존 데이터를 유지한 채 정상 종료(exit 0).
def fetch_goldbox():
    for attempt in range(3):
        sd = time.strftime('%y%m%dT%H%M%SZ', time.gmtime())
        sig = hmac.new(SECRET_KEY.encode(), (sd + "GET" + PATH).encode(), hashlib.sha256).hexdigest()
        auth = "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(ACCESS_KEY, sd, sig)
        req = urllib.request.Request(DOMAIN + PATH)
        req.add_header("Authorization", auth)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print("골드박스 조회 실패 (시도 {}/3): {}".format(attempt + 1, e))
            time.sleep(5)
    return None

resp = fetch_goldbox()
if resp is None:
    print("골드박스 API가 계속 실패하여 기존 데이터를 유지합니다.")
    sys.exit(0)

items = resp.get("data") or []
if not items:
    print("골드박스 응답이 비어 있어 기존 데이터를 유지합니다.")
    sys.exit(0)

deals = []
for i in sorted(items, key=lambda x: x.get("rank") or 999):
    deals.append({
        "name": i.get("productName", ""),
        "price": int(i.get("productPrice") or 0),
        "image": i.get("productImage", ""),
        "url": i.get("productUrl", ""),
        "category": i.get("categoryName", ""),
        "rocket": bool(i.get("isRocket")),
    })

updated = time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() + 9 * 3600 - time.timezone if time.daylight == 0 else 0))
# KST 표기 (UTC 기준 실행 환경 대비)
updated = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 9 * 3600))

out = "const DEALS = " + json.dumps(deals, ensure_ascii=False) + ";\n"
out += 'const DEALS_UPDATED = "' + updated + '";\n'

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(base, "deals-data.js"), "w", encoding="utf-8") as f:
    f.write(out)
print("deals-data.js 갱신 완료:", len(deals), "개 상품,", updated)
