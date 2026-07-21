/* ===== 띠별/별자리 개별 페이지 공용: 오늘의 운세 렌더러 =====
 * tti.html과 같은 시드 규칙을 사용해 점수가 서로 일치함
 */
function hashSeed(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  return h >>> 0;
}
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const DF_MSGS = [
  "막혔던 일이 스르르 풀리는 하루예요. 미뤄둔 연락 한 통이 좋은 물꼬가 됩니다.",
  "귀인이 가까이에 있는 날입니다. 오늘 만나는 사람에게 밝게 인사해 보세요.",
  "서두르지 않는 것이 오늘의 승부수예요. 천천히 가도 충분히 빠릅니다.",
  "재물의 기운이 감도는 날. 다만 새어 나가는 작은 지출부터 단속하세요.",
  "생각지 못한 칭찬이나 인정을 받을 수 있어요. 겸손하게 웃으며 받으세요.",
  "말이 씨가 되는 날이니 긍정적인 말로 하루를 채워보세요.",
  "몸을 움직일수록 운이 붙는 날이에요. 산책이나 가벼운 운동이 행운을 부릅니다.",
  "오래 고민하던 문제의 답이 대화 속에서 툭 튀어나옵니다. 사람들과 이야기를 나눠보세요.",
  "정리정돈이 운을 부르는 날. 가방 속, 책상 위부터 가볍게 비워보세요.",
  "새로운 제안이나 소식이 들어올 수 있어요. 열린 마음으로 들어보면 기회가 보입니다.",
  "오늘은 베푸는 만큼 돌아오는 날이에요. 작은 친절이 큰 복으로 자랍니다.",
  "감이 좋은 날입니다. 사소한 선택은 첫 느낌을 믿어보세요.",
  "욕심을 한 스푼 덜어내면 오히려 더 큰 것이 들어오는 하루예요.",
  "익숙한 것에서 벗어나 보세요. 새로운 길, 새로운 메뉴가 활력이 됩니다.",
  "주변의 응원이 힘이 되는 날이에요. 도움을 청하는 것도 능력입니다.",
  "느긋한 마음이 최고의 부적이 되는 하루입니다. 여유를 챙기세요."
];
const DF_KEYS  = ["기회", "여유", "소통", "정리", "직감", "도전", "배려", "휴식", "집중", "인연", "행동", "감사"];
const DF_TIMES = ["아침 7~9시", "오전 9~11시", "낮 11~1시", "오후 1~3시", "오후 3~5시", "저녁 5~7시", "저녁 7~9시", "밤 9~11시"];
const DF_DIRS  = ["동쪽", "서쪽", "남쪽", "북쪽", "남동쪽", "북동쪽", "남서쪽", "북서쪽"];

/* kind: "tti"(12간지, tti.html과 동일 시드) 또는 "zodiac"(별자리)
 * idx: 그룹 내 인덱스, label: "쥐띠"/"물병자리" 등 (순위 문구용) */
function renderDailyFortune(kind, idx, label) {
  const t = new Date();
  const dateStr = t.getFullYear() + "-" + (t.getMonth() + 1) + "-" + t.getDate();
  const useMyeongri = kind === "tti" && typeof MG !== "undefined";
  const useAstro = kind === "zodiac" && typeof ASTRO !== "undefined";

  let score, rank, mg = null;
  if (useMyeongri) {
    // 띠는 곧 지지 → 오늘 일진과의 오행·합충 관계로 실제 계산
    mg = MG.ttiFortune(idx, t);
    score = mg.total;
    rank = MG.ttiRanking(t).rank[idx];
  } else if (useAstro) {
    // 별자리는 오늘 태양궁과의 각(애스펙트) + 원소 + 달 위상으로 계산
    mg = ASTRO.zodiacFortune(idx, t);
    score = mg.total;
    rank = ASTRO.zodiacRanking(t).rank[idx];
  } else {
    const scores = [];
    for (let i = 0; i < 12; i++) {
      const r = mulberry32(hashSeed(dateStr + "|" + kind + "|" + i));
      scores.push(55 + Math.floor(r() * 46));
    }
    score = scores[idx];
    rank = 1 + scores.filter((s, j) => s > score || (s === score && j < idx)).length;
  }
  const rng = mulberry32(hashSeed(dateStr + "|" + kind + "-detail|" + idx));
  const stars = (useMyeongri || useAstro)
    ? (score >= 82 ? 5 : score >= 73 ? 4 : score >= 65 ? 3 : score >= 56 ? 2 : 1)
    : (score >= 92 ? 5 : score >= 80 ? 4 : score >= 66 ? 3 : 2);
  const group = kind === "tti" ? "12간지" : "12별자리";

  document.getElementById("dfDate").textContent =
    t.getFullYear() + "년 " + (t.getMonth() + 1) + "월 " + t.getDate() + "일";
  document.getElementById("score").textContent = score + "점";
  document.getElementById("rankLine").innerHTML =
    "오늘 " + group + " 중 <b>" + rank + "위</b>" +
    (rank === 1 ? " 👑 오늘의 주인공!" : rank <= 3 ? " ✨ 상위권이에요!" : rank >= 11 ? " — 이런 날일수록 여유가 무기!" : "");
  document.getElementById("stars").textContent = "★".repeat(stars) + "☆".repeat(5 - stars);
  document.getElementById("msg").textContent = mg ? mg.msgs["총운"] : DF_MSGS[Math.floor(rng() * DF_MSGS.length)];

  const label2 = document.querySelector("#mgBox .section-label");
  if (label2) label2.textContent = useAstro ? "📜 이 별자리 운세의 근거" : "📜 이 순위가 나온 이유";

  const box = document.getElementById("mgBox");
  if (box) {
    if (mg) {
      document.getElementById("mgExplain").innerHTML =
        mg.explain.map(function (line) { return "<p>" + line + "</p>"; }).join("") +
        '<p class="mg-note">' + (useAstro
          ? "오늘 태양궁과의 각(애스펙트), 4원소 상성, 달의 위상으로 계산한 결과입니다. 순위도 12별자리 점수를 계산해 매긴 것이며, 무작위가 아닙니다. 행성 전체를 보는 정통 점성술과 달리 태양·달만 반영한 간이 방식이에요."
          : "일진(日辰)과 띠 지지의 오행 관계(십신)·합충으로 계산한 결과입니다. 순위도 12띠 점수를 계산해 매긴 것이며, 무작위가 아닙니다.") + '</p>';
      box.style.display = "";
    } else {
      box.style.display = "none";
    }
  }
  document.getElementById("lkKey").textContent = DF_KEYS[Math.floor(rng() * DF_KEYS.length)];
  document.getElementById("lkTime").textContent = DF_TIMES[Math.floor(rng() * DF_TIMES.length)];
  document.getElementById("lkDir").textContent = DF_DIRS[Math.floor(rng() * DF_DIRS.length)];

  window.SHARE_TEXT = "🔮 " + label + " 오늘 " + score + "점, " + group + " 중 " + rank + "위! 너도 무료로 확인해봐";
}
