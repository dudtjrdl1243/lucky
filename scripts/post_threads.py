# -*- coding: utf-8 -*-
"""스레드(Threads) 자동 포스팅 — 요일별 콘텐츠 로테이션
  월·수·금 : 운세 티저 (사이트 링크)
  화·목    : 오늘의 가성비템 (쿠팡 파트너스, [광고] 표기)
  토       : 로또 (사이트 링크)
  일       : 일상·공감글 (링크 없음, 순수 도달용)
말투는 계정 톤(짧고 건조한 반말 혼잣말)에 맞춤. 하루 1개만 게시.
THREADS_ACCESS_TOKEN 없으면 조용히 건너뜀. USER_ID는 토큰으로 자동 조회.
"""
import datetime, json, os, re, sys, time, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fortune_calc

TOKEN = os.environ.get("THREADS_ACCESS_TOKEN", "").strip()
USER_ID = os.environ.get("THREADS_USER_ID", "").strip()
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
KST_TODAY = time.strftime("%Y-%m-%d", kst)
KST_TZ = datetime.timezone(datetime.timedelta(hours=9))

# ── 이미 올린 글 조회 (중복 방지의 핵심) ───────────────
# 깃허브 액션 예약 실행은 1~2시간씩 밀리거나 통째로 건너뛴다. 그래서 한 슬롯에
# 여러 번 예약을 걸어두는데, 그러면 같은 글이 두 번 나갈 수 있다.
# 실제로 올라간 글을 API로 확인해서 (1) 오늘 이 슬롯 글이 이미 나갔으면 건너뛰고
# (2) 최근에 쓴 문구는 다시 고르지 않는다.
def fetch_recent(limit=500):
    """최근 게시물을 페이지 끝까지 읽어 오래된 문구 재사용도 막는다.

    예전에는 50개만 확인해서 하루 2~3회 게시 기준 약 2~3주가 지나면
    이미 쓴 정보글을 새 글로 착각했다. Threads가 주는 paging.next를 따라가되
    작업 시간이 과도하게 늘지 않도록 최대 limit개에서 멈춘다.
    """
    page_size = min(100, limit)
    url = ("https://graph.threads.net/v1.0/" + USER_ID + "/threads"
           "?fields=text,timestamp&limit=" + str(page_size) +
           "&access_token=" + urllib.parse.quote(TOKEN))
    posts, seen_urls = [], set()
    while url and len(posts) < limit and url not in seen_urls:
        seen_urls.add(url)
        with urllib.request.urlopen(url, timeout=30) as r:
            payload = json.loads(r.read().decode())
        posts.extend(payload.get("data", []))
        url = (payload.get("paging") or {}).get("next")
    return posts[:limit]


def _norm(s):
    """공백·줄바꿈 차이를 무시하고 같은 글인지 비교하기 위한 정규화"""
    return re.sub(r"\s+", "", s or "")


def _kst_date(ts):
    try:
        return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z") \
                               .astimezone(KST_TZ).strftime("%Y-%m-%d")
    except Exception:
        return ""


RECENT, RECENT_OK = [], False
for _try in range(2):
    try:
        RECENT = fetch_recent()
        RECENT_OK = True
        print("최근 게시물 {}건 조회 — 중복 검사에 사용".format(len(RECENT)))
        break
    except Exception as e:
        print("최근 게시물 조회 실패 ({}/2): {}".format(_try + 1, e))
        if _try == 0:
            time.sleep(5)

# 조회에 실패하면 중복인지 알 수 없다. 이때 재시도 예약까지 글을 올리면
# 같은 글이 여러 번 나가므로, 확인이 안 된 재시도 실행은 그냥 포기한다.
# (본 예약 실행은 하루 한 번뿐이라 그대로 진행해도 중복이 생기지 않는다.)
if not RECENT_OK and os.environ.get("THREADS_REQUIRE_CHECK", "").strip() == "1":
    print("중복 확인을 못 했고 이번은 재시도 실행이라 건너뜁니다.")
    sys.exit(0)

RECENT_TEXTS = set(_norm(p.get("text")) for p in RECENT)
TODAY_TEXTS = set(_norm(p.get("text")) for p in RECENT
                  if _kst_date(p.get("timestamp", "")) == KST_TODAY)

# 본문에는 링크를 넣지 않고 첫 댓글로 분리한다.
# (스레드는 본문에 외부 링크가 있으면 노출이 줄어드는 편)
# 형식: (본문, 댓글에 붙일 페이지, 댓글 앞머리)

# ── 운세 티저 (월·수·금) ─────────────────────────────
# 오늘 실제로 계산된 순위를 그대로 넣는 티저.
# 사이트에서 나오는 값과 같아야 하므로 fortune_calc(=JS 엔진과 동일 규칙)로 계산한다.
# 매일 내용이 바뀌므로 같은 문구가 반복될 일이 없다.
def live_fortune():
    try:
        f = fortune_calc.today_facts()
    except Exception as e:
        print("오늘의 순위 계산 실패 — 일반 문구만 사용합니다:", e)
        return []
    tti, zod = f["tti"], f["zodiac"]
    t1, t2, t3, tlast = tti[0][0], tti[1][0], tti[2][0], tti[-1][0]
    z1, z2, z3 = zod[0][0], zod[1][0], zod[2][0]
    return [
        ("오늘 띠별 운세 1위 {}띠\n2위 {}띠, 3위 {}띠\n내 띠는 몇 위인지 보고 옴".format(t1, t2, t3),
         "tti.html", "12띠 순위 여기서 봄"),
        ("오늘 별자리 1위 {}\n2위 {}, 3위 {}\n내 자리는 어디쯤인지 확인함".format(z1, z2, z3),
         "zodiac.html", "12별자리 순위 여기"),
        ("오늘은 {}일 — {} 기운이 도는 날\n띠 순위 1위는 {}띠라는데".format(f["day_name"], f["day_elem"], t1),
         "tti.html", "계산 근거까지 여기 있음"),
        ("오늘 {}띠가 1위\n{}띠가 12위\n같은 날인데 이렇게 갈리네".format(t1, tlast),
         "tti.html", "전체 순위 여기"),
        ("달은 지금 {} 단계\n오늘 별자리 1위는 {}로 나옴".format(f["moon"], z1),
         "zodiac.html", "내 별자리 순위 여기"),
        ("태양이 지금 {}에 있어서\n오늘은 {} 흐름이 제일 좋다고".format(f["sun_sign"], z1),
         "zodiac.html", "순위 확인은 여기"),
        # 물어보는 글이 반응이 훨씬 크더라 (계정 실적·타 계정 상위글 둘 다 같은 방향)
        ("오늘 띠 순위 1위가 {}띠라는데\n여기 {}띠 있음?".format(t1, t1),
         "tti.html", "12띠 전체 순위 여기"),
        ("오늘 별자리 1위 {}\n{} 있으면 손 들어봐".format(z1, z1),
         "zodiac.html", "내 자리 몇 위인지 여기서 봄"),
        ("{}띠가 1위, {}띠가 12위래\n다들 무슨 띠임?".format(t1, tlast),
         "tti.html", "순위 나온 곳"),
    ]


# 인천 기준. Open-Meteo는 API 키가 필요 없고 무료라 등록·토큰 관리가 없다.
# 실패하면 그냥 빈 목록을 돌려주고 기존 일상글로 넘어간다.
WEATHER_URL = ("https://api.open-meteo.com/v1/forecast?latitude=37.4563&longitude=126.7052"
               "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
               "&timezone=Asia%2FSeoul&forecast_days=1")


def weather_daily():
    """오늘 실제 날씨로 만든 일상글. 날씨가 '할 말이 있을 때'만 후보를 낸다.
    선선하고 평범한 날엔 빈 목록을 돌려줘서, 날씨 얘기가 매일 나오는 패턴이 되지 않게 한다."""
    try:
        with urllib.request.urlopen(WEATHER_URL, timeout=15) as r:
            d = json.loads(r.read().decode())["daily"]
        hi = int(round(d["temperature_2m_max"][0]))
        lo = int(round(d["temperature_2m_min"][0]))
        rain = float(d["precipitation_sum"][0] or 0)
        code = int(d["weather_code"][0])
    except Exception as e:
        print("날씨 조회 실패 — 일반 일상글로 넘어갑니다:", e)
        return []

    out = []
    if rain >= 3 or code in (61, 63, 65, 80, 81, 82, 95, 96, 99):
        out += ["비 와서 널어둔 빨래 다시 들여놨다\n오늘은 글렀네",
                "종일 비 오네\n나가려던 거 그냥 다 미뤘다"]
    elif code in (71, 73, 75, 77, 85, 86):
        out += ["눈 온다\n창밖만 보고 있는 중"]
    if hi >= 33:
        out += ["오늘 {}도\n에어컨 없이는 못 버티겠다".format(hi),
                "{}도래\n낮에 잠깐 나갔다가 바로 후회했다".format(hi)]
    elif hi >= 30:
        out += ["오늘 {}도\n선풍기 앞에서 안 움직이는 중".format(hi)]
    elif hi <= 0:
        out += ["오늘 최고가 {}도\n나가기 싫어서 그냥 배달 시켰다".format(hi)]
    elif hi <= 10:
        out += ["오늘 {}도까지밖에 안 올랐다\n이불 밖이 위험한 계절".format(hi)]
    if lo >= 25:
        out += ["밤인데 {}도\n창문 열어놔도 소용이 없다".format(lo)]
    if hi - lo >= 12:
        out += ["낮엔 {}도였는데 지금 {}도\n일교차 뭐지".format(hi, lo)]
    return out


def live_lotto():
    """lotto-picks.js 의 실제 값으로 만든 로또 티저.
    제외수 개수나 통계 수치는 매주 바뀌므로 글에 직접 적어두면 사이트와 어긋난다.
    그래서 운세와 마찬가지로 파일에서 읽어 그때그때 문장을 만든다."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "lotto-picks.js")
    try:
        m = re.search(r"const LOTTO_PICKS = (\{.*\});", open(path, encoding="utf-8").read(), re.S)
        p = json.loads(m.group(1))
    except Exception as e:
        print("로또 추천 데이터 읽기 실패 — 일반 문구만 사용합니다:", e)
        return []

    out = []
    ex, pat, res = p.get("exclude") or [], p.get("patterns") or {}, p.get("results") or []
    if ex:
        out.append(("이번 회차 제외수 {}개 뽑아뒀다\n최근 7회에 두 번 이상 나온 번호들".format(len(ex)),
                    "lotto.html", "제외수랑 추천번호 여기"))
    if pat.get("carryAnyPct"):
        out.append(("직전 회차 번호가 다음 주에 또 나온 경우가 {}%더라\n생각보다 높지 않나".format(pat["carryAnyPct"]),
                    "lotto.html", "이런 통계 정리해둠"))
    if pat.get("consecPct"):
        out.append(("당첨번호에 연속된 두 수가 들어간 회차가 {}%\n절반이 넘네".format(pat["consecPct"]),
                    "lotto.html", "패턴 정리해둔 곳"))
    if res:
        best = max(g["hit"] for g in res[0]["games"])
        tone = ("이 정도면 선방" if best >= 4 else
                "3개면 5등은 됐다" if best == 3 else
                "아쉽게 두 개" if best == 2 else
                "처참하네")
        out.append(("지난 회차 우리 추천번호 최고 {}개 맞았다\n{}\n\n그래도 성적표는 지우지 않고 그대로 둠".format(
            best, tone),
            "lotto.html", "전 회차 성적표 여기"))
    return out


FORTUNE = [
    ("오늘 12간지 중에 1위인 띠가 있다는데\n내 띠는 몇 위려나", "tti.html", "여기서 확인함"),
    ("출근길에 오늘 운세 한 번 보고 가는 사람\n나만 그런 거 아니지", "today.html", "보는 곳 남겨둠"),
    ("행운의 시간이랑 방향까지 알려주더라\n오늘은 좀 믿어보려고", "today.html", "여기"),
    ("별자리 운세 오늘 순위 나왔는데\n1위 아니면 안 보는 걸로", "zodiac.html", "순위 여기서 봄"),
    ("이름이랑 생년월일만 넣으면 30초컷\n금전운만 보고 나올 예정", "today.html", "링크 두고 감"),
    ("띠별 순위 매일 바뀌는 거 알고 있었나\n어제 꼴찌였는데 오늘은 좀", "tti.html", "여기"),
]

# ── 로또 (토) ────────────────────────────────────────
# 이 판은 "1등 예상번호" 자랑글로 이미 포화 상태다. 똑같이 해봐야 묻힌다.
# 우리만 가진 건 전 회차 성적표를 그대로 공개한다는 것 — 맞은 것만 보여주는 데는 많아도
# 틀린 걸 남기는 데는 거의 없다. 자랑 대신 그 정직함을 앞에 둔다.
LOTTO = [
    ("토요일이다\n번호는 뽑았고 이제 기다리면 된다", "lotto.html", "번호 뽑은 곳"),
    ("이번 주도 조용히 번호 하나 뽑고 감\n되면 좋고 아니면 말고", "lotto.html", "여기"),
    ("우리 추천번호 성적표 그대로 올려둠\n맞은 것만 보여주는 건 좀 그렇잖아",
     "lotto.html", "전 회차 기록 여기"),
    ("로또 번호 고를 때 뭐 보고 고름?\n난 그냥 통계 돌린 거 쓰는 편",
     "lotto.html", "돌린 결과 여기 있음"),
    ("당첨번호 확인은 밤에\n번호 뽑는 건 지금", "lotto.html", "링크 두고 감"),
    ("로또는 사는 게 아니라 일주일치 상상을 사는 거라던데\n오늘도 상상 결제 완료", "lotto.html", "여기서 뽑음"),
]

# ── 일상·공감 (링크 없음) : 저녁 슬롯에서 도달 확보용 ───
# 질문 던지기 / 공감·하소연 / 살림팁 / 가벼운 TMI / 담백한 기록 을 섞는다.
#
# 앞의 네 결은 전부 반응을 노린 구조다("다들 ~함?", "나만 그런 거 아니지", "~한 사람 나임").
# 하나씩 보면 괜찮은데 매일 나가면 패턴이 읽혀서 사람이 쓴 것 같지 않아진다.
# 그래서 마지막 '담백한 기록' 묶음은 일부러 질문도 펀치라인도 없이,
# 그냥 있었던 일을 적고 끝낸다. 반응은 덜 나오겠지만 계정이 사람처럼 보이는 값을 한다.
DAILY = [
    # 질문 던지기
    "방구석에서 제일 자주 하는 말\n\"이거 진작 살걸\"\n\n다들 진작 살걸 1위는 뭐임",
    "다들 집에 하나씩 있는 안 쓰는 가전\n나는 에어프라이어인데\n너네 집은 뭐임",
    "만원으로 하루 행복해질 수 있는 방법\n하나씩만 알려줘\n내껀 편의점 신상 털기",
    "이사할 때 제일 버리기 아까운 거 1위\n난 안 읽은 책들인데\n다들 뭐 못 버림?",
    "요즘 국룰 살림템 뭐 있음?\n나만 모르는 거 있을까봐 불안함",
    "배달 시킬 때 최소주문금액 맞추려고\n괜히 하나 더 담는 사람\n나만 그런 거 아니지",
    # 공감·하소연
    "자기 전에 제일 하기 싫은 일 1위\n1. 설거지\n2. 빨래 개기\n3. 내일 생각하기\n\n난 3번",
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
    # 질문 던지기 (추가)
    "다들 냉장고에 몇 년째 자리만 지키는 소스 있음?\n나는 굴소스\n샀는데 두 번 씀",
    "집에서 제일 자주 잃어버리는 물건 1위\n난 손톱깎이\n어디 숨는 건지 진짜 미스터리",
    "택배 뜯고 나서 그 상자\n바로 버리는 사람 vs 일단 쟁여두는 사람\n난 후자라 베란다가 상자 창고",
    "무선 이어폰 한쪽만 잃어버려본 사람\n손 들어\n나는 지금 왼쪽만 있음",
    "다들 '나중에 쓰겠지' 하고 모아둔 거 뭐 있음?\n난 쇼핑백\n서랍 한 칸이 쇼핑백임",
    "충전기 케이블 몇 개나 있음?\n난 다섯 갠데 멀쩡한 건 두 개\n나머지는 왜 못 버리는지 모름",
    # 공감·하소연 (추가)
    "분리수거하려고 라벨 떼는데\n안 떨어지는 거 만나면\n그날 하루 기분 상함",
    "새로 산 옷 태그 안 뗀 채로\n옷장에 3주째 걸려있음\n입긴 할 건데 언젠가",
    "영양제 사놓고 3일 먹고 까먹는 거\n나만 그런 거 아니지\n지금 유통기한 지난 거 두 통 있음",
    "'딱 하나만 보고 자야지' 하고 켠 영상\n정신 차리니 새벽 2시\n알고리즘한테 진 거임",
    "설거지 다 했다 싶으면\n꼭 싱크대 뒤에서 컵 하나 더 나옴\n끝이 없는 게임",
    "장 보러 갔다가\n원래 사려던 건 까먹고\n딴 거만 잔뜩 사옴",
    "옷은 많은데 입을 게 없는 이 현상\n과학적으로 설명 좀\n옷장은 꽉 찼는데",
    # 살림팁 (추가)
    "창틀 먼지\n마른 붓으로 쓸어 모은 다음 물티슈\n물부터 대면 진흙됨",
    "칼 잘 안 들 때\n도자기 컵 바닥(유약 없는 부분)에 몇 번 갈면 살아남\n숫돌 없어도 됨",
    "수건 빨아도 뻣뻣하면\n식초 조금 넣고 헹굼\n섬유유연제보다 이게 나음",
    "은수저 검게 변한 거\n알루미늄 포일 깔고 소금+뜨거운 물\n1분이면 반짝임",
    "행주 삶기 귀찮으면\n젖은 채로 전자레인지 2분\n웬만한 세균 잡힘",
    "스티커 자국 안 지워질 때\n드라이기로 데운 뒤 떼면 쭉 벗겨짐\n손톱으로 긁지 마",
    # 가벼운 TMI (추가)
    "오늘 목표: 아무것도 안 하기\n달성률 100%\n뿌듯함",
    "라면 끓일 때 계란 넣는 타이밍으로\n싸울 수 있는 사이\n나는 마지막에 톡 파임",
    "이불 밖은 위험하다는 말\n겨울에만 맞는 줄 알았는데\n에어컨 튼 여름에도 맞음",
    "배달 앱 켜서 30분 고민하다\n결국 어제 먹은 거 또 시킴\n선택지가 많으면 못 고르는 인간",
    "몰아서 쉬려고 했는데\n누워있다 보니 하루가 다 갔다\n시간 도둑맞음",
    # ── 담백한 기록 ──
    # 질문도 펀치라인도 없이 있었던 일만 적고 끝낸다. 위 묶음들이 전부
    # 반응을 노린 구조라, 그것만 계속 나가면 사람이 쓴 것 같지 않아진다.
    "베란다에 널어둔 빨래가 아직 안 말랐다\n오늘 안에는 글렀네",
    "택배가 문 앞에 와 있는데\n뭘 시켰는지 기억이 안 난다",
    "커피 내리려다 원두 떨어진 걸 알았다\n오늘은 그냥 물",
    "청소기 돌리다 콘센트가 뽑혀서\n두 번 꽂았다",
    "빨래 개면서 예능 틀어놨는데\n빨래는 그대로고 예능만 다 봤다",
    "창문 열어두니까 바람이 좀 들어온다\n이제 좀 살 것 같다",
    "라면에 계란 넣으려다\n마지막 하나라 그냥 뒀다",
    "형광등 하나가 나갔는데 아직 안 갈았다\n어두운 채로 이틀째",
    "설거지 미뤄뒀다가 자기 전에 다 했다\n개운하긴 하다",
    "장 보러 나가려다 비 오는 거 보고\n그냥 들어왔다",
    "이불 빨래를 돌렸는데\n건조대에 자리가 없다\n생각이 짧았다",
    "저녁 뭐 먹을지 30분 고민하다\n결국 김치볶음밥",
    "책상 정리하다 영수증 뭉치가 나와서\n버리는 데만 십 분 걸렸다",
    "밤에 물 마시러 나왔다가\n불 켜기 귀찮아서 더듬어서 갔다",
    "화분에 물 주는 걸 사흘 잊었는데\n아직 살아있다",
    "가스레인지 위에 냄비 올려두고\n다른 방에서 딴짓하다 태울 뻔했다",
]

# ── 오후 정보글 (링크 없음) : 저장 유도용 ───────────────
# "저장해두고 싶은" 실용 정보. 사실 확실한 것만.
# 짧은 사용 장면과 체감 효과를 함께 적어 정보 목록처럼 딱딱해 보이지 않게 한다.
# 전부 질문으로 끝내면 패턴이 생기므로 담백한 관찰·자조를 섞는다.
TIPS = [
    # 2026-09-05 전면 교체. 기존 37개는 이미 한 바퀴 돌아 재게시하지 않는다.
    # 정책·의학처럼 바뀌거나 검증이 필요한 내용은 빼고, 오래 써도 안전한 생활 팁만 둔다.
    "사진첩에 스크린샷 쌓이는 사람\n필요한 것만 즐겨찾기 해두고 나머지는 월말에 한 번 정리\n\n막상 찾으려면 사진보다 캡처가 더 많더라",
    "브라우저 탭 30개씩 열어두면\n나중에 볼 건 읽기 목록에 넣고 탭은 닫기\n\n안 닫으면 결국 어느 것도 안 봄",
    "메일함 정리할 때 하나씩 지우지 말고\n보낸 사람 이름으로 검색해서 광고 메일을 묶어서 정리\n\n십 분이면 숫자가 확 줄어듦",
    "비밀번호를 메모장에 적어두는 대신\n기기 기본 비밀번호 관리자를 쓰면 자동완성까지 됨\n\n사이트마다 다르게 만드는 게 핵심",
    "2단계 인증 켰으면 복구 코드도 챙겨두기\n휴대폰 잃어버렸을 때 마지막 탈출구임\n\n사진첩 말고 잠금되는 곳에 보관",
    "휴대폰 분실 찾기 기능\n잃어버린 뒤 켜는 건 늦으니까 설정에서 지금 한 번 확인\n\n막상 필요할 때 꺼져 있으면 진짜 막막함",
    "여행 전에 지도에서 숙소 주변을 오프라인 저장\n데이터 안 터져도 길은 찾을 수 있음\n\n낯선 곳 도착 첫날에 특히 유용함",
    "파일 이름을 '최종 진짜최종'로 만들지 말고\n날짜_내용 순서로 저장\n예: 0905_견적서\n\n나중에 정렬하면 바로 보임",
    "다운로드 폴더는 일주일에 한 번만 비워도\n필요한 파일 찾는 시간이 확 줄어듦\n\n내 컴퓨터에서 제일 빨리 어질러지는 방임",
    "종이 문서 급하게 보낼 때\n그냥 사진 찍지 말고 휴대폰 문서 스캔 기능 쓰기\n\n그림자랑 기울기 자동으로 잡혀서 훨씬 깔끔함",
    "매달 반복되는 납부일이나 점검일\n기억하려 하지 말고 달력에 반복 일정으로 한 번만 등록\n\n기억력보다 알림이 믿을 만함",
    "앱 알림이 너무 많으면 전부 끄지 말고\n결제·배송·사람이 보낸 메시지만 남기기\n\n중요한 알림이 광고 사이에 묻히는 게 문제",
    "비슷하게 생긴 충전선이 많으면\n작은 스티커에 기기 이름 써서 양쪽 끝에 붙이기\n\n서랍 뒤지는 시간이 생각보다 많이 줄어듦",
    "자주 쓰는 문장이나 주소는\n휴대폰 단축어에 짧은 글자로 등록해두기\n\n매번 똑같은 걸 다시 치고 있었다면 추천",
    "공유받은 중요한 링크는 채팅방에만 두지 말고\n북마크 폴더 하나 만들어 바로 저장\n\n대화 검색으로 찾는 건 갈수록 어려워짐",
    "냉장고 안에 뭐가 있는지 자꾸 잊으면\n장보기 전에 문 열고 사진 한 장\n\n마트에서 같은 소스 또 사는 일 줄어듦",
    "냉동실은 종류별로 칸만 나눠도 편함\n고기·간편식·얼린 재료처럼 세 구역이면 충분\n\n봉투 뒤집다가 손 시릴 일이 줄어듦",
    "물건 하나 사면 비슷한 것 하나 내보내기\n옷이나 컵처럼 계속 늘어나는 물건에 특히 잘 먹힘\n\n수납장을 더 사는 것보다 먼저 할 일",
    "버릴지 고민되는 물건은 바로 결정하지 말고\n상자 하나에 모아 날짜 적어두기\n한 달간 안 찾으면 보내기 쉬워짐",
    "건전지는 새것과 쓴 것을 같은 통에 넣지 않기\n통 두 개만 나눠도 매번 잔량 확인할 필요가 없음\n\n왜 진작 안 나눴나 싶었음",
    "가전 설명서는 전부 보관하지 말고\n모델명 보이게 사진 찍어서 폴더에 저장\n\n필요할 땐 모델명 검색이 더 빠름",
    "집에 있는 가전 모델명과 구입일\n한 문서에 적어두면 수리 문의할 때 편함\n\n고장 난 뒤 제품 뒤집어보는 일 없어짐",
    "이사 상자에 내용물을 위에만 쓰지 말고\n옆면 두 군데에도 적기\n\n쌓아두면 위쪽 글씨는 하나도 안 보임",
    "침구 세트는 베갯잇 안에 같이 넣어두기\n시트랑 이불 커버가 흩어지지 않음\n\n호텔식 정리보다 이게 현실적으로 편함",
    "여행 짐 목록은 여행 끝나고 수정하기\n안 쓴 건 빼고 놓고 간 건 추가\n\n다음 여행 준비가 점점 빨라짐",
    "케이블 정리는 예쁘게 숨기는 것보다\n어느 기기 선인지 표시하는 게 먼저\n\n뽑아도 되는 선 찾다가 결국 다 뽑게 됨",
    "유통기한을 자주 놓치는 물건은\n포장에 적힌 날짜를 달력에 미리 등록\n\n서랍 안에 넣는 순간 존재도 같이 잊어버림",
    "보증서와 중요한 영수증은 한 봉투에 모으고\n봉투 겉에 품목만 적어두기\n\n고장 났을 때 집 전체를 뒤질 필요가 없음",
    "청소용품을 장소마다 흩어두기보다\n작은 바구니 하나에 기본 도구만 모아두기\n\n청소 시작 전 준비부터 지치는 걸 막아줌",
    "가구 사기 전에 놓을 자리를 사진 찍고\n사진 위에 가로·세로 치수 적어두기\n\n매장에서 줄자 찾을 일이 없어짐",
    "온라인으로 생필품 살 때 총가격보다\n100g·1개당 가격을 같이 보기\n\n대용량이라고 항상 싼 건 아니더라",
    "사고 싶은 물건은 장바구니에 하루만 두기\n다음 날에도 필요하면 사고 아니면 지우기\n\n밤에 담은 물건은 아침에 보면 절반이 필요 없음",
    "구독 결제일을 달력 한곳에 모아두면\n결제된 뒤 알아차리는 일을 줄일 수 있음\n\n무료 체험도 시작할 때 종료 알림부터 등록",
    "무료배송 금액 맞추려고 안 필요한 걸 담으면\n배송비보다 더 쓰는 경우가 많음\n\n결제 전에 추가한 물건 가격만 다시 보기",
    "가격 비교할 때 할인율보다 최종 결제금액 보기\n쿠폰 조건이 다르면 할인율 숫자는 별 의미 없음\n\n큰 퍼센트에 먼저 눈이 가는 게 함정",
    "반품할 가능성이 있는 물건은\n포장 뜯기 전에 반품 조건과 구성품부터 확인\n\n상자 버리고 나서 찾으면 꼭 하나씩 빠져 있음",
    "계좌이체할 때 메모에 용도 적어두기\n몇 달 뒤 거래내역만 봐도 바로 기억남\n\n숫자만 남으면 진짜 아무 생각도 안 남",
    "영수증 사진은 품목_날짜로 이름 바꿔두기\n사진첩에만 두면 필요할 때 못 찾음\n\nAS용은 따로 폴더까지 만들면 끝",
    "장보기 목록은 물건 이름만 쓰지 말고\n냉장·냉동·생활용품 순으로 묶기\n\n매장을 되돌아가는 횟수가 줄어듦",
    "묶음 상품 살 때 보관 공간부터 확인\n싸게 샀는데 둘 곳이 없으면 집이 창고가 됨\n\n특히 휴지랑 생수는 부피가 가격보다 큼",
    "여행 예약 확인서는 출발 전에 캡처해두기\n앱 로그인이 풀려도 예약번호는 바로 꺼낼 수 있음\n\n인터넷 안 되는 순간은 꼭 급할 때 옴",
    "짐 부치기 전에 캐리어 겉모습 사진 한 장\n비슷한 가방 설명할 때 말보다 사진이 빠름\n\n특징 없는 검은 캐리어면 더 필요함",
    "여행용 충전기는 작은 파우치 하나에 몰아넣기\n숙소 바뀔 때 콘센트마다 두고 오는 걸 막아줌\n\n마지막 날엔 파우치가 찼는지만 확인",
    "해외 숙소 주소는 현지어 화면도 저장해두기\n기사님에게 보여줄 때 영문 주소보다 빠를 때가 많음\n\n도착해서 번역기 찾으면 늦음",
    "여행 일정은 이동시간 뒤에 여유 칸 하나 두기\n한 곳만 늦어져도 하루 전체가 밀리는 걸 막아줌\n\n빈 시간도 일정의 일부임",
    "가고 싶은 식당은 이름만 메모하지 말고\n지도에 저장하면서 휴무일도 같이 적기\n\n도착해서 문 닫힌 걸 보면 힘 빠짐",
    "여행 전날 새 물건을 처음 쓰지 말기\n신발·가방·충전기는 미리 한 번 써봐야 문제를 찾음\n\n여행지에서 사용법 찾는 건 꽤 귀찮음",
    "숙소를 옮기는 여행이면 짐을 날짜별보다\n매일 쓰는 것과 가끔 쓰는 것으로 나누기\n\n매번 캐리어 전체를 풀지 않아도 됨",
    "우산은 젖은 채 접어두지 말고 집에 오자마자 펼치기\n다 마른 뒤 접어야 냄새가 덜 남음\n\n현관 구석에 세워두면 그대로 잊음",
    "내일 할 일은 길게 적지 말고 중요한 세 개만\n나머지는 여유가 생기면 하는 목록으로 분리\n\n열 개 적고 두 개 하는 것보다 마음이 편함",
    "회의가 끝나면 내용 요약보다\n누가 무엇을 언제까지 할지만 먼저 적기\n\n좋은 얘기 많이 해도 다음 행동이 없으면 그대로임",
    "파일에 v2_final 대신 날짜를 붙이기\n수정본이 여러 개 생겨도 최신 파일을 찾기 쉬움\n\n진짜최종_최종2에서 벗어나는 방법",
    "반복해서 만드는 문서는 빈 양식으로 하나 저장\n다음번엔 복사해서 내용만 바꾸기\n\n매달 같은 표를 처음부터 만들고 있었다면 추천",
    "자료 조사할 때 문장만 복사하지 말고\n출처 링크를 바로 아래 같이 저장\n\n나중에 어디서 봤는지 찾는 시간이 더 오래 걸림",
    "떠오른 생각은 여러 앱에 흩어 적지 말고\n일단 한 메모함에만 넣기\n\n정리는 나중 문제고 잃어버리지 않는 게 먼저",
    "집중할 때 휴대폰을 뒤집어두는 것보다\n손이 닿지 않는 곳에 두는 게 확실함\n\n화면이 안 보여도 진동 한 번이면 끝남",
    "해야 할 일이 막막하면 완료가 아니라\n시작 동작만 적기\n예: 보고서 쓰기 대신 파일 열기\n\n첫 칸이 작으면 움직이기 쉬움",
    "일주일에 한 번은 백업 파일을 실제로 열어보기\n저장됐다고 떠도 복구가 되는지는 다른 문제임\n\n백업은 열릴 때까지가 백업",
    "업데이트를 계속 미룬 기기는\n중요한 작업 없는 날 하나 정해서 재시작까지 하기\n\n급할 때 자동 업데이트 걸리는 게 제일 곤란함",
    "마감일만 적지 말고 시작 알림도 따로 만들기\n마감 당일 알림은 알려주는 게 아니라 재촉하는 수준\n\n며칠 전 알림 하나가 훨씬 쓸모 있음",
    "먼지 닦을 때 아래부터 하면 두 번 일함\n선반 위에서 아래로 내려오고 마지막에 바닥\n\n청소도 순서가 있더라",
    "청소용 천은 용도별로 색을 다르게 정하기\n주방·욕실이 섞이지 않고 찾기도 쉬움\n\n글씨로 표시하는 것보다 한눈에 보임",
    "청소기 필터를 씻었다면 완전히 말린 뒤 끼우기\n겉만 말라 보여도 안쪽은 축축할 수 있음\n\n급하면 여분 필터 하나가 편함",
    "옷 세탁표시가 흐려질 것 같으면 새 옷일 때 사진\n나중에 건조기 넣어도 되는지 바로 확인 가능\n\n택 떼고 나면 제일 먼저 잊는 정보임",
    "얼룩 제거제를 처음 쓰는 옷은\n눈에 안 띄는 안쪽에 먼저 시험하기\n\n얼룩보다 탈색 자국이 더 눈에 띌 수 있음",
    "계절용품은 완전히 말린 다음 보관하기\n조금 남은 습기가 몇 달 뒤 냄새로 돌아옴\n\n보관함 닫기 전에 한 번 더 확인",
    "주방 수세미 교체일을 기억하기 어렵다면\n새 수세미 꺼낸 날을 달력에 적기\n\n색만 보고는 얼마나 썼는지 모르겠더라",
    "개봉한 소스나 식재료는 뚜껑에 날짜 적기\n유통기한보다 언제 열었는지가 더 궁금할 때가 많음\n\n냉장고 속 추리게임 줄이는 법",
    "분리배출 기준은 지역마다 다를 수 있으니\n헷갈리는 건 관리실이나 지자체 안내를 한 번 확인\n\n인터넷에서 본 한 줄보다 우리 동네 기준이 정확함",
    "청소 시작 전에 타이머 10분만 맞추기\n끝까지 다 하려 하면 시작도 못 하는 날이 있음\n\n열 분 지나면 생각보다 많이 치워져 있음",
    "자주 잃어버리는 물건은 잘 보이는 곳보다\n돌아오면 무조건 두는 한 자리를 정하기\n\n열쇠는 기억보다 자리가 찾아줌",
    "냉장고 문에 붙인 메모가 너무 많아지면\n이번 주에 필요한 것만 남기고 사진으로 보관\n\n메모도 많아지면 배경처럼 안 보이기 시작함",
    "종이 쇼핑백은 크기별로 하나씩만 남기고\n나머지는 바로 정리\n\n언젠가 쓸 것 같아서 모으면 서랍 하나가 금방 참",
    "새 물건을 들이면 포장재는 바로 버리지 말고\n정상 작동 확인할 때까지만 한곳에 보관\n\n며칠씩 집안에 흩어두는 것과는 다름",
    "외출 전 확인할 건 문 옆에 짧게 붙여두기\n지갑·열쇠·휴대폰 정도면 충분\n\n항목이 길어지면 결국 안 보게 됨",
]

# ── 특가 (화·목) : 사이트 특가 페이지로 보내는 글 ──────
# 예전에는 상품 하나를 골라 사진을 붙이고, 본문에는 상품과 무관한 혼잣말을
# 무작위로 얹었다. 그러다 보니 글과 제품이 겉돌아서 광고 티만 났다.
# 지금은 본문을 deals-data.js 실제 값(개수·최저가·카테고리·가격)으로 만든다.
# 사실만 쓰니 어긋날 일이 없고, 링크는 특가 페이지 하나로 보내 사이트도 같이 키운다.
def _won(n):
    return "{:,}원".format(int(n))


def _short(s, n=24):
    return s if len(s) <= n else s[:n] + "…"


def _line(d):
    return "· {} {}".format(_short(d["name"]), _won(d["price"]))

def choose(cands, guard=None):
    """후보 [(본문, 댓글|None, 이미지|None), ...] 에서 하나 고른다.

    - 오늘 이 슬롯 글이 이미 나갔으면 None → 아예 게시하지 않는다.
      (예약이 밀려 같은 슬롯이 두 번 돌아도 중복 발행되지 않게 하는 안전장치)
    - 최근에 이미 쓴 문구는 건너뛰고 다음 것을 고른다.
    - guard: 중복 검사에 쓸 후보 목록(기본은 cands 자신). 한 슬롯 안에서
      묶음을 갈아끼울 때, 다른 묶음으로 이미 나간 글까지 검사에 넣기 위한 것.
    """
    if not cands:
        return None
    if any(_norm(c[0]) in TODAY_TEXTS for c in (guard or cands)):
        print("오늘 이 슬롯 글은 이미 올라갔습니다 — 건너뜁니다.")
        return None
    start = kst.tm_yday % len(cands)
    for k in range(len(cands)):
        c = cands[(start + k) % len(cands)]
        if _norm(c[0]) not in RECENT_TEXTS:
            return c
    print("후보가 전부 이미 쓰였습니다 — 반복 게시하지 않고 종료합니다.")
    return None

def load_deals():
    """deals-data.js 의 상품 목록 전체"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "deals-data.js")
    if not os.path.exists(path):
        return []
    m = re.search(r"const DEALS = (\[.*?\]);", open(path, encoding="utf-8").read(), re.S)
    if not m:
        return []
    return [d for d in json.loads(m.group(1)) if d.get("url")]


def deal_candidates():
    """오늘 특가 데이터로 만든 홍보글 후보. 본문에 쓰는 숫자·상품명은 전부 실제 값."""
    deals = load_deals()
    if not deals:
        return []
    rockets = [d for d in deals if d.get("rocket")] or deals
    by_price = sorted(rockets, key=lambda d: d["price"])
    cheap3 = by_price[:3]
    under20 = [d for d in by_price if d["price"] < 20000]

    # 문구에 맞는 가격대에서만 뽑는다. 아무거나 뽑으면
    # "장바구니 채우기 좋은" 자리에 63만원짜리 TV가 들어가는 식으로 어긋난다.
    budget = under20 or by_price                                        # 부담 없이 담는 가격
    mid = [d for d in by_price if 10000 <= d["price"] <= 80000] or by_price  # 하나만 짚어 말할 가격

    seed = week + kst.tm_yday  # 주차로 회전시켜 같은 상품이 매주 반복되지 않게

    def rot(lst, k, extra=0):
        if not lst:
            return []
        s = (seed + extra) % len(lst)
        return [lst[(s + i) % len(lst)] for i in range(min(k, len(lst)))]

    cats = {}
    for d in rockets:
        cats.setdefault(d.get("category") or "기타", []).append(d)
    multi = sorted(c for c, v in cats.items() if len(v) >= 2)

    # 글에 상품 두어 개만 적으면 "이게 전부"로 읽힌다. 전체가 몇 개인지 먼저 밝혀서
    # 오늘 올라온 골드박스 묶음 중 일부를 고른 거라는 게 드러나게 한다.
    total = len(deals)
    out = []
    out.append(("오늘 쿠팡 골드박스 {}개 올라왔는데\n제일 싼 게 {}\n\n{}".format(
        total, _won(by_price[0]["price"]),
        "\n".join(_line(d) for d in cheap3)), cheap3[0]))
    cart = rot(budget, 3, 2)  # 위 '제일 싼 것' 목록과 겹치지 않게 시작점을 밀어둔다
    if len(cart) == 3:
        out.append(("오늘 골드박스 {}개 중에\n장바구니 채우기 좋은 것만 추려봄\n\n{}".format(
            total, "\n".join(_line(d) for d in cart)), cart[0]))
    one = rot(mid, 1)
    if one:
        out.append(("오늘 올라온 골드박스 {}개 훑다가\n제일 눈에 밟힌 거\n\n{} {}\n로켓배송이라 금방 옴".format(
            total, _short(one[0]["name"], 30), _won(one[0]["price"])), one[0]))
    if len(under20) >= 3:
        u = rot(under20, 3, 5)
        out.append(("골드박스 {}개 중에 2만원 아래만 {}개\n그중 세 개만 적어둠\n\n{}\n\n장 볼 때 같이 담으면 됨".format(
            total, len(under20), "\n".join(_line(d) for d in u)), u[0]))
    if multi:
        cat = multi[seed % len(multi)]
        cl = sorted(cats[cat], key=lambda d: d["price"])[:3]
        out.append(("오늘 골드박스 {}개 중에\n{} 쪽만 {}개 있길래\n\n{}".format(
            total, cat, len(cats[cat]), "\n".join(_line(d) for d in cl)), cl[0]))

    reply = ("전체 목록은 여기\n👉 " + SITE + "deals.html\n\n"
             "쿠팡 파트너스 활동의 일환으로 수수료를 제공받습니다.")
    # 사진 속 상품은 본문에 이름이 나온 것으로 맞춘다
    return [(body + "\n\n#광고", reply, (d.get("image") or None)) for body, d in out]

def linked(pool):
    """(본문, 페이지, 댓글 앞머리) 목록 → 후보 형식으로"""
    return [(b, lead + "\n👉 " + SITE + page, None) for b, page, lead in pool]


# 주제 태그. 반응 좋은 계정들은 전부 달고 있는데 우리만 없어서 주제 피드·검색
# 노출 통로를 통째로 놓치고 있었다. (마침표·앰퍼샌드는 못 쓰고 50자 이내)
TOPIC = {
    "tips": "꿀팁",
    "daily": "살림",
    "fortune": "오늘의운세",
    "lotto": "로또",
    "deal": "가성비",
}


def build_text():
    """((본문, 첫 댓글, 이미지), 주제태그) 를 돌려준다. 올릴 게 없으면 (None, None)."""
    # 수동 실행 시 THREADS_FORCE_TYPE 로 콘텐츠 종류 지정 가능
    forced = os.environ.get("THREADS_FORCE_TYPE", "").strip().lower()
    wd = kst.tm_wday  # 0=월

    if forced == "tips":
        # 오후 정보글 (저장 유도용, 링크 없음)
        return choose([(t, None, None) for t in TIPS]), TOPIC["tips"]
    if forced == "daily":
        # 저녁 일상글 (도달 확보용, 링크 없음). 아침 슬롯은 여기로 오지 않는다.
        # 날씨 글은 사흘에 한 번꼴로만 — 매일 날씨 얘기면 그것도 결국 패턴이다.
        wx = [(t, None, None) for t in weather_daily()]
        base = [(t, None, None) for t in DAILY]
        pool = wx if (wx and kst.tm_yday % 3 == 0) else base
        return choose(pool, guard=wx + base), TOPIC["daily"]
    if forced == "fortune" or (not forced and wd in (0, 2, 4)):
        # 오늘 계산된 실제 순위를 쓴 티저를 앞에 두고, 일반 문구를 뒤에 붙인다
        return choose(linked(live_fortune() + FORTUNE)), TOPIC["fortune"]
    if forced == "lotto" or (not forced and wd == 5):
        return choose(linked(live_lotto() + LOTTO)), TOPIC["lotto"]

    # 화·목·일 (또는 forced == "deal") : 특가 페이지 홍보
    cands = deal_candidates()
    if not cands:
        return choose(linked(live_fortune() + FORTUNE)), TOPIC["fortune"]
    return choose(cands), TOPIC["deal"]


chosen, topic_tag = build_text()
if not chosen:
    print("올릴 글이 없어 종료합니다.")
    sys.exit(0)
text, reply_text, image_url = chosen

def api(path, params):
    data = urllib.parse.urlencode(dict(params, access_token=TOKEN)).encode()
    req = urllib.request.Request("https://graph.threads.net/v1.0/" + path, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def publish(txt, reply_to=None, image=None, topic=None):
    params = {"text": txt}
    if image:
        params["media_type"] = "IMAGE"
        params["image_url"] = image
    else:
        params["media_type"] = "TEXT"
    if reply_to:
        params["reply_to_id"] = reply_to
    elif topic:
        params["topic_tag"] = topic  # 주제는 본문에만 (댓글에는 안 붙는다)
    c = api(USER_ID + "/threads", params)
    time.sleep(3 if not image else 6)  # 이미지는 처리 시간이 더 필요
    return api(USER_ID + "/threads_publish", {"creation_id": c["id"]})

# 사진이나 주제 태그가 거부당해도 본문은 반드시 나가야 한다.
# 조건을 하나씩 떼면서 다시 시도한다.
def publish_main():
    tries = []
    if image_url:
        tries.append(("사진+주제", {"image": image_url, "topic": topic_tag}))
        tries.append(("사진만", {"image": image_url}))
    tries.append(("주제만", {"topic": topic_tag}))
    tries.append(("본문만", {}))
    last = None
    for label, kw in tries:
        try:
            r = publish(text, **kw)
            print("게시 성공 ({})".format(label))
            return r
        except Exception as e:
            print("게시 실패 ({}): {}".format(label, e))
            last = e
    raise last


try:
    result = publish_main()
    post_id = result.get("id")
    print("스레드 포스팅 성공:", post_id)
    print("--- 본문 ---")
    print(text)

    # 링크는 본문이 아니라 첫 댓글로 (본문에 외부 링크가 있으면 노출이 줄어드는 편)
    # 본문 직후에는 답글이 실패하는 경우가 있어 간격을 두고 세 번까지 시도한다.
    if reply_text and post_id:
        for attempt in range(1, 4):
            try:
                rep = publish(reply_text, reply_to=post_id)
                print("첫 댓글 작성 성공:", rep.get("id"))
                print("--- 댓글 ---")
                print(reply_text)
                break
            except Exception as e:
                print("첫 댓글 작성 실패 ({}/3): {}".format(attempt, e))
                if attempt < 3:
                    time.sleep(15)
        else:
            print("첫 댓글을 끝내 못 달았습니다 (본문은 정상 게시됨).")
except Exception as e:
    print("스레드 포스팅 실패:", e)
    sys.exit(0)
