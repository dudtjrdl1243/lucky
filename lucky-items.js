/* ===== 별별운세 · 오늘의 행운 아이템 (쿠팡 파트너스) =====
 * url이 빈 문자열("")인 상품은 화면에 표시되지 않습니다.
 * 링크는 쿠팡 파트너스 Open API로 생성 (2026-07-20 재선정: 브랜드 국민템 위주)
 */

// 오늘의 운세 "행운의 아이템" 12종과 1:1 매칭 (today.html의 ITEMS 배열과 키가 같아야 함)
const LUCKY_PRODUCTS = {
  "손수건":   { emoji: "🤍", name: "닥스 손수건 선물세트",   pitch: "오늘의 행운을 닦아 간직하세요",        keyword: "손수건 선물세트", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9081691704&itemId=26680645240&vendorItemId=94303015980&traceid=V0-153-421a909efa6e7203&clickBeacon=b1900740-8373-11f1-a3d3-25fee80816c6%7E3&requestid=20260719221354803274305867&token=31850C%7CMIXED" },
  "텀블러":   { emoji: "🥤", name: "1L 대용량 보온 텀블러",  pitch: "좋은 기운을 가득 담아 다니는 하루",    keyword: "보온 텀블러",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8407779103&itemId=24307962138&vendorItemId=91323851985&traceid=V0-153-8a768ff37072c8cd&clickBeacon=9fb28580-83cc-11f1-b656-a5d387e08fa5%7E3&requestid=20260720085030010269933711&token=31850C%7CMIXED" },
  "동전":     { emoji: "🪙", name: "황금 금원보 세트",       pitch: "재물운을 부르는 풍수 황금 동전",        keyword: "황금 금원보",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8625276862&itemId=25025483494&vendorItemId=92030235442&traceid=V0-153-551842545124946a&clickBeacon=b6c45da0-83ce-11f1-8c53-d91502b3293e%7E3&requestid=20260720090527758133196670&token=31850C%7CMIXED" },
  "볼펜":     { emoji: "🖊️", name: "제트스트림 볼펜",        pitch: "쓰는 일마다 술술 풀리라고",            keyword: "제트스트림 볼펜", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=22559961&itemId=87636101&vendorItemId=3149746208&traceid=V0-153-763c2de4d11aa345&requestid=20260719221359197322602799&token=31850C%7CMIXED" },
  "이어폰":   { emoji: "🎧", name: "QCY 블루투스 이어폰",    pitch: "좋은 소식이 먼저 들리는 귀",            keyword: "QCY 이어폰",      url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9181779721&itemId=27078563811&vendorItemId=94046839272&traceid=V0-153-33d07cfe78b6a16a&clickBeacon=a1ae7c90-83cc-11f1-b1b7-d2177ea42793%7E3&requestid=20260720085033324274305875&token=31850C%7CMIXED" },
  "립밤":     { emoji: "💋", name: "바세린 립테라피 4개입",  pitch: "오늘은 말 한마디가 행운이 되는 날",    keyword: "바세린 립밤",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=1946659295&itemId=20559880136&vendorItemId=94724614628&traceid=V0-153-34c257b8cc02cbff&clickBeacon=a2a90930-83cc-11f1-a778-16e3bc314155%7E3&requestid=20260720085035055269934902&token=31850C%7CMIXED" },
  "열쇠고리": { emoji: "🍀", name: "네잎클로버 키링",        pitch: "행운을 열쇠에 채워 다니세요",          keyword: "네잎클로버 키링", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9596365603&itemId=28647349238&vendorItemId=95589927576&traceid=V0-153-0ab5f76c425d30a9&clickBeacon=b6951fa0-8373-11f1-81dc-c37485a0006e%7E3&requestid=20260719221403225151571378&token=31850C%7CMIXED" },
  "책 한 권": { emoji: "📖", name: "베스트셀러 에세이",      pitch: "오늘의 운세가 권하는 마음 채우기",      keyword: "베스트셀러 에세이", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8997695998&itemId=26363854918&vendorItemId=81808031957&traceid=V0-153-77814e07f20d0d95&requestid=20260719221404596320881712&token=31850C%7CGM" },
  "우산":     { emoji: "☂️", name: "125cm 대형 자동우산",    pitch: "궂은 일은 미리 막아주는 부적",          keyword: "3단 자동우산",    url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9610287327&itemId=28691625429&vendorItemId=95636281351&traceid=V0-153-867abaf6dd0fb5ed&clickBeacon=b844cb70-8373-11f1-be0e-62b423c41c54%7E3&requestid=20260719221406087083183823&token=31850C%7CMIXED" },
  "사탕":     { emoji: "🍬", name: "12가지맛 캔디 대용량",   pitch: "입안이 달면 하루도 달아요",            keyword: "캔디 대용량",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9238855064&itemId=27317787078&vendorItemId=94808892599&traceid=V0-153-13a311b1359ec2e2&clickBeacon=a3a4f560-83cc-11f1-a2c6-34b18e02161f%7E3&requestid=20260720085036665112273792&token=31850C%7CMIXED" },
  "머리끈":   { emoji: "🎀", name: "스크런치 7종 세트",      pitch: "행운은 단단히 묶어둬야 안 도망가요",    keyword: "곱창 머리끈 세트", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8492688966&itemId=24576685859&vendorItemId=91588537664&traceid=V0-153-05e3e0ed4f3484c0&clickBeacon=b9e5d140-8373-11f1-80e8-f9bdfd3d1ace%7E3&requestid=20260719221408768210216650&token=31850C%7CMIXED" },
  "향수":     { emoji: "🌸", name: "포맨트 시그니처 퍼퓸",   pitch: "좋은 향에는 좋은 인연이 따라와요",      keyword: "포맨트 퍼퓸",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9528029336&itemId=25437665642&vendorItemId=95740716473&traceid=V0-153-90a15399e8e81ed1&requestid=20260720085038284274307386&token=31850C%7CMIXED" }
};

// 로또 페이지용 행운템 (번호 뽑을 때마다 랜덤 1개 노출)
const LOTTO_PRODUCTS = [
  { emoji: "🐷", name: "파스텔 돼지저금통",   pitch: "당첨 전까지 꿈은 여기에 저축",          keyword: "돼지저금통",      url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=8787630944&itemId=25574167955&vendorItemId=92565233984&traceid=V0-153-b9777f8320d09d01&clickBeacon=bba5a9b0-8373-11f1-80a4-c3003be8aa29%7E3&requestid=20260719221411768227456557&token=31850C%7CMIXED" },
  { emoji: "🎰", name: "로또번호 추첨기",     pitch: "손맛으로 굴려 뽑는 나만의 황금 번호",   keyword: "로또번호 추첨기", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9307017296&itemId=27574798881&vendorItemId=94666082007&traceid=V0-153-e8238b1f8e3fc37a&clickBeacon=a59f3ec0-83cc-11f1-bb1d-0074c790735c%7E3&requestid=20260720085039961274307826&token=31850C%7CMIXED" },
  { emoji: "🍀", name: "네잎클로버 키링",     pitch: "진짜 행운은 들고 다니는 사람 것",       keyword: "네잎클로버 키링", url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9596365603&itemId=28647349238&vendorItemId=95589927576&traceid=V0-153-0ab5f76c425d30a9&clickBeacon=bd3ec040-8373-11f1-9c6f-8cc8780b42eb%7E3&requestid=20260719221414442128798455&token=31850C%7CMIXED" },
  { emoji: "🐸", name: "황금 재물 두꺼비",    pitch: "책상 위 명당에 모시는 금전운",          keyword: "황금 두꺼비",     url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9237306784&itemId=27311567909&vendorItemId=94278014123&traceid=V0-153-e6b900eaabf98561&clickBeacon=a6a8bf80-83cc-11f1-a69b-71dca3a3da17%7E3&requestid=20260720085041667185817110&token=31850C%7CMIXED" },
  { emoji: "🔐", name: "미니 금고",           pitch: "당첨금 보관 연습부터 미리미리",         keyword: "미니 금고",       url: "https://link.coupang.com/re/AFFSDP?lptag=AF9276380&pageKey=9046699434&itemId=26550987394&vendorItemId=93658274179&traceid=V0-153-8f3eaf1d239d3ca7&clickBeacon=189c2f90-8374-11f1-97b0-f177c35e1e87%7E3&requestid=20260719221647735227451726&token=31850C%7CMIXED" }
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
