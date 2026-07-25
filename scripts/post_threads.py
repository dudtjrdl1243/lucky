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

# 본문에는 링크를 넣지 않고 첫 댓글로 분리한다.
# (스레드는 본문에 외부 링크가 있으면 노출이 줄어드는 편)
# 형식: (본문, 댓글에 붙일 페이지, 댓글 앞머리)

# ── 운세 티저 (월·수·금) ─────────────────────────────
FORTUNE = [
    ("오늘 12간지 중에 1위인 띠가 있다는데\n내 띠는 몇 위려나", "tti.html", "여기서 확인함"),
    ("출근길에 오늘 운세 한 번 보고 가는 사람\n나만 그런 거 아니지", "today.html", "보는 곳 남겨둠"),
    ("행운의 시간이랑 방향까지 알려주더라\n오늘은 좀 믿어보려고", "today.html", "여기"),
    ("별자리 운세 오늘 순위 나왔는데\n1위 아니면 안 보는 걸로", "zodiac.html", "순위 여기서 봄"),
    ("이름이랑 생년월일만 넣으면 30초컷\n금전운만 보고 나올 예정", "today.html", "링크 두고 감"),
    ("띠별 순위 매일 바뀌는 거 알고 있었나\n어제 꼴찌였는데 오늘은 좀", "tti.html", "여기"),
]

# ── 로또 (토) ────────────────────────────────────────
LOTTO = [
    ("토요일이다\n번호는 뽑았고 이제 기다리면 된다", "lotto.html", "번호 뽑은 곳"),
    ("이번 주도 조용히 번호 하나 뽑고 감\n되면 좋고 아니면 말고", "lotto.html", "여기"),
    ("당첨번호 확인은 밤에\n번호 뽑는 건 지금", "lotto.html", "링크 두고 감"),
    ("로또는 사는 게 아니라 일주일치 상상을 사는 거라던데\n오늘도 상상 결제 완료", "lotto.html", "여기서 뽑음"),
]

# ── 일상·공감 (링크 없음) : 저녁 슬롯에서 도달 확보용 ───
# 네 가지 결을 섞는다: 질문 던지기 / 공감·하소연 / 살림팁 / 가벼운 TMI
DAILY = [
    # 질문 던지기
    "방구석에서 제일 자주 하는 말\n\"이거 진작 살걸\"\n\n다들 진작 살걸 1위는 뭐임",
    "다들 집에 하나씩 있는 안 쓰는 가전\n나는 에어프라이어인데\n너네 집은 뭐임",
    "만원으로 하루 행복해질 수 있는 방법\n하나씩만 알려줘\n내껀 편의점 신상 털기",
    "이사할 때 제일 버리기 아까운 거 1위\n난 안 읽은 책들인데\n다들 뭐 못 버림?",
    "요즘 국룰 살림템 뭐 있음?\n나만 모르는 거 있을까봐 불안함",
    "배달 시킬 때 최소주문금액 맞추려고\n괜히 하나 더 담는 사람\n나만 그런 거 아니지",
    # 공감·하소연
    "일요일 밤에 제일 하기 싫은 일 1위\n1. 설거지\n2. 빨래 개기\n3. 내일 생각하기\n\n난 3번",
    "방 정리하다가 안 쓰는 물건 나오면\n왜 산 건지 기억도 안 남\n\n나만 그런 거 아니지?",
    "분명 어제 충전했는데\n아침에 보면 20%인 폰\n대체 밤에 뭐 하는 거임",
    "택배 오는 날이 제일 설레는데\n막상 뜯으면 '아 맞다 이거 샀었지'\n기억을 못 함",
    "퇴근하고 집 오면 아무것도 하기 싫은데\n또 내일 되면 뭐라도 사고 있음\n인간은 반복하는 존재",
    "냉장고 열고 5초간 멍때리다가\n그냥 닫는 거 나만 함?",
    # 살림팁
    "밀폐용기 냄새 뺄 때\n쌀뜨물에 30분 담가두면 싹 빠짐\n표백제보다 이게 나음",
    "프라이팬 기름때는 뜨거울 때\n키친타월로 한 번 닦고 설거지하면\n세제 반만 써도 됨",
    "옷장 눅눅할 때 신문지 몇 장 넣어두면\n습기 잡아줌\n제습제 사기 전에 이거부터",
    "전자레인지 안 냄새는\n레몬 반 개 넣고 2분 돌리면 사라짐\n이거 알고 나서 편해짐",
    "리모컨·손잡이 같은 데\n물티슈로만 닦지 말고 마른걸로 한 번 더\n안 그럼 자국 남더라",
    # 가벼운 TMI
    "오늘 방구석에서 3시간째 넷플릭스만 봄\n생산성 0이지만 행복 100",
    "장바구니에 담아두고 일주일 묵히면\n절반은 안 사게 되더라\n지금 내 장바구니엔 4개 있음",
    "커피 줄인다면서 오늘도 두 잔째\n내일부터는 진짜임 (17일째)",
    "청소 시작하려고 유튜브 청소 영상 틀었는데\n영상만 30분째 보는 중",
    "오늘 산 것 중 제일 잘 산 거\n1000원짜리 수세미\n삶의 질 이런 데서 올라감",
]

# ── 오후 정보글 (링크 없음) : 저장 유도용 ───────────────
# "저장해두고 싶은" 실용 정보. 사실 확실한 것만. 팔로우 전환의 핵심.
TIPS = [
    "택배 상자 버릴 때 송장 그냥 떼지 말고\n네임펜으로 개인정보만 쓱 긋기\n요즘 이거로 정보 털리는 사람 많음",
    "카드 포인트 통합조회\n'카드포인트 통합조회' 검색 → 여러 카드 흩어진 포인트 한 번에 현금화 가능\n평균 몇만 원씩 잠자고 있음",
    "냉동실 음식 언제 넣었는지 모르겠으면\n마스킹테이프에 날짜 적어 붙이기\n'냉동실 미라' 만들지 않는 유일한 방법",
    "영수증 잉크는 열에 지워짐\n중요한 영수증은 사진 찍어두기\n환불·AS 때 원본 요구하면 곤란해짐",
    "세탁기 통세척\n한 달에 한 번 빈 통에 과탄산소다 넣고 삶음 코스\n안 하면 빨래에서 냄새 나는 이유가 이거",
    "핸드폰 약정 끝났는데 그대로 쓰는 사람\n'선택약정 25% 할인' 신청하면 매달 요금 깎임\n통신사가 먼저 안 알려줌",
    "실리콘 주방용품 기름때\n식용유 살짝 묻혀 닦고 세척하면 미끌거림 사라짐\n기름은 기름으로",
    "안 쓰는 앱 구독 정리\n아이폰: 설정→내 이름→구독 / 안드로이드: 플레이스토어→결제\n생각보다 새고 있는 돈 많음",
    "가스레인지 기름때 굳은 거\n베이킹소다+물 반죽 발라 10분 뒤 닦기\n박박 문지를 필요 없어짐",
    "정부24에서 '숨은 환급금' 조회\n미환급 세금·보험료 한 번에 확인됨\n안 찾아가면 그냥 사라지는 돈",
    "옷에 볼펜 자국\n손소독제(알코올) 살짝 묻혀 두드리면 빠짐\n문지르지 말고 두드리기",
    "가전 살 때 '으뜸효율 환급'\n에너지효율 1등급 사면 최대 10% 돌려받음 (예산 소진 전까지)\n영수증 챙겨두기",
    "배수구 냄새\n식초 붓고 5분 뒤 뜨거운 물\n뚫어뻥 사기 전에 이것부터",
    "안경 김서림\n렌즈 안쪽에 주방세제 한 방울 문지르고 닦기\n마스크 쓸 때 효과 좋음",
    "전기요금 복지할인\n다자녀·출산·장애·기초수급 해당되면 한전 신청으로 매달 감면\n의외로 모르고 안 받는 집 많음",
]

# ── 가성비템 (화·목) : 쿠팡 파트너스 ─────────────────
# 본문은 제품을 특정하지 않는 혼잣말 한 줄만 둔다.
# 제품명·가격·광고표기·링크·수수료 고지는 전부 첫 댓글에 모은다.
DEAL_HOOKS = [
    "이거 필요한 시기가 되었나",
    "가격 보고 좀 놀람",
    "이 가격이면 그냥 사는 게 맞지",
    "고민하다 결국 담음",
    "이런 건 있으면 확실히 편하더라",
    "쟁여두면 마음이 편한 종류",
    "장바구니에서 일주일 버티다 결국 졌다",
    "살 땐 몰랐는데 없으면 아쉬운 것들 있잖아",
    "방구석 살림 난이도 한 칸 내려감",
    "이런 건 진작 알았어야 했는데",
    "안 사도 되는데 자꾸 눈에 밟히는 종류",
    "지출은 했지만 후회는 없는 쪽",
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
    """(본문, 첫 댓글, 본문에 붙일 이미지 URL) 을 돌려준다. 없으면 None."""
    # 수동 실행 시 THREADS_FORCE_TYPE 로 콘텐츠 종류 지정 가능
    forced = os.environ.get("THREADS_FORCE_TYPE", "").strip().lower()
    wd = kst.tm_wday  # 0=월

    def with_link(item):
        body, page, lead = item
        return body, lead + "\n👉 " + SITE + page

    if forced == "fortune" or (not forced and wd in (0, 2, 4)):
        b, r = with_link(pick(FORTUNE)); return b, r, None
    if forced == "lotto" or (not forced and wd == 5):
        b, r = with_link(pick(LOTTO)); return b, r, None
    if forced == "tips":
        # 오후 정보글 (저장 유도용, 링크 없음)
        return TIPS[kst.tm_yday % len(TIPS)], None, None
    if forced == "daily" or (not forced and wd == 6):
        # 일상글은 링크 없이 (도달 확보용). 저녁 슬롯이라 날짜에 오프셋을 줘
        # 같은 날 아침 글과, 어제 저녁 글과 겹치지 않게 한다.
        idx = (kst.tm_yday * 2 + 1) % len(DAILY)
        return DAILY[idx], None, None

    # 화·목 (또는 forced == "deal") : 가성비템
    deal = load_deal()
    if not deal:
        b, r = with_link(pick(FORTUNE)); return b, r, None
    name = deal["name"]
    if len(name) > 40:
        name = name[:40] + "…"
    url = deal["url"] + ("&" if "?" in deal["url"] else "?") + "subid=th"  # 스레드 유입 구분
    # 본문에 제품 사진이 들어가므로 광고 표기를 본문에도 남긴다 (표시 위치 규정 대응)
    body = pick(DEAL_HOOKS) + "\n\n#광고"
    reply = "{}\n{:,}원{}\n\n{}\n\n쿠팡 파트너스 활동의 일환으로 수수료를 제공받습니다.".format(
        name, deal["price"], " · 로켓배송" if deal.get("rocket") else "", url)
    return body, reply, (deal.get("image") or None)

text, reply_text, image_url = build_text()

def api(path, params):
    data = urllib.parse.urlencode(dict(params, access_token=TOKEN)).encode()
    req = urllib.request.Request("https://graph.threads.net/v1.0/" + path, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def publish(txt, reply_to=None, image=None):
    params = {"text": txt}
    if image:
        params["media_type"] = "IMAGE"
        params["image_url"] = image
    else:
        params["media_type"] = "TEXT"
    if reply_to:
        params["reply_to_id"] = reply_to
    c = api(USER_ID + "/threads", params)
    time.sleep(3 if not image else 6)  # 이미지는 처리 시간이 더 필요
    return api(USER_ID + "/threads_publish", {"creation_id": c["id"]})

try:
    try:
        result = publish(text, image=image_url)
    except Exception as e:
        if image_url:
            print("이미지 게시 실패, 글만 올립니다:", e)
            result = publish(text)
        else:
            raise
    post_id = result.get("id")
    print("스레드 포스팅 성공:", post_id)
    print("--- 본문 ---")
    print(text)

    # 링크는 본문이 아니라 첫 댓글로 (본문에 외부 링크가 있으면 노출이 줄어드는 편)
    if reply_text and post_id:
        try:
            rep = publish(reply_text, reply_to=post_id)
            print("첫 댓글 작성 성공:", rep.get("id"))
            print("--- 댓글 ---")
            print(reply_text)
        except Exception as e:
            print("첫 댓글 작성 실패(본문은 정상 게시됨):", e)
except Exception as e:
    print("스레드 포스팅 실패:", e)
    sys.exit(0)
