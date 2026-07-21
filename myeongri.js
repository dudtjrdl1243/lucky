/* ===== 간이 명리(命理) 엔진 =====
 * 실제 규칙으로 계산하는 부분:
 *   - 일주(日柱) 간지: 60갑자 순환 (기준 1900-01-01 = 갑술일, 검증 완료)
 *   - 오행(五行) 배속, 상생(相生)·상극(相剋)
 *   - 십신(十神): 내 일간과 오늘 기운의 관계 → 비겁/식상/재성/관성/인성
 *   - 지지 관계: 육합(六合)·삼합(三合)·충(沖)
 * 점수는 이 관계들로 결정되며, 같은 조건이면 항상 같은 결과가 나옵니다.
 * (정통 사주는 태어난 시각과 절기 기준 월주까지 보지만, 여기서는 일주 중심의 간이 방식입니다.)
 */
const MG = (function () {
  const STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"];
  const STEM_H = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
  const BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"];
  const BRANCH_H = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
  const ANIMALS = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"];

  // 오행: 0=목 1=화 2=토 3=금 4=수  (생: e→(e+1)%5, 극: e→(e+2)%5)
  const ELEM = ["목", "화", "토", "금", "수"];
  const ELEM_H = ["木", "火", "土", "金", "水"];
  const ELEM_COLOR = ["푸른", "붉은", "노란", "흰", "검은"];
  const STEM_ELEM = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4];
  const BRANCH_ELEM = [4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4];

  const DAY0 = Date.UTC(1900, 0, 1); // 기준일: 갑술(index 10)

  function pillarIndex(y, m, d) {
    const days = Math.round((Date.UTC(y, m - 1, d) - DAY0) / 86400000);
    return ((10 + days) % 60 + 60) % 60;
  }

  function pillar(y, m, d) {
    const i = pillarIndex(y, m, d);
    const s = i % 10, b = i % 12;
    return {
      stem: s, branch: b,
      name: STEMS[s] + BRANCHES[b],
      hanja: STEM_H[s] + BRANCH_H[b],
      stemElem: STEM_ELEM[s],
      branchElem: BRANCH_ELEM[b],
      animal: ANIMALS[b],
    };
  }

  /* 십신: 내 일간(me)과 상대 기운(t)의 오행 관계 */
  function tenGod(me, t) {
    if (t === me) return "비겁";
    if (t === (me + 1) % 5) return "식상"; // 내가 낳아주는 것
    if (t === (me + 2) % 5) return "재성"; // 내가 이기는 것
    if (me === (t + 2) % 5) return "관성"; // 나를 이기는 것
    return "인성";                          // 나를 낳아주는 것
  }

  /* 지지 관계: 삼합(같은 mod 4) / 충(차이 6) / 육합(합이 12로 나눠 1) */
  function branchRel(a, b) {
    if (a === b) return "동일";
    if (Math.abs(a - b) === 6) return "충";
    if ((a + b) % 12 === 1) return "육합";
    if (a % 4 === b % 4) return "삼합";
    return "무관";
  }

  // 십신별 점수 보정 [총운, 애정, 금전, 직장·학업, 건강]
  const GOD_SCORE = {
    "비겁": [2, -3, -5, 3, 7],
    "식상": [7, 12, 4, -2, 4],
    "재성": [9, 6, 16, 3, -3],
    "관성": [3, 4, 3, 14, -7],
    "인성": [8, -1, -2, 9, 9],
  };
  const REL_SCORE = { "육합": 8, "삼합": 6, "동일": 3, "무관": 0, "충": -9 };

  const GOD_DESC = {
    "비겁": "나와 같은 기운이 도는 날. 경쟁심과 체력은 올라가지만 지출은 새기 쉬워요.",
    "식상": "내가 밖으로 뻗어나가는 기운. 표현하고 움직일수록 풀리는 날이에요.",
    "재성": "내가 다스리는 기운, 곧 재물의 자리. 금전 흐름이 열리는 날입니다.",
    "관성": "나를 다잡는 기운. 일과 규율에는 힘이 실리지만 몸은 무리하기 쉬워요.",
    "인성": "나를 살려주는 기운. 도움과 배움, 귀인이 들어오는 자리예요.",
  };
  const REL_TAIL = {
    "육합": "육합(六合) — 서로 끌어당기는 관계라 매사 순조롭습니다.",
    "삼합": "삼합(三合) — 힘을 모아주는 관계라 흐름이 좋습니다.",
    "동일": "같은 지지라 기운이 겹칩니다. 익숙한 일이 잘 풀려요.",
    "무관": "특별한 합충(合沖) 관계가 없어 무난한 하루입니다.",
    "충": "충(沖) — 부딪히는 관계라 변동수가 있습니다. 이동·계약은 한 번 더 확인하세요.",
  };

  const CATS = ["총운", "애정운", "금전운", "직장·학업운", "건강운"];

  // 십신 × 항목별 조언 (2개씩 번갈아 나옴)
  const MSG = {
    "비겁": [
      ["경쟁 구도가 생겨도 밀리지 않는 날이에요. 다만 혼자 다 하려 들면 지칩니다.", "내 몫을 지키는 힘이 강한 날. 양보는 오늘만 잠시 미뤄도 좋아요."],
      ["상대와 기 싸움이 붙기 쉬운 날. 한 발 물러서면 관계가 오래갑니다.", "친구 같은 편안함이 커지는 날이에요. 설렘보다 의리가 앞섭니다."],
      ["돈이 새기 쉬운 날. 나눠 쓸 일이 생기면 미리 선을 그어두세요.", "지출 제안이 들어오기 쉬운 날. 오늘은 지갑을 조금 닫아두는 게 좋아요."],
      ["동료와 부딪히기 쉽지만 실력은 드러나는 날. 결과로 말하세요.", "혼자 처리하려 하지 말고 역할을 나누면 훨씬 빨리 끝납니다."],
      ["체력이 붙는 날이에요. 미뤄둔 운동을 시작하기 좋습니다.", "기운이 넘쳐 무리하기 쉬운 날. 마무리는 여유 있게 하세요."],
    ],
    "식상": [
      ["말과 행동이 술술 풀리는 날. 미뤄둔 연락이나 제안을 오늘 꺼내보세요.", "새로운 걸 시작하기 좋은 날이에요. 손이 가는 대로 움직이면 됩니다."],
      ["표현하는 만큼 돌아오는 날. 마음을 돌려 말하지 마세요.", "웃음 코드가 잘 맞는 하루. 가벼운 대화에서 인연이 열립니다."],
      ["활동한 만큼 수입으로 이어지는 날. 다만 큰 투자는 다음으로 미루세요.", "작은 부수입이 생길 수 있어요. 움직이는 쪽이 이득입니다."],
      ["아이디어가 쏟아지는 날. 메모해두면 나중에 진짜 쓸 게 나옵니다.", "정해진 틀보다 새 방식이 먹히는 날. 제안해볼 만해요."],
      ["몸을 움직일수록 개운해지는 날이에요. 산책 20분이면 충분합니다.", "기분 따라 과식하기 쉬운 날. 즐기되 한 접시만 덜어내세요."],
    ],
    "재성": [
      ["붙잡은 것을 내 것으로 만드는 날. 결정을 미루지 않는 편이 좋아요.", "실속이 챙겨지는 하루예요. 계산이 맞아떨어집니다."],
      ["여유가 매력이 되는 날. 베푸는 쪽이 마음을 얻습니다.", "함께 무언가를 사거나 먹으면 사이가 좋아지는 날이에요."],
      ["금전 흐름이 가장 크게 열리는 날. 미뤄둔 정산이나 청구를 오늘 처리하세요.", "돈 이야기를 꺼내기 좋은 날이에요. 조건을 말해도 무리가 없습니다."],
      ["성과가 숫자로 보이는 날. 실적 정리에 유리합니다.", "맡은 만큼 확실히 챙기는 날이에요. 애매한 건 문서로 남기세요."],
      ["일에 몰두하다 끼니를 거르기 쉬운 날. 물이라도 챙기세요.", "욕심이 체력을 앞서는 날. 오늘은 한 가지만 끝내도 충분합니다."],
    ],
    "관성": [
      ["규칙과 절차가 나를 지켜주는 날. 정공법이 가장 빠릅니다.", "책임이 늘지만 그만큼 신뢰도 쌓이는 하루예요."],
      ["진중한 태도가 점수를 얻는 날. 가벼운 농담은 아껴두세요.", "약속을 지키는 것만으로 마음을 얻는 날입니다."],
      ["나가는 돈이 정해져 있는 날. 계획대로만 쓰면 문제없어요.", "큰 지출 결정은 내일로 미루는 편이 안전합니다."],
      ["윗사람 눈에 드는 날이에요. 보고와 정리를 꼼꼼히 하세요.", "맡겨진 일에서 인정받는 날. 기본기가 그대로 드러납니다."],
      ["긴장이 몸으로 오는 날. 어깨와 목을 자주 풀어주세요.", "무리한 일정은 줄이세요. 오늘은 쉬는 것도 일입니다."],
    ],
    "인성": [
      ["도와주는 사람이 나타나는 날. 혼자 끙끙대지 말고 물어보세요.", "배움이 붙는 하루예요. 읽고 듣는 시간이 그대로 남습니다."],
      ["상대의 이야기를 들어주는 쪽이 매력적인 날이에요.", "설렘보다 편안함이 커지는 날. 오래 볼 사람이 보입니다."],
      ["당장 버는 날은 아니지만 나중을 위한 씨앗을 심기 좋아요.", "지출은 공부나 나를 채우는 쪽으로 쓰면 아깝지 않습니다."],
      ["공부와 자격, 준비에 최적인 날. 집중이 오래 갑니다.", "귀인의 조언이 방향을 잡아주는 날이에요."],
      ["푹 쉬면 회복이 빠른 날. 일찍 자는 게 최고의 보약입니다.", "몸이 편안해지는 날이에요. 따뜻한 것을 챙겨 드세요."],
    ],
  };

  function compute(by, bm, bd, today) {
    const t = today || new Date();
    const me = pillar(by, bm, bd);
    const day = pillar(t.getFullYear(), t.getMonth() + 1, t.getDate());

    const meElem = me.stemElem;                 // 일간 오행 = 나
    const god = tenGod(meElem, day.stemElem);   // 오늘 천간과의 관계
    const godB = tenGod(meElem, day.branchElem); // 오늘 지지와의 관계
    const rel = branchRel(me.branch, day.branch);

    const base = GOD_SCORE[god], sub = GOD_SCORE[godB], bonus = REL_SCORE[rel];
    const scores = {};
    CATS.forEach(function (c, i) {
      // 천간(주)·지지(보조) 영향 + 지지 관계 보정
      let v = 62 + base[i] + Math.round(sub[i] * 0.5) + bonus;
      scores[c] = Math.max(41, Math.min(99, v));
    });

    // 조언 문구: 십신으로 결정, 날짜에 따라 두 개 중 하나
    const alt = day.stem % 2;
    const msgs = {};
    CATS.forEach(function (c, i) { msgs[c] = MSG[god][i][alt]; });

    const explain = [
      "오늘은 " + day.name + "(" + day.hanja + ")일 — " + ELEM[day.stemElem] + "(" + ELEM_H[day.stemElem] + ")의 기운이 도는 날입니다.",
      "당신이 태어난 날은 " + me.name + "(" + me.hanja + ")일, 일간은 " + STEMS[me.stem] + "(" + STEM_H[me.stem] + ") — 오행으로 " + ELEM[meElem] + "(" + ELEM_H[meElem] + ")입니다.",
      godSentence(god, day.stemElem, meElem) + " " + GOD_DESC[god],
      relSentence(rel, "태어난 날의 지지", me.branch, day.branch),
    ];

    // 행운의 색: 나를 살려주는 오행(인성)의 색 — X생me 이므로 X = (me+4)%5
    const helper = (meElem + 4) % 5;

    return {
      dayPillar: day, myPillar: me, god: god, rel: rel,
      scores: scores, msgs: msgs, explain: explain,
      luckyColor: ELEM_COLOR[helper] + " 계열",
      luckyElem: ELEM[helper],
    };
  }

  function godLabel(g) {
    return { "비겁": "比劫", "식상": "食傷", "재성": "財星", "관성": "官星", "인성": "印星" }[g];
  }

  /* 받침 유무 판정 (목·금은 받침 있음, 화·토·수는 없음) */
  function hasBatchim(word) {
    const code = word.charCodeAt(word.length - 1) - 0xAC00;
    return code >= 0 && code <= 11171 && code % 28 !== 0;
  }

  /* 지지 관계 문장 — 주어와 두 지지를 받아 조사까지 맞춰 조립
   * 예) "호랑이띠의 인(寅)과 오늘 지지 신(申)이 충(沖) — ..." */
  function relSentence(rel, ownerLabel, myBranch, dayBranch) {
    const aName = BRANCHES[myBranch], bName = BRANCHES[dayBranch];
    const a = aName + "(" + BRANCH_H[myBranch] + ")" + (hasBatchim(aName) ? "과" : "와");
    const b = bName + "(" + BRANCH_H[dayBranch] + ")" + (hasBatchim(bName) ? "이" : "가");
    return ownerLabel + " " + a + " 오늘 지지 " + b + " " + REL_TAIL[rel];
  }

  /* 십신 관계를 자연스러운 한 문장으로 */
  function godSentence(god, dayE, meE) {
    const dayName = ELEM[dayE], meName = ELEM[meE];
    const day = dayName + "(" + ELEM_H[dayE] + ")";
    const me = meName + "(" + ELEM_H[meE] + ")";
    const dayTopic = "오늘의 " + day + (hasBatchim(dayName) ? "은" : "는");
    const meSubj = "당신의 " + me + (hasBatchim(meName) ? "이" : "가");
    const meObj = "당신의 " + me + (hasBatchim(meName) ? "을" : "를");
    if (god === "비겁") return dayTopic + " 당신과 같은 " + me + " — 비겁(比劫)입니다.";
    if (god === "식상") return dayTopic + " " + meSubj + " 낳아주는 식상(食傷)입니다.";
    if (god === "재성") return dayTopic + " " + meSubj + " 다스리는 재성(財星)입니다.";
    if (god === "관성") return dayTopic + " " + meObj + " 다스리는 관성(官星)입니다.";
    return dayTopic + " " + meObj + " 살려주는 인성(印星)입니다.";
  }

  /* ===== 띠별 오늘의 운세 =====
   * 띠는 곧 지지(자~해)이므로, 오늘 일진과의 관계를 실제 규칙으로 계산한다.
   *   - 띠 지지의 오행 vs 오늘 일간 오행 → 십신
   *   - 띠 지지 vs 오늘 일지 → 육합·삼합·충
   * 12띠 점수를 모두 계산해 순위까지 산출 (난수 아님).
   */
  function ttiFortune(branchIdx, today) {
    const t = today || new Date();
    const day = pillar(t.getFullYear(), t.getMonth() + 1, t.getDate());
    const myElem = BRANCH_ELEM[branchIdx];
    const god = tenGod(myElem, day.stemElem);
    const rel = branchRel(branchIdx, day.branch);

    const base = GOD_SCORE[god], bonus = REL_SCORE[rel];
    const scores = {};
    CATS.forEach(function (c, i) {
      scores[c] = Math.max(41, Math.min(99, 62 + base[i] + bonus));
    });
    const total = Math.round(CATS.reduce(function (s, c) { return s + scores[c]; }, 0) / CATS.length);

    const explain = [
      "오늘은 " + day.name + "(" + day.hanja + ")일 — " + ELEM[day.stemElem] + "(" + ELEM_H[day.stemElem] + ")의 기운이 도는 날입니다.",
      ANIMALS[branchIdx] + "띠는 지지 " + BRANCHES[branchIdx] + "(" + BRANCH_H[branchIdx] + "), 오행으로 " + ELEM[myElem] + "(" + ELEM_H[myElem] + ")입니다.",
      godSentence(god, day.stemElem, myElem).replace("당신의", ANIMALS[branchIdx] + "띠의") + " " + GOD_DESC[god],
      relSentence(rel, ANIMALS[branchIdx] + "띠의", branchIdx, day.branch),
    ];

    return {
      animal: ANIMALS[branchIdx], branch: BRANCHES[branchIdx],
      god: god, rel: rel, total: total, scores: scores,
      msgs: (function () { const m = {}; CATS.forEach(function (c, i) { m[c] = MSG[god][i][day.stem % 2]; }); return m; })(),
      explain: explain, dayPillar: day,
    };
  }

  /* 12띠 전체 점수 → 순위 (동점이면 지지 순서가 앞선 띠가 상위) */
  function ttiRanking(today) {
    const list = [];
    for (let i = 0; i < 12; i++) list.push({ idx: i, total: ttiFortune(i, today).total });
    const sorted = list.slice().sort(function (a, b) { return b.total - a.total || a.idx - b.idx; });
    const rank = {};
    sorted.forEach(function (e, n) { rank[e.idx] = n + 1; });
    return { rank: rank, totals: list };
  }

  return {
    compute: compute, pillar: pillar, CATS: CATS,
    ttiFortune: ttiFortune, ttiRanking: ttiRanking,
    ANIMALS: ANIMALS, BRANCHES: BRANCHES,
  };
})();
