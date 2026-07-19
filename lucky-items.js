/* ===== 별별운세 · 오늘의 행운 아이템 (쿠팡 파트너스) =====
 * url이 빈 문자열("")인 상품은 화면에 표시되지 않습니다.
 * 쿠팡 파트너스 대시보드에서 keyword로 상품을 검색해 링크 생성 후
 * url에 붙여넣으면 해당 아이템이 자동으로 노출됩니다.
 */

// 오늘의 운세 "행운의 아이템" 12종과 1:1 매칭 (today.html의 ITEMS 배열과 키가 같아야 함)
const LUCKY_PRODUCTS = {
  "손수건":   { emoji: "🤍", name: "포근한 손수건",        pitch: "오늘의 행운을 닦아 간직하세요",        keyword: "손수건 선물세트", url: "" },
  "텀블러":   { emoji: "🥤", name: "행운의 텀블러",        pitch: "좋은 기운을 담아 다니는 하루",          keyword: "보온 텀블러",     url: "" },
  "동전":     { emoji: "🪙", name: "행운의 동전지갑",      pitch: "굴러들어올 금전운을 담을 자리",        keyword: "동전지갑",        url: "" },
  "볼펜":     { emoji: "🖊️", name: "술술 풀리는 볼펜",     pitch: "쓰는 일마다 술술 풀리라고",            keyword: "제트스트림 볼펜", url: "" },
  "이어폰":   { emoji: "🎧", name: "행운의 이어폰",        pitch: "좋은 소식이 먼저 들리는 귀",            keyword: "블루투스 이어폰", url: "" },
  "립밤":     { emoji: "💋", name: "말문이 트이는 립밤",   pitch: "오늘은 말 한마디가 행운이 되는 날",    keyword: "립밤",            url: "" },
  "열쇠고리": { emoji: "🍀", name: "네잎클로버 키링",      pitch: "행운을 열쇠에 채워 다니세요",          keyword: "네잎클로버 키링", url: "" },
  "책 한 권": { emoji: "📖", name: "마음을 채우는 책",     pitch: "오늘의 운세가 권하는 마음 채우기",      keyword: "베스트셀러 에세이", url: "" },
  "우산":     { emoji: "☂️", name: "든든한 자동우산",      pitch: "궂은 일은 미리 막아주는 부적",          keyword: "3단 자동우산",    url: "" },
  "사탕":     { emoji: "🍬", name: "달콤한 행운 사탕",     pitch: "입안이 달면 하루도 달아요",            keyword: "수제 사탕",       url: "" },
  "머리끈":   { emoji: "🎀", name: "복을 묶는 머리끈",     pitch: "행운은 단단히 묶어둬야 안 도망가요",    keyword: "곱창 머리끈 세트", url: "" },
  "향수":     { emoji: "🌸", name: "좋은 기운의 향수",     pitch: "좋은 향에는 좋은 인연이 따라와요",      keyword: "미니 향수",       url: "" }
};

// 로또 페이지용 행운템 (번호 뽑을 때마다 랜덤 1개 노출)
const LOTTO_PRODUCTS = [
  { emoji: "🐷", name: "황금 돼지저금통",   pitch: "당첨 전까지 꿈은 여기에 저축",        keyword: "돼지저금통",       url: "" },
  { emoji: "👛", name: "복권 보관 지갑",    pitch: "1등 복권은 구겨지면 안 되니까",       keyword: "복권 지갑",        url: "" },
  { emoji: "🍀", name: "네잎클로버 키링",   pitch: "진짜 행운은 들고 다니는 사람 것",     keyword: "네잎클로버 키링",  url: "" },
  { emoji: "🧧", name: "황금 복(福) 스티커", pitch: "지갑에 붙이는 금전운 부적",           keyword: "황금 복 스티커",   url: "" },
  { emoji: "🔐", name: "미니 금고",         pitch: "당첨금 보관 연습부터 미리미리",       keyword: "미니 금고",        url: "" }
];

const PARTNERS_NOTICE = "이 서비스는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.";

// 상품 카드 렌더링 — url 없으면 아무것도 표시하지 않음
function renderLuckyShop(containerId, product, label) {
  const box = document.getElementById(containerId);
  if (!box) return;
  if (!product || !product.url) { box.innerHTML = ""; return; }
  box.innerHTML =
    '<p class="section-label">' + (label || "🎁 오늘의 행운템 챙기기") + '</p>' +
    '<a class="lucky-shop" href="' + product.url + '" target="_blank" rel="noopener sponsored">' +
      '<span class="ls-emoji">' + product.emoji + '</span>' +
      '<span class="ls-body"><span class="ls-name">' + product.name + '</span>' +
      '<span class="ls-pitch">' + product.pitch + '</span></span>' +
      '<span class="ls-go">쿠팡에서 보기 →</span>' +
    '</a>' +
    '<p class="ls-notice">' + PARTNERS_NOTICE + '</p>';
}
