/* ===== 결과 공유하기 =====
 * 모바일: 시스템 공유창(카톡·문자·인스타 등) / PC: 클립보드 복사
 * 각 페이지가 결과를 만들 때 window.SHARE_TEXT를 채워두면 됨
 */
async function shareResult() {
  const text = (window.SHARE_TEXT || document.title) + "\n";
  const url = location.href.split("#")[0].split("?")[0];
  if (navigator.share) {
    try {
      await navigator.share({ text: text + url });
      return;
    } catch (e) {
      if (e && e.name === "AbortError") return; // 사용자가 공유창을 닫음
    }
  }
  try {
    await navigator.clipboard.writeText(text + url);
    alert("결과가 복사됐어요! 카톡 등에 붙여넣어 공유해 보세요 📋");
  } catch (e) {
    prompt("아래 내용을 복사해서 공유하세요", text + url);
  }
}
