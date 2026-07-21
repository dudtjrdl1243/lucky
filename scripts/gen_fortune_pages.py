# -*- coding: utf-8 -*-
"""띠별 12 + 별자리 12 개별 페이지 생성기 → C:\\Users\\user\\Desktop\\lucky\\"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dudtjrdl1243.github.io/lucky/"

TTI = [
    # slug, 이름, 이모지, 특성 소개, 궁합(잘맞는띠), 주의띠, 키워드3
    ("rat", "쥐띠", "🐭", "쥐띠는 12간지의 첫 자리를 차지할 만큼 영리하고 눈치가 빠른 띠예요. 상황 판단이 빠르고 재물을 모으는 감각이 타고나서, 어디서든 실속을 챙기는 생활의 달인으로 통합니다. 다만 신중함이 지나쳐 좋은 기회 앞에서 망설이기도 해요.", "용띠 · 원숭이띠", "말띠", ["영리함", "재물감각", "순발력"]),
    ("ox", "소띠", "🐮", "소띠는 성실과 끈기의 대명사예요. 묵묵히 자기 길을 가는 뚝심이 있어 주변의 신뢰를 얻고, 한 번 시작한 일은 끝을 보는 책임감으로 큰 성취를 이룹니다. 속도는 느려 보여도 결국 가장 멀리 가는 띠라는 말이 있죠.", "뱀띠 · 닭띠", "양띠", ["성실", "끈기", "신용"]),
    ("tiger", "호랑이띠", "🐯", "호랑이띠는 타고난 리더예요. 용맹하고 추진력이 강해 남들이 주저할 때 앞장서고, 정의감이 강해 불의를 보면 참지 못합니다. 카리스마 넘치는 만큼 욱하는 성미만 다스리면 큰 그릇이 됩니다.", "말띠 · 개띠", "원숭이띠", ["리더십", "용맹", "추진력"]),
    ("rabbit", "토끼띠", "🐰", "토끼띠는 온화하고 섬세한 평화주의자예요. 사람의 마음을 잘 읽어 인간관계가 부드럽고, 감각이 좋아 예술이나 스타일 분야에서 빛을 냅니다. 갈등을 싫어해 속마음을 숨기는 경향은 살짝 주의할 점이에요.", "양띠 · 돼지띠", "닭띠", ["온화함", "섬세함", "인복"]),
    ("dragon", "용띠", "🐲", "용띠는 12간지 중 유일한 상상의 동물답게 스케일이 커요. 야망과 카리스마를 타고나 큰 무대에서 능력을 발휘하고, 어려운 상황에서도 당당함을 잃지 않습니다. 자존심이 강한 만큼 주변의 조언에 귀 기울이면 금상첨화예요.", "쥐띠 · 원숭이띠", "개띠", ["카리스마", "야망", "당당함"]),
    ("snake", "뱀띠", "🐍", "뱀띠는 지혜와 직관의 띠예요. 겉으로 드러내지 않지만 속으로 깊이 생각하고, 핵심을 꿰뚫는 통찰력으로 중요한 순간에 정확한 판단을 내립니다. 신중한 성격 덕에 실수가 적고 재물 관리에도 능해요.", "소띠 · 닭띠", "돼지띠", ["지혜", "직관", "신중함"]),
    ("horse", "말띠", "🐴", "말띠는 자유와 열정의 아이콘이에요. 활동적이고 사교성이 좋아 어디서든 분위기를 살리고, 한 번 꽂히면 무서운 집중력으로 달립니다. 얽매이는 것을 싫어하니 자율성이 보장될 때 최고의 능력이 나와요.", "호랑이띠 · 개띠", "쥐띠", ["열정", "자유", "사교성"]),
    ("sheep", "양띠", "🐑", "양띠는 배려심 깊고 온순한 예술가형이에요. 감수성이 풍부해 창작 분야에 재능이 있고, 다정한 성품 덕분에 곁에 사람이 끊이지 않습니다. 결정 앞에서 망설이는 버릇만 고치면 하는 일마다 순풍이 붑니다.", "토끼띠 · 돼지띠", "소띠", ["배려", "감수성", "온화함"]),
    ("monkey", "원숭이띠", "🐵", "원숭이띠는 재치와 임기응변의 천재예요. 다재다능해서 뭘 해도 평균 이상은 하고, 유머 감각으로 사람들을 즐겁게 만듭니다. 머리 회전이 빠른 만큼 한 우물을 파면 그 분야의 대가가 될 수 있어요.", "쥐띠 · 용띠", "호랑이띠", ["재치", "다재다능", "융통성"]),
    ("rooster", "닭띠", "🐔", "닭띠는 꼼꼼하고 계획적인 완벽주의자예요. 시간 약속을 잘 지키고 일처리가 야무져서 믿고 맡길 수 있는 사람으로 통합니다. 표현력도 좋아 말과 글로 사람을 움직이는 재주가 있어요.", "소띠 · 뱀띠", "토끼띠", ["꼼꼼함", "계획성", "표현력"]),
    ("dog", "개띠", "🐶", "개띠는 충직함과 정의감의 상징이에요. 한 번 맺은 인연을 소중히 여기고, 옳다고 믿는 일에는 물러서지 않는 강단이 있습니다. 걱정이 많은 편이지만 그만큼 위기를 미리 대비하는 능력이 뛰어나요.", "호랑이띠 · 말띠", "용띠", ["충직", "정의감", "신뢰"]),
    ("pig", "돼지띠", "🐷", "돼지띠는 예로부터 복과 재물의 상징이에요. 너그럽고 솔직한 성품이라 사람들이 편하게 다가오고, 통이 커서 베푼 만큼 더 크게 돌아오는 복을 누립니다. 거절을 잘 못하는 착한 심성은 장점이자 관리 포인트예요.", "토끼띠 · 양띠", "뱀띠", ["복덕", "너그러움", "솔직함"]),
]

ZODIAC = [
    ("aries", "양자리", "♈", "3월 21일 ~ 4월 19일", "양자리는 12별자리의 첫 주자답게 개척 정신이 넘쳐요. 하고 싶은 게 생기면 바로 움직이는 행동파로, 그 솔직한 에너지가 주변까지 움직입니다. 불의 별자리 특유의 열정으로 시작이 반이 아니라 전부임을 보여주죠.", "사자자리 · 사수자리", ["열정", "개척", "직진"]),
    ("taurus", "황소자리", "♉", "4월 20일 ~ 5월 20일", "황소자리는 안정과 감각의 별자리예요. 서두르지 않고 차근차근 쌓아 올리는 끈기가 있고, 맛집·음악·향기 같은 좋은 것을 알아보는 오감이 발달했습니다. 한 번 마음을 주면 오래가는 의리파이기도 해요.", "처녀자리 · 염소자리", ["안정", "감각", "끈기"]),
    ("gemini", "쌍둥이자리", "♊", "5월 21일 ~ 6월 21일", "쌍둥이자리는 호기심과 소통의 아이콘이에요. 새로운 정보를 빨아들이는 속도가 남다르고, 재치 있는 말솜씨로 어떤 자리든 즐겁게 만듭니다. 두 가지 일을 동시에 해내는 멀티태스킹 능력도 타고났어요.", "천칭자리 · 물병자리", ["호기심", "소통", "재치"]),
    ("cancer", "게자리", "♋", "6월 22일 ~ 7월 22일", "게자리는 따뜻한 감성과 보호 본능의 별자리예요. 소중한 사람을 챙기는 마음이 깊고, 공감 능력이 뛰어나 주변의 고민 상담소 역할을 자주 맡습니다. 기억력이 좋아 받은 정은 꼭 갚는 의리도 있어요.", "전갈자리 · 물고기자리", ["감성", "공감", "가정적"]),
    ("leo", "사자자리", "♌", "7월 23일 ~ 8월 22일", "사자자리는 타고난 주인공이에요. 밝고 당당한 에너지로 어디서든 존재감을 뿜고, 통이 커서 아낌없이 베푸는 관대함이 매력입니다. 칭찬을 먹고 자라는 별자리라 인정받을수록 더 크게 빛나요.", "양자리 · 사수자리", ["자신감", "관대함", "존재감"]),
    ("virgo", "처녀자리", "♍", "8월 23일 ~ 9월 23일", "처녀자리는 분석력과 세심함의 별자리예요. 남들이 놓치는 디테일을 잡아내는 눈이 있고, 맡은 일은 완벽하게 끝내야 직성이 풀립니다. 겉은 차분해 보여도 속은 누구보다 따뜻한 실속형 조력자예요.", "황소자리 · 염소자리", ["분석력", "세심함", "완벽주의"]),
    ("libra", "천칭자리", "♎", "9월 24일 ~ 10월 22일", "천칭자리는 균형과 조화의 달인이에요. 갈등 속에서도 양쪽 입장을 헤아리는 공정함이 있고, 세련된 미적 감각과 사교성으로 사람들을 자연스럽게 이어줍니다. 우유부단해 보이는 신중함은 사실 최선을 찾는 과정이죠.", "쌍둥이자리 · 물병자리", ["균형", "사교성", "미적감각"]),
    ("scorpio", "전갈자리", "♏", "10월 23일 ~ 11월 22일", "전갈자리는 집중력과 통찰의 별자리예요. 한 번 목표를 정하면 끝까지 파고드는 무서운 몰입력이 있고, 사람과 상황의 본질을 꿰뚫어 봅니다. 쉽게 마음을 열지 않지만 한 번 연 마음은 누구보다 깊어요.", "게자리 · 물고기자리", ["집중력", "통찰", "의지"]),
    ("sagittarius", "사수자리", "♐", "11월 23일 ~ 12월 21일", "사수자리는 낙천과 모험의 별자리예요. 어떤 상황에서도 긍정 회로를 돌리는 힘이 있고, 여행과 새로운 경험에서 인생의 답을 찾습니다. 시원시원한 성격과 넓은 시야 덕에 주변에 늘 웃음이 따라요.", "양자리 · 사자자리", ["낙천", "모험", "자유"]),
    ("capricorn", "염소자리", "♑", "12월 22일 ~ 1월 19일", "염소자리는 책임감과 야망의 별자리예요. 목표를 향해 계단을 하나씩 오르는 인내심이 있고, 어린 시절보다 나이 들수록 운이 트이는 대기만성형입니다. 묵묵한 노력이 결국 정상에서 빛을 발해요.", "황소자리 · 처녀자리", ["책임감", "야망", "인내"]),
    ("aquarius", "물병자리", "♒", "1월 20일 ~ 2월 18일", "물병자리는 독창성과 미래지향의 별자리예요. 남들과 다른 시선으로 세상을 보고, 시대를 앞서가는 아이디어로 주변을 놀라게 합니다. 자유를 사랑하지만 인류애가 깊어 공동체를 위한 일에 진심이에요.", "쌍둥이자리 · 천칭자리", ["독창성", "미래지향", "자유"]),
    ("pisces", "물고기자리", "♓", "2월 19일 ~ 3월 20일", "물고기자리는 상상력과 공감의 별자리예요. 예술적 감수성이 풍부해 음악·그림·글에서 재능을 보이고, 타인의 감정을 제 것처럼 느끼는 깊은 공감 능력이 있습니다. 꿈꾸는 힘이 곧 현실을 만드는 별자리죠.", "게자리 · 전갈자리", ["상상력", "공감", "예술성"]),
]

def tti_years(idx):
    ys = [y for y in range(1948, 2027) if (y - 4) % 12 == idx][-6:]
    return "·".join(str(y) for y in ys) + "년생"

PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{site}{fname}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{site}{fname}">
<meta property="og:locale" content="ko_KR">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔮</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{title}","url":"{site}{fname}","inLanguage":"ko"}}</script>
</head>
<body>
<div class="wrap">

  <header class="site">
    <a class="logo" href="index.html">🔮 별별운세</a>
    <p class="tagline">{tagline}</p>
  </header>

  <nav class="menu">
    <a href="index.html">홈</a>
    <a href="today.html">오늘의 운세</a>
    <a href="tarot.html">타로</a>
    <a href="saju.html">사주</a>
    <a href="tti.html"{tti_on}>띠별 운세</a>
    <a href="gunghap.html">궁합</a>
    <a href="lotto.html">로또</a>
    <a href="deals.html">특가</a>
  </nav>

  <div class="card">
    <h2>{emoji} {name} 오늘의 운세</h2>
    <p class="desc" style="margin-bottom:4px;">{sub}</p>
    <p class="desc" id="dfDate" style="color:var(--gold);"></p>
    <div class="big-number" id="score"></div>
    <p class="rank-line" id="rankLine"></p>
    <div class="score-row"><span class="cat">오늘의 별점</span><span class="stars" id="stars"></span></div>
    <p class="fortune-msg" id="msg" style="margin-top:12px; font-size:1.02rem;"></p>

    <p class="section-label">🍀 오늘의 포인트</p>
    <div class="lucky-grid">
      <div class="item"><div class="k">오늘의 키워드</div><div class="v" id="lkKey"></div></div>
      <div class="item"><div class="k">행운의 시간</div><div class="v" id="lkTime"></div></div>
      <div class="item"><div class="k">행운의 방향</div><div class="v" id="lkDir"></div></div>
    </div>
    <div id="mgBox" style="display:none;">
      <p class="section-label">📜 이 순위가 나온 이유</p>
      <div class="mg-explain" id="mgExplain"></div>
    </div>
    <button class="ghost" onclick="shareResult()" style="margin-top:20px;">📤 결과 공유하기</button>
  </div>

  <div class="card">
    <h2>💫 {name}는 어떤 사람?</h2>
    <p class="desc" style="color:var(--text); line-height:1.8;">{intro}</p>
    <div class="trait-chips">{chips}</div>
    <div class="lucky-grid" style="grid-template-columns:repeat(2,1fr); margin-top:14px;">
      <div class="item"><div class="k">{mate_label}</div><div class="v" style="font-size:.92rem;">{mates}</div></div>
      <div class="item"><div class="k">{extra_label}</div><div class="v" style="font-size:.92rem;">{extra}</div></div>
    </div>
  </div>

  <div class="card">
    <h2>{grid_title}</h2>
    <div class="link-grid">
{links}
    </div>
  </div>

  <a class="lucky-shop" href="today.html" style="margin-top:22px;">
    <span class="ls-emoji">🌞</span>
    <span class="ls-body"><span class="ls-name">이름+생년월일로 보는 오늘의 운세</span>
    <span class="ls-pitch">총운·애정운·금전운·건강운을 별점과 함께</span></span>
    <span class="ls-go">보러 가기 →</span>
  </a>

  <div style="margin-top:28px;display:flex;justify-content:center;">
    <ins class="kakao_ad_area" style="display:none;" data-ad-unit="DAN-7Y8i4O6wwHmSqg0j" data-ad-width="300" data-ad-height="250"></ins>
  </div>
  <script type="text/javascript" src="//t1.kakaocdn.net/kas/static/ba.min.js" async></script>

  <footer class="site">
    <p>✨ 모든 결과는 오락용입니다. 가볍게 재미로만 즐겨주세요 ✨</p>
    <p style="margin-top:6px;font-size:12px"><a href="privacy.html" style="color:inherit;opacity:.7">개인정보처리방침</a></p>
  </footer>

</div>

<script src="share.js"></script>
<script src="myeongri.js"></script>
<script src="astro.js"></script>
<script src="daily-fortune.js"></script>
<script>renderDailyFortune("{kind}", {idx}, "{name}");</script>
<script src="visitor-count.js"></script>
</body>
</html>
"""

made = []

# ── 띠별 12페이지 ──
for i, (slug, name, emoji, intro, mates, avoid, traits) in enumerate(TTI):
    fname = "tti-" + slug + ".html"
    years = tti_years(i)
    links = "\n".join(
        '      <a href="tti-{s}.html"{cur}>{e} {n}</a>'.format(
            s=s2, cur=' class="cur"' if s2 == slug else "", e=e2, n=n2)
        for (s2, n2, e2, *_rest) in TTI)
    html = PAGE.format(
        title="{} 오늘의 운세 무료 ({}) | 별별운세".format(name, years),
        desc="{} 오늘의 운세를 무료로 확인하세요. 오늘의 점수와 12간지 순위, 행운의 시간·방향까지 매일 업데이트! {} 성격과 궁합 정보도 함께.".format(name, name),
        keywords="{}운세,{} 오늘의운세,오늘의 {}운세,띠별운세".format(name, name, name),
        site=SITE, fname=fname,
        tagline="오늘 " + name + "에게 흐르는 기운은?",
        tti_on="", emoji=emoji, name=name,
        sub=years,
        intro=intro,
        chips="".join("<span>#" + t + "</span>" for t in traits),
        mate_label="잘 맞는 띠", mates=mates,
        extra_label="조심할 띠", extra=avoid,
        grid_title="🐾 다른 띠 운세 보기",
        links=links,
        kind="tti", idx=i,
    )
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(html)
    made.append(fname)

# ── 별자리 12페이지 ──
for i, (slug, name, emoji, period, intro, mates, traits) in enumerate(ZODIAC):
    fname = "zodiac-" + slug + ".html"
    links = "\n".join(
        '      <a href="zodiac-{s}.html"{cur}>{e} {n}</a>'.format(
            s=s2, cur=' class="cur"' if s2 == slug else "", e=e2, n=n2)
        for (s2, n2, e2, *_rest) in ZODIAC)
    html = PAGE.format(
        title="{} 오늘의 운세 무료 ({}) | 별별운세".format(name, period),
        desc="{} 오늘의 운세를 무료로 확인하세요. 오늘의 점수와 12별자리 순위, 행운의 시간·방향까지 매일 업데이트! {} 성격과 궁합 정보도 함께.".format(name, name),
        keywords="{}운세,{} 오늘의운세,별자리운세,오늘의 별자리운세".format(name, name),
        site=SITE, fname=fname,
        tagline="오늘 " + name + "의 별은 어디서 빛날까?",
        tti_on="", emoji=emoji, name=name,
        sub=period,
        intro=intro,
        chips="".join("<span>#" + t + "</span>" for t in traits),
        mate_label="잘 맞는 별자리", mates=mates,
        extra_label="별자리 기간", extra=period.replace(" ", "").replace("~", " ~ "),
        grid_title="✨ 다른 별자리 운세 보기",
        links=links,
        kind="zodiac", idx=i,
    )
    with open(os.path.join(BASE, fname), "w", encoding="utf-8") as f:
        f.write(html)
    made.append(fname)

# ── sitemap 갱신 ──
sm_path = os.path.join(BASE, "sitemap.xml")
sm = open(sm_path, encoding="utf-8").read()
new_lines = ""
for fname in made:
    loc = SITE + fname
    if loc not in sm:
        new_lines += "  <url><loc>{}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>\n".format(loc)
if new_lines:
    sm = sm.replace("</urlset>", new_lines + "</urlset>")
    with open(sm_path, "w", encoding="utf-8") as f:
        f.write(sm)

print("생성:", len(made), "페이지 + sitemap", ("갱신" if new_lines else "변화없음"))
