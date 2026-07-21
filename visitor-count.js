/* ===== 방문자 카운터 =====
 * 집계는 항상 하되, 화면 표시는 운영자만 보이게 함.
 *   주소 뒤에 #stats  → 이 브라우저에서 계속 보임
 *   주소 뒤에 #stats-off → 다시 숨김
 * 같은 사람이 새로고침해도 하루 1회만 집계됨.
 */
(function () {
  var API = "https://api.counterapi.dev/v1/byeolbyeol-unse/";

  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  var d = new Date();
  var dayKey = "d" + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate());
  var visitFlag = "bb_v_" + dayKey;

  function ls(fn, dflt) { try { return fn(); } catch (e) { return dflt; } }

  var firstVisitToday = !ls(function () { return localStorage.getItem(visitFlag); }, "1");

  function call(key, increment) {
    return fetch(API + key + (increment ? "/up" : "/"), { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (j) { return typeof j.count === "number" ? j.count : null; })
      .catch(function () { return null; });
  }

  function shouldShow() {
    if (location.hash === "#stats") {
      ls(function () { return localStorage.setItem("bb_stats", "1"); });
      return true;
    }
    if (location.hash === "#stats-off") {
      ls(function () { return localStorage.removeItem("bb_stats"); });
      return false;
    }
    return ls(function () { return localStorage.getItem("bb_stats") === "1"; }, false);
  }

  function render(total, today) {
    if (!shouldShow() || total === null) return;
    var footer = document.querySelector("footer.site");
    if (!footer) return;
    var p = document.createElement("p");
    p.style.cssText = "margin-top:6px;font-size:12px;opacity:.65";
    p.textContent = "👀 오늘 " + (today === null ? "-" : today) + "명 · 전체 " + total + "명";
    footer.appendChild(p);
  }

  Promise.all([call("total", firstVisitToday), call(dayKey, firstVisitToday)])
    .then(function (res) {
      if (firstVisitToday) ls(function () { return localStorage.setItem(visitFlag, "1"); });
      render(res[0], res[1]);
    });
})();
