# -*- coding: utf-8 -*-
"""최근 Threads 게시물의 공식 인사이트를 사이트용 JSON으로 갱신한다."""
import datetime
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "threads-insights.json")
TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
USER_ID = os.environ.get("THREADS_USER_ID", "").strip()
API = "https://graph.threads.com/v1.0/"
SITE = "dudtjrdl1243.github.io/lucky"
KST = datetime.timezone(datetime.timedelta(hours=9))


def get(path, params):
    query = urllib.parse.urlencode(dict(params, access_token=TOKEN))
    with urllib.request.urlopen(API + path + "?" + query, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def metric_value(item):
    if isinstance(item.get("total_value"), dict):
        return item["total_value"].get("value", 0) or 0
    values = item.get("values") or []
    return (values[0].get("value", 0) if values else 0) or 0


def content_type(text, dt):
    if "#광고" in text or "골드박스" in text:
        return "deal"
    if "로또" in text or "당첨번호" in text or "회차" in text:
        return "lotto"
    if "띠" in text or "별자리" in text or "운세" in text:
        return "fortune"
    # 자동 게시 슬롯을 기준으로 링크 없는 글을 구분한다.
    hour = dt.astimezone(KST).hour
    return "tips" if hour < 17 else "daily"


def main():
    global USER_ID
    if not TOKEN:
        print("THREADS_ACCESS_TOKEN 없음 - 인사이트 갱신을 건너뜁니다.")
        return
    if not USER_ID:
        USER_ID = str(get("me", {"fields": "id"})["id"])

    media = get(USER_ID + "/threads", {
        "fields": "id,text,timestamp,permalink,media_type", "limit": 100,
    }).get("data", [])
    posts = []
    campaign_clicks = {}
    denied = None
    for i, item in enumerate(media):
        text = (item.get("text") or "").strip()
        # 첫 댓글의 홍보 링크는 독립 게시물 성과표에서 제외한다.
        if not text or SITE in text:
            continue
        try:
            raw = get(str(item["id"]) + "/insights", {
                "metric": "views,likes,replies,reposts,quotes,shares",
            }).get("data", [])
        except Exception as e:
            denied = e
            break
        metrics = {m["name"]: metric_value(m) for m in raw}
        try:
            dt = datetime.datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        except Exception:
            dt = datetime.datetime.now(datetime.timezone.utc)
        interactions = (metrics.get("likes", 0) + metrics.get("replies", 0) * 2
                        + metrics.get("reposts", 0) * 3 + metrics.get("quotes", 0) * 3
                        + metrics.get("shares", 0) * 3)
        posts.append({
            "id": str(item["id"]),
            "content_id": hashlib.sha1("".join(text.split()).encode("utf-8")).hexdigest()[:8],
            "timestamp": item.get("timestamp"),
            "type": content_type(text, dt),
            "text": text,
            "permalink": item.get("permalink", ""),
            "views": int(metrics.get("views", 0)),
            "likes": int(metrics.get("likes", 0)),
            "replies": int(metrics.get("replies", 0)),
            "reposts": int(metrics.get("reposts", 0)),
            "quotes": int(metrics.get("quotes", 0)),
            "shares": int(metrics.get("shares", 0)),
            "score": int(interactions),
        })
        if i % 10 == 9:
            time.sleep(1)

    if denied is not None:
        print("Threads 인사이트를 읽지 못했습니다. threads_manage_insights 권한을 확인하세요:", denied)
        return
    if not posts:
        print("저장할 Threads 게시물이 없어 기존 파일을 유지합니다.")
        return

    # Threads 자체가 센 링크 클릭 수도 함께 저장한다. UTM이 붙은 URL은 게시일/종류가
    # 들어 있으므로 사이트 카운터와 나란히 보면 중간 이탈도 확인할 수 있다.
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        user_data = get(USER_ID + "/threads_insights", {
            "metric": "clicks",
            "since": int((now_utc - datetime.timedelta(days=45)).timestamp()),
            "until": int(now_utc.timestamp()),
        }).get("data", [])
        for metric in user_data:
            for link in metric.get("link_total_values", []) or []:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(link.get("link_url", "")).query)
                campaign = (query.get("utm_campaign") or [""])[0]
                if campaign.startswith("th_"):
                    campaign_clicks[campaign] = campaign_clicks.get(campaign, 0) + int(link.get("value", 0) or 0)
    except Exception as e:
        print("Threads 공식 링크 클릭 수는 이번에 읽지 못했습니다:", e)

    payload = {
        "updated_at": datetime.datetime.now(KST).isoformat(timespec="seconds"),
        "posts": posts,
        "campaign_clicks": campaign_clicks,
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, OUT)
    print("Threads 인사이트 {}건 저장".format(len(posts)))


if __name__ == "__main__":
    main()
