# -*- coding: utf-8 -*-
"""스레드(Threads) 자동 포스팅 — 매일 오늘의 운세 티저 + 사이트 링크
THREADS_ACCESS_TOKEN / THREADS_USER_ID 환경변수가 없으면 조용히 건너뜀.
Threads 공식 API: 컨테이너 생성 → 발행 2단계.
"""
import json, os, sys, time, urllib.request, urllib.parse

TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "")
USER_ID = os.environ.get("THREADS_USER_ID", "")
SITE = "https://dudtjrdl1243.github.io/lucky/"

if not TOKEN or not USER_ID:
    print("스레드 설정 없음 - 건너뜁니다.")
    sys.exit(0)

kst = time.gmtime(time.time() + 9 * 3600)
weekday = ["월", "화", "수", "목", "금", "토", "일"][kst.tm_wday]

# 요일별로 다른 티저 (같은 글 반복 방지)
TEASERS = [
    "월요일 출근길, 오늘 하루 기운이 궁금하다면 🔮\n이름+생년월일만 넣으면 오늘의 총운·금전운·애정운이 무료!",
    "오늘 12간지 중 1위는 무슨 띠일까? 👑\n내 띠 순위 무료로 확인하고 가세요!",
    "수요일 고비, 행운의 시간과 방향으로 넘겨봐요 ⏰\n오늘의 운세 무료 확인!",
    "목요일, 이번 주 로또 사기 전에 행운의 번호부터 🍀\n우주의 기운 담은 번호 무료 생성!",
    "불금 시작! 오늘 애정운이 궁금하다면 💗\n무료 운세 30초면 끝!",
    "로또 추첨일! 🎱 행운의 번호 아직 안 뽑았다면 지금이 마지막 기회.\n당첨번호도 오늘 밤 자동 업데이트!",
    "일요일 밤, 다음 주 기운 미리 보기 🌙\n띠별·별자리 운세 무료로 확인하세요!",
]
text = "🔮 " + str(kst.tm_mon) + "/" + str(kst.tm_mday) + " (" + weekday + ")\n\n" + TEASERS[kst.tm_wday] + "\n\n👉 " + SITE

def api(path, params):
    data = urllib.parse.urlencode(dict(params, access_token=TOKEN)).encode()
    req = urllib.request.Request("https://graph.threads.net/v1.0/" + path, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

try:
    container = api(USER_ID + "/threads", {"media_type": "TEXT", "text": text})
    time.sleep(3)  # 컨테이너 처리 대기 (권장)
    result = api(USER_ID + "/threads_publish", {"creation_id": container["id"]})
    print("스레드 포스팅 성공:", result.get("id"))
except Exception as e:
    print("스레드 포스팅 실패:", e)
    sys.exit(0)  # 스레드 실패가 전체 워크플로를 막지 않게
