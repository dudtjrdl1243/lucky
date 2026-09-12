/* ===== 결과 공유하기 =====
 * 모바일: 시스템 공유창(카톡·문자·인스타 등) / PC: 클립보드 복사
 * 각 페이지가 결과를 만들 때 window.SHARE_TEXT를 채워두면 됨
 */
async function shareResult() {
  const text = (window.SHARE_TEXT || document.title) + "\n";
  const url = location.href.split("#")[0].split("?")[0];
  // Windows의 공유창은 메일만 보이는 경우가 많아 오히려 불편하다.
  // 설치된 카카오톡·텔레그램 등이 표시되는 모바일/태블릿에서만 시스템 공유창을 쓴다.
  const mobileShare = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
    (navigator.maxTouchPoints > 1 && window.matchMedia("(max-width: 900px)").matches);
  if (mobileShare && navigator.share) {
    try {
      await navigator.share({ text: text + url });
      return;
    } catch (e) {
      if (e && e.name === "AbortError") return; // 사용자가 공유창을 닫음
    }
  }
  try {
    await navigator.clipboard.writeText(text + url);
    alert("결과와 링크를 복사했어요. 카카오톡이나 텔레그램 대화창에 붙여넣어 주세요 📋");
  } catch (e) {
    prompt("아래 내용을 복사해서 공유하세요", text + url);
  }
}
