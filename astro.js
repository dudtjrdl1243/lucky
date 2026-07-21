/* ===== 서양 점성술 간이 엔진 =====
 * 명리(음양오행)와는 다른 체계이므로 파일을 분리했습니다.
 * 실제 규칙으로 계산하는 부분:
 *   - 오늘 태양이 머무는 별자리(태양궁): 날짜로 결정
 *   - 내 별자리와 오늘 태양궁 사이의 각(角) → 애스펙트
 *     0°합 / 30°반육분 / 60°육분 / 90°사분 / 120°삼분 / 150°퀸컹크스 / 180°대립
 *   - 4원소(불·흙·공기·물)와 3특질(활동·고정·변통)
 *   - 달의 위상: 삭망월 29.53059일 주기로 계산 (기준 2000-01-06 신월)
 * 점수는 위 관계로 결정되며, 같은 조건이면 항상 같은 결과가 나옵니다.
 */
const ASTRO = (function () {
  // [이름, 기호, 시작월, 시작일, 원소(0불 1흙 2공기 3물), 특질(0활동 1고정 2변통)]
  const SIGNS = [
    ["양자리", "♈", 3, 21, 0, 0], ["황소자리", "♉", 4, 20, 1, 1],
    ["쌍둥이자리", "♊", 5, 21, 2, 2], ["게자리", "♋", 6, 22, 3, 0],
    ["사자자리", "♌", 7, 23, 0, 1], ["처녀자리", "♍", 8, 23, 1, 2],
    ["천칭자리", "♎", 9, 24, 2, 0], ["전갈자리", "♏", 10, 23, 3, 1],
    ["사수자리", "♐", 11, 23, 0, 2], ["염소자리", "♑", 12, 22, 1, 0],
    ["물병자리", "♒", 1, 20, 2, 1], ["물고기자리", "♓", 2, 19, 3, 2],
  ];
  const ELEMENTS = ["불", "흙", "공기", "물"];
  const ELEM_DESC = ["열정과 추진", "안정과 실속", "소통과 사고", "감정과 직관"];
  const MODALITY = ["활동궁", "고정궁", "변통궁"];
  const MOD_DESC = ["새로 시작하고 이끄는", "지키고 밀고 나가는", "맞춰가고 변화하는"];

  /* 날짜 → 태양이 머무는 별자리 index */
  function sunSign(m, d) {
    for (let i = 0; i < 12; i++) {
      const [, , sm, sd] = SIGNS[i];
      const next = SIGNS[(i + 1) % 12];
      const nm = next[2], nd = next[3];
      const after = (m > sm) || (m === sm && d >= sd);
      const before = (m < nm) || (m === nm && d < nd);
      if (sm < nm ? (after && before) : (after || before)) return i;
    }
    return 0;
  }

  /* 달의 위상 (0~7): 기준 2000-01-06 18:14 UTC 신월, 삭망월 29.530588853일 */
  const MOONS = [
    ["신월(삭)", "새로 시작하기 좋은 때. 씨앗을 심는 시기예요."],
    ["초승달", "시작한 일에 힘이 붙는 때. 꾸준함이 관건입니다."],
    ["상현달", "결정과 추진의 때. 미루던 선택을 내리기 좋아요."],
    ["차오르는 달", "결과가 눈에 보이기 시작하는 때. 속도를 올려도 좋습니다."],
    ["보름달", "감정과 기운이 최고조. 좋은 일도 갈등도 커지는 때예요."],
    ["기우는 달", "받은 것을 나누고 정리하는 때. 감사 인사가 잘 통합니다."],
    ["하현달", "덜어내고 비우는 때. 정리하면 마음이 가벼워져요."],
    ["그믐달", "쉬어가는 때. 다음을 준비하며 재충전하기 좋습니다."],
  ];
  function moonPhase(date) {
    const ref = Date.UTC(2000, 0, 6, 18, 14);
    const days = (date.getTime() - ref) / 86400000;
    let p = (days % 29.530588853) / 29.530588853;
    if (p < 0) p += 1;
    return { idx: Math.floor(p * 8) % 8, ratio: p };
  }

  /* 두 별자리 사이의 애스펙트 */
  const ASPECTS = {
    0: ["합(合)", "0°", "태양이 당신의 별자리를 지나는 시기예요. 자기 자신에게 집중되는 때입니다."],
    1: ["반육분(半六分)", "30°", "약하게 스치는 각. 잔잔하지만 조금 어색한 흐름이에요."],
    2: ["육분(六分)", "60°", "기회의 각. 손을 뻗으면 잡히는 흐름입니다."],
    3: ["사분(四分)", "90°", "긴장의 각. 부딪히지만 그만큼 추진력이 생깁니다."],
    4: ["삼분(三分)", "120°", "가장 조화로운 각. 애쓰지 않아도 술술 풀립니다."],
    5: ["퀸컹크스", "150°", "어긋나는 각. 조정과 타협이 필요한 흐름이에요."],
    6: ["대립(對立)", "180°", "마주 보는 각. 관계에서 균형을 요구받는 때입니다."],
  };
  function aspectOf(a, b) {
    const d = Math.abs(a - b) % 12;
    return Math.min(d, 12 - d);
  }

  // 애스펙트별 점수 [총운, 애정, 금전, 직장·학업, 건강]
  const ASP_SCORE = {
    0: [8, 6, 4, 6, 6], 1: [2, 2, 3, 2, 2], 2: [7, 9, 6, 6, 4],
    3: [-4, -3, -1, 3, -6], 4: [10, 9, 8, 7, 8], 5: [-2, -4, -3, -1, -3],
    6: [-3, -6, -1, 4, -5],
  };

  // 애스펙트 × 항목 조언
  const MSG = {
    0: ["나에게 집중되는 시기. 하고 싶던 일을 꺼내기 좋아요.", "내 매력이 그대로 드러나는 때. 꾸미는 만큼 보입니다.", "나를 위한 소비가 늘기 쉬운 때. 한 가지만 고르세요.", "존재감이 커지는 시기. 의견을 내면 통합니다.", "기운이 도는 때지만 과신은 금물. 페이스를 지키세요."],
    1: ["조금 어색해도 흐름은 나쁘지 않아요. 하던 대로 가면 됩니다.", "미묘한 온도차가 느껴지는 때. 서두르지 마세요.", "큰 변화는 없는 시기. 유지가 곧 이득입니다.", "무난하게 흘러가는 때. 기본에 충실하세요.", "특별할 것 없이 무난한 컨디션이에요."],
    2: ["기회가 옆에 와 있는 시기. 먼저 말 걸고 먼저 물어보세요.", "새로운 인연이 가볍게 시작되기 좋은 때예요.", "작은 부수입이나 좋은 제안이 들어올 수 있어요.", "협업이 잘 풀리는 시기. 도움을 청하면 바로 옵니다.", "가볍게 몸을 움직이기 좋은 때. 산책부터 시작하세요."],
    3: ["부딪히는 일이 있지만 그만큼 밀고 나가는 힘도 커요.", "감정이 예민해지기 쉬운 때. 한 박자 쉬고 말하세요.", "예상 못 한 지출이 생기기 쉬운 시기. 여유분을 남겨두세요.", "압박이 있지만 실력이 드러나는 때. 정면 돌파가 낫습니다.", "긴장이 몸으로 오는 시기. 잠과 스트레칭을 챙기세요."],
    4: ["가장 순조로운 시기. 미뤄둔 일을 꺼내기에 최적입니다.", "관계가 부드럽게 풀리는 때. 표현하면 그대로 전해져요.", "금전 흐름이 안정되는 시기. 계획한 대로 굴러갑니다.", "노력이 결과로 이어지는 때. 마무리하기 좋아요.", "컨디션이 안정적인 시기. 회복도 빠릅니다."],
    5: ["조금씩 어긋나는 느낌이 드는 때. 계획을 유연하게 두세요.", "말이 잘 안 통한다 느껴지면 오늘은 미루는 게 나아요.", "예정에 없던 비용이 생기기 쉬운 시기. 확인 또 확인.", "일정이 꼬이기 쉬운 때. 여유 시간을 넉넉히 잡으세요.", "잔병치레가 있기 쉬운 시기. 무리하지 마세요."],
    6: ["마주 보는 시기. 상대의 입장에서 보면 답이 보입니다.", "관계에서 균형을 요구받는 때. 한쪽으로 기울지 마세요.", "함께 쓰는 돈에서 이견이 생기기 쉬워요. 미리 정하세요.", "협상과 조율이 핵심인 시기. 명확히 말하면 통합니다.", "무리한 일정으로 지치기 쉬운 때. 쉬는 것도 일정입니다."],
  };

  const CATS = ["총운", "애정운", "금전운", "직장·학업운", "건강운"];

  function zodiacFortune(idx, today) {
    const t = today || new Date();
    const sun = sunSign(t.getMonth() + 1, t.getDate());
    const asp = aspectOf(idx, sun);
    const moon = moonPhase(t);

    const [name, sym, , , elem, mod] = SIGNS[idx];
    const sunName = SIGNS[sun][0];
    const base = ASP_SCORE[asp];

    // 원소 궁합: 같은 원소 +4, 상성(불-공기 / 흙-물) +2
    const sunElem = SIGNS[sun][4];
    let elemBonus = 0;
    if (elem === sunElem) elemBonus = 4;
    else if ((elem === 0 && sunElem === 2) || (elem === 2 && sunElem === 0) ||
             (elem === 1 && sunElem === 3) || (elem === 3 && sunElem === 1)) elemBonus = 2;
    // 달 위상: 보름 전후로 기운이 올라감
    const moonBonus = [1, 2, 3, 4, 5, 3, 1, 0][moon.idx];

    const scores = {};
    CATS.forEach(function (c, i) {
      scores[c] = Math.max(41, Math.min(99, 62 + base[i] + elemBonus + moonBonus));
    });
    const total = Math.round(CATS.reduce(function (s, c) { return s + scores[c]; }, 0) / CATS.length);

    const msgs = {};
    CATS.forEach(function (c, i) { msgs[c] = MSG[asp][i]; });

    const A = ASPECTS[asp];
    const explain = [
      "오늘 태양은 " + sunName + "에 머물고 있습니다. (" + (t.getMonth() + 1) + "월 " + t.getDate() + "일 기준)",
      name + "는 " + ELEMENTS[elem] + "의 원소, " + MODALITY[mod] + " — " + ELEM_DESC[elem] + ", " + MOD_DESC[mod] + " 기질입니다.",
      name + "와 오늘 태양궁 " + sunName + " 사이는 " + A[1] + " " + A[0] + " 관계예요. " + A[2],
      "달은 지금 " + MOONS[moon.idx][0] + " 단계입니다. " + MOONS[moon.idx][1],
    ];

    return {
      sign: name, symbol: sym, aspect: A[0], total: total,
      scores: scores, msgs: msgs, explain: explain,
      element: ELEMENTS[elem], modality: MODALITY[mod],
    };
  }

  function zodiacRanking(today) {
    const list = [];
    for (let i = 0; i < 12; i++) list.push({ idx: i, total: zodiacFortune(i, today).total });
    const sorted = list.slice().sort(function (a, b) { return b.total - a.total || a.idx - b.idx; });
    const rank = {};
    sorted.forEach(function (e, n) { rank[e.idx] = n + 1; });
    return { rank: rank, totals: list };
  }

  return { zodiacFortune: zodiacFortune, zodiacRanking: zodiacRanking, sunSign: sunSign, moonPhase: moonPhase, CATS: CATS };
})();
