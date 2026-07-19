/* ===== 별별운세 · 오늘의 행운 아이템 (쿠팡 파트너스) =====
 * url이 빈 문자열("")인 상품은 화면에 표시되지 않습니다.
 * 링크는 쿠팡 파트너스 Open API로 생성 (전 상품 로켓배송, 2026-07-19 기준)
 */

// 오늘의 운세 "행운의 아이템" 12종과 1:1 매칭 (today.html의 ITEMS 배열과 키가 같아야 함)
const LUCKY_PRODUCTS = {
  "손수건":   { emoji: "🤍", name: "포근한 손수건",        pitch: "오늘의 행운을 닦아 간직하세요",        keyword: "손수건 선물세트", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9081691704&itemId=26680645240&vendorItemId=94303015980&traceid=V0-153-421a909efa6e7203&clickBeacon=b1900740-8373-11f1-a3d3-25fee80816c6%7E3&requestid=20260719221354803274305867&token=31850C%7CMIXED" },
  "텀블러":   { emoji: "🥤", name: "행운의 텀블러",        pitch: "좋은 기운을 담아 다니는 하루",          keyword: "보온 텀블러",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8787565536&itemId=28576661002&vendorItemId=95520879434&traceid=V0-153-ed45ffb754e1c867&requestid=20260719221356400303339518&token=31850C%7CMIXED" },
  "동전":     { emoji: "🪙", name: "행운의 동전지갑",      pitch: "굴러들어올 금전운을 담을 자리",        keyword: "동전지갑",        url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8546906774&itemId=24748810716&vendorItemId=91757337738&traceid=V0-153-5752004e5ee299f0&clickBeacon=b3625640-8373-11f1-bcb2-f5a8c0250eca%7E3&requestid=20260719221357904303339780&token=31850C%7CMIXED" },
  "볼펜":     { emoji: "🖊️", name: "술술 풀리는 볼펜",     pitch: "쓰는 일마다 술술 풀리라고",            keyword: "제트스트림 볼펜", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=22559961&itemId=87636101&vendorItemId=3149746208&traceid=V0-153-763c2de4d11aa345&requestid=20260719221359197322602799&token=31850C%7CMIXED" },
  "이어폰":   { emoji: "🎧", name: "행운의 이어폰",        pitch: "좋은 소식이 먼저 들리는 귀",            keyword: "무선 이어폰",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9638528835&itemId=28797461479&vendorItemId=91372701346&traceid=V0-153-cfa0e14e81a750a7&clickBeacon=175d6e00-8374-11f1-80f7-8e3e17efba6c%7E3&requestid=20260719221645641320888386&token=31850C%7CMIXED" },
  "립밤":     { emoji: "💋", name: "말문이 트이는 립밤",   pitch: "오늘은 말 한마디가 행운이 되는 날",    keyword: "립밤",            url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8592995245&itemId=26419181363&vendorItemId=93395116825&traceid=V0-153-68b1194fc66b4aa6&clickBeacon=b5c377c0-8373-11f1-87e9-671f1cdd93eb%7E3&requestid=20260719221401893223303080&token=31850C%7CMIXED" },
  "열쇠고리": { emoji: "🍀", name: "네잎클로버 키링",      pitch: "행운을 열쇠에 채워 다니세요",          keyword: "네잎클로버 키링", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9596365603&itemId=28647349238&vendorItemId=95589927576&traceid=V0-153-0ab5f76c425d30a9&clickBeacon=b6951fa0-8373-11f1-81dc-c37485a0006e%7E3&requestid=20260719221403225151571378&token=31850C%7CMIXED" },
  "책 한 권": { emoji: "📖", name: "마음을 채우는 책",     pitch: "오늘의 운세가 권하는 마음 채우기",      keyword: "베스트셀러 에세이", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8997695998&itemId=26363854918&vendorItemId=81808031957&traceid=V0-153-77814e07f20d0d95&requestid=20260719221404596320881712&token=31850C%7CGM" },
  "우산":     { emoji: "☂️", name: "든든한 자동우산",      pitch: "궂은 일은 미리 막아주는 부적",          keyword: "3단 자동우산",    url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9610287327&itemId=28691625429&vendorItemId=95636281351&traceid=V0-153-867abaf6dd0fb5ed&clickBeacon=b844cb70-8373-11f1-be0e-62b423c41c54%7E3&requestid=20260719221406087083183823&token=31850C%7CMIXED" },
  "사탕":     { emoji: "🍬", name: "달콤한 행운 사탕",     pitch: "입안이 달면 하루도 달아요",            keyword: "수제 사탕",       url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9039478184&itemId=26521129089&vendorItemId=94651388327&traceid=V0-153-a265c17e145de942&clickBeacon=b9138d20-8373-11f1-ad18-e8b48f0640fc%7E3&requestid=20260719221407408022242638&token=31850C%7CMIXED" },
  "머리끈":   { emoji: "🎀", name: "복을 묶는 머리끈",     pitch: "행운은 단단히 묶어둬야 안 도망가요",    keyword: "곱창 머리끈 세트", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8492688966&itemId=24576685859&vendorItemId=91588537664&traceid=V0-153-05e3e0ed4f3484c0&clickBeacon=b9e5d140-8373-11f1-80e8-f9bdfd3d1ace%7E3&requestid=20260719221408768210216650&token=31850C%7CMIXED" },
  "향수":     { emoji: "🌸", name: "좋은 기운의 향수",     pitch: "좋은 향에는 좋은 인연이 따라와요",      keyword: "미니 향수",       url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8201985399&itemId=23515298174&vendorItemId=90541690865&traceid=V0-153-faac29626a5eb3d9&clickBeacon=bade6210-8373-11f1-8c8f-ae5d825a5f00%7E3&requestid=20260719221410360225373928&token=31850C%7CMIXED" }
};

// 로또 페이지용 행운템 (번호 뽑을 때마다 랜덤 1개 노출)
const LOTTO_PRODUCTS = [
  { emoji: "🐷", name: "황금 돼지저금통",   pitch: "당첨 전까지 꿈은 여기에 저축",        keyword: "돼지저금통",       url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8787630944&itemId=25574167955&vendorItemId=92565233984&traceid=V0-153-b9777f8320d09d01&clickBeacon=bba5a9b0-8373-11f1-80a4-c3003be8aa29%7E3&requestid=20260719221411768227456557&token=31850C%7CMIXED" },
  { emoji: "👛", name: "복권 보관 지갑",    pitch: "1등 복권은 구겨지면 안 되니까",       keyword: "복권 지갑",        url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9503989862&itemId=28316446027&vendorItemId=95269048242&traceid=V0-153-7da9b3f7aa2ca590&clickBeacon=bc73f630-8373-11f1-81a9-5e245c9b6ec8%7E3&requestid=20260719221413063006364078&token=31850C%7CMIXED" },
  { emoji: "🍀", name: "네잎클로버 키링",   pitch: "진짜 행운은 들고 다니는 사람 것",     keyword: "네잎클로버 키링",  url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9596365603&itemId=28647349238&vendorItemId=95589927576&traceid=V0-153-0ab5f76c425d30a9&clickBeacon=bd3ec040-8373-11f1-9c6f-8cc8780b42eb%7E3&requestid=20260719221414442128798455&token=31850C%7CMIXED" },
  { emoji: "🧧", name: "황금 복(福) 스티커", pitch: "지갑에 붙이는 금전운 부적",           keyword: "황금 복 스티커",   url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9460006520&itemId=28148376878&vendorItemId=95112987226&traceid=V0-153-b3557231c316575c&clickBeacon=be18f3a0-8373-11f1-8a69-0b6420bbc7dd%7E3&requestid=20260719221415782042648415&token=31850C%7CMIXED" },
  { emoji: "🔐", name: "미니 금고",         pitch: "당첨금 보관 연습부터 미리미리",       keyword: "미니 금고",        url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9046699434&itemId=26550987394&vendorItemId=93658274179&traceid=V0-153-8f3eaf1d239d3ca7&clickBeacon=189c2f90-8374-11f1-97b0-f177c35e1e87%7E3&requestid=20260719221647735227451726&token=31850C%7CMIXED" }
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
