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
def fetch_recent(limit=50):
    url = ("https://graph.threads.net/v1.0/" + USER_ID + "/threads"
           "?fields=text,timestamp&limit=" + str(limit) +
           "&access_token=" + urllib.parse.quote(TOKEN))
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode()).get("data", [])


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
    "주말에 몰아서 쉬려고 했는데\n누워있다 보니 벌써 일요일 저녁\n시간 도둑맞음",
]

# ── 오후 정보글 (링크 없음) : 저장 유도용 ───────────────
# "저장해두고 싶은" 실용 정보. 사실 확실한 것만.
# 정보만 툭 던지던 때는 반응이 0이었다. 잘 되는 계정들을 보니 정보를 주는 글보다
# 물어보는 글이 훨씬 컸다. 그래서 끝에 한 줄씩 붙였는데, 전부 질문으로 끝내면
# 그것대로 틀에 박혀 보여서 질문·자조·툭 던지는 말을 섞어 하나씩 따로 썼다.
TIPS = [
    "택배 상자 버릴 때 송장 그냥 떼지 말고\n네임펜으로 개인정보만 쓱 긋기\n요즘 이거로 정보 털리는 사람 많음\n\n다들 그냥 뜯어서 버리지?\n나도 얼마 전까지 그랬음",
    "카드 포인트 통합조회\n'카드포인트 통합조회' 검색 → 여러 카드 흩어진 포인트 한 번에 현금화 가능\n평균 몇만 원씩 잠자고 있음\n\n해본 사람 얼마 나왔는지 궁금하네",
    "냉동실 음식 언제 넣었는지 모르겠으면\n마스킹테이프에 날짜 적어 붙이기\n'냉동실 미라' 만들지 않는 유일한 방법\n\n우리 집 냉동실엔 정체불명이 아직 있음\n다들 하나씩 있지 않음?",
    "영수증 잉크는 열에 지워짐\n중요한 영수증은 사진 찍어두기\n환불·AS 때 원본 요구하면 곤란해짐\n\n지워진 영수증 들고 가본 적 있는데\n그날 진짜 허탈했음",
    "세탁기 통세척\n한 달에 한 번 빈 통에 과탄산소다 넣고 삶음 코스\n안 하면 빨래에서 냄새 나는 이유가 이거\n\n마지막으로 한 게 언제인지 기억 안 나면\n지금이 그때임",
    "핸드폰 약정 끝났는데 그대로 쓰는 사람\n'선택약정 25% 할인' 신청하면 매달 요금 깎임\n통신사가 먼저 안 알려줌\n\n이거 모르고 몇 년 그냥 낸 사람 손\n나임",
    "실리콘 주방용품 기름때\n식용유 살짝 묻혀 닦고 세척하면 미끌거림 사라짐\n기름은 기름으로\n\n알기 전엔 세제로만 박박 문질렀음",
    "안 쓰는 앱 구독 정리\n아이폰: 설정→내 이름→구독 / 안드로이드: 플레이스토어→결제\n생각보다 새고 있는 돈 많음\n\n지금 열어보면 하나쯤 나올걸\n난 두 개 나왔음",
    "가스레인지 기름때 굳은 거\n베이킹소다+물 반죽 발라 10분 뒤 닦기\n박박 문질러도 안 되던 게 그냥 밀림\n\n손목 나가기 전에 알았으면 좋았을 것",
    "정부24에서 '숨은 환급금' 조회\n미환급 세금·보험료 한 번에 확인됨\n안 찾아가면 그냥 사라지는 돈\n\n0원 나와도 손해는 아니니까 한 번씩 해보길",
    "옷에 볼펜 자국\n손소독제(알코올) 살짝 묻혀 두드리면 빠짐\n문지르지 말고 두드리기\n\n문지르면 더 번짐\n이거 모르고 옷 한 벌 버렸음",
    "가전 살 때 '으뜸효율 환급'\n에너지효율 1등급 사면 최대 10% 돌려받음 (예산 소진 전까지)\n영수증 챙겨두기\n\n큰 거 살 때 이거 안 챙기면 좀 아깝잖아",
    "배수구 냄새\n식초 붓고 5분 뒤 뜨거운 물\n뚫어뻥 사기 전에 이것부터\n\n여름엔 이거 안 하면 답이 없더라",
    "안경 김서림\n렌즈 안쪽에 주방세제 한 방울 문지르고 닦기\n마스크 쓸 때 효과 좋음\n\n안경 쓰는 사람만 아는 고통 있잖아",
    "전기요금 복지할인\n다자녀·출산·장애·기초수급이면 한전 고객센터(123) 또는 한전ON에서 신청\n매달 요금 감면\n\n해당되는데 모르고 안 받는 집이 꽤 됨\n주변에 있으면 알려주면 좋을 듯",
    # ── 돈 아끼는 정보 (경로까지) ──
    "미환급금 조회\n'정부24' 앱 → '숨은 환급금 찾기' 검색\n지방세·보험료·통신비 미환급 한 번에 뜸, 신청 버튼까지 그 자리에서\n\n이런 거 찾아본 사람 있음?",
    "국민연금·건강보험 과오납\n'내 곁에 국민연금' 앱 또는 건강보험공단(1577-1000)에서 조회\n더 낸 돈 돌려받는 거라 눈치 볼 필요 없음",
    "휴면예금 찾기\n'파인(fine.fss.or.kr)' 접속 → 잠자는 내 돈 찾기\n안 쓴 통장·보험·카드포인트까지 한 번에 조회됨\n\n학생 때 만든 통장 기억나면 특히 해볼 만함",
    "실비보험 청구, 병원 안 가도 됨\n'실손24' 앱이나 보험사 앱에서 진료비 영수증 사진으로 청구\n소액이라 귀찮아서 안 하는 돈이 제일 아까움\n\n귀찮아서 그냥 넘긴 거 다들 있지",
    "자동차세 연납\n1월에 한 번에 내면 약 5% 할인 (위택스 또는 이택스에서 신청)\n어차피 낼 돈, 미리 내고 깎는 방식\n\n1월에 알림 오면 그냥 넘기지 말길",
    "청년 지원금 한눈에\n'온통청년(youthcenter.go.kr)'에서 내 나이·지역 맞는 지원사업 검색\n주거·취업·금융 지원 생각보다 많음\n\n해당 나이면 한 번 훑어볼 만함",
    "카드 연회비 아끼기\n안 쓰는 카드는 '해지' 말고 '단순 정지'\n연회비 안 나가고 실적·등급은 유지됨\n\n해지하면 실적 날아가는 거 모르는 사람 많더라",
    "통신비 미환급\n번호이동·해지 때 남은 요금 환급 안 받은 거\n통신사 고객센터에서 '미환급액' 조회하면 나옴\n\n번호이동 해본 적 있으면 한 번 확인해보길",
    # ── 생활 실용 (경로까지) ──
    "택배 파손·분실\n택배사 말고 물건 산 '쇼핑몰 고객센터'로\n판매자 책임이라 이쪽이 훨씬 빠름\n\n택배사에 전화 돌리다 하루 날린 적 있음",
    "인터넷 최저가 진짜 찾기\n네이버쇼핑 말고 '다나와'에서 검색 → 카드할인가까지 비교\n같은 물건 몇천 원씩 차이 남\n\n나중에 더 싼 거 보면 좀 억울하잖아",
    "무료 폰트 쓸 때\n'눈누(noonnu.cc)'에서 상업용 무료만 모아서 다운\n아무거나 쓰면 저작권 문제 생김",
    "약 복용시간 헷갈릴 때\n약 봉투 사진 찍어 '약학정보원' 검색하면 성분·주의사항 다 나옴\n중복 복용 막을 수 있음\n\n약 봉투 바로 버리지 말고 찍어두는 게 편함",
    "전세·월세 계약 전\n'등기부등본'은 '인터넷등기소'에서 700원이면 뗌\n집주인 말 믿지 말고 이거부터 확인\n\n700원 아끼려다 보증금 날리는 게 더 무섭지",
    "중고거래 사기 확인\n'더치트(thecheat.co.kr)'에 상대 계좌·번호 검색\n신고 이력 있으면 거르기\n\n거래 전에 1분이면 됨",
    "여권 갱신 미리\n만료 6개월 전부터 갱신 가능, 잔여기간 6개월 미만이면 입국 거부되는 나라 많음\n\n출국 직전에 알면 이미 늦음",
    # ── 살림 실용 (추가) ──
    "도마 소독\n굵은소금 뿌리고 레몬으로 문지른 뒤 헹굼\n칼자국 사이 세균까지 잡힘\n\n칼자국 사이는 세제로 안 되더라",
    "유리컵 얼룩\n식초물에 10분 담갔다 닦으면 반짝임\n물때는 산으로 녹임\n\n물때는 아무리 문질러도 안 지워지잖아",
    "옷 보풀\n일회용 면도기로 살살 밀면 제거됨\n보풀제거기 없어도 됨\n\n보풀제거기 사놓고 안 쓰는 사람 나임",
    "김치통 냄새\n쌀뜨물 채워 하루 두면 배인 냄새 빠짐\n김치통은 이거 아니면 답 없음\n\n김치통 냄새는 진짜 못 잡는 줄 알았음",
    "프라이팬 코팅 오래 쓰려면\n센 불에 빈 팬 예열 금지, 금속 도구 금지\n이 두 개만 지켜도 훨씬 오래 감\n\n코팅 팬 1년마다 버리는 사람 주목",
    "곰팡이 실리콘\n휴지에 락스 적셔 30분 덮어두고 떼기\n뿌리기만 하면 흘러내려서 효과 없음\n\n락스 뿌려도 왜 안 되나 했는데 이유가 이거였음",
    "냄비 눌어붙은 거\n물+베이킹소다 넣고 5분 끓이면 스르륵 떨어짐\n\n박박 긁으면 코팅만 나감",
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

def choose(cands):
    """후보 [(본문, 댓글|None, 이미지|None), ...] 에서 하나 고른다.

    - 오늘 이 슬롯 글이 이미 나갔으면 None → 아예 게시하지 않는다.
      (예약이 밀려 같은 슬롯이 두 번 돌아도 중복 발행되지 않게 하는 안전장치)
    - 최근에 이미 쓴 문구는 건너뛰고 다음 것을 고른다.
    """
    if not cands:
        return None
    if any(_norm(c[0]) in TODAY_TEXTS for c in cands):
        print("오늘 이 슬롯 글은 이미 올라갔습니다 — 건너뜁니다.")
        return None
    start = kst.tm_yday % len(cands)
    for k in range(len(cands)):
        c = cands[(start + k) % len(cands)]
        if _norm(c[0]) not in RECENT_TEXTS:
            return c
    print("후보가 전부 최근에 쓰였습니다 — 순번대로 재사용합니다.")
    return cands[start]

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

    out = []
    out.append(("오늘 로켓배송 특가 {}개 올라옴\n제일 싼 게 {}\n\n{}".format(
        len(rockets), _won(by_price[0]["price"]),
        "\n".join(_line(d) for d in cheap3)), cheap3[0]))
    cart = rot(budget, 3, 2)  # 위 '제일 싼 것' 목록과 겹치지 않게 시작점을 밀어둔다
    if len(cart) == 3:
        out.append(("장바구니 채우기 좋은 것들만 추려봄\n\n{}".format(
            "\n".join(_line(d) for d in cart)), cart[0]))
    one = rot(mid, 1)
    if one:
        out.append(("오늘 특가 중에 제일 눈에 밟힌 거\n{} {}\n로켓배송이라 금방 옴".format(
            _short(one[0]["name"], 30), _won(one[0]["price"])), one[0]))
    if len(under20) >= 3:
        u = rot(under20, 3, 5)
        out.append(("2만원 아래로만 {}개 있길래 모아둠\n\n{}\n\n장 볼 때 같이 담으면 됨".format(
            len(under20), "\n".join(_line(d) for d in u)), u[0]))
    if multi:
        cat = multi[seed % len(multi)]
        cl = sorted(cats[cat], key=lambda d: d["price"])[:3]
        out.append(("오늘 {} 쪽만 {}개 떴는데\n\n{}".format(
            cat, len(cats[cat]), "\n".join(_line(d) for d in cl)), cl[0]))

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
        return choose([(t, None, None) for t in DAILY]), TOPIC["daily"]
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
