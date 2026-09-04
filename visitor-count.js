/* ===== 방문자 카운터 =====
 * 집계는 항상 하되, 화면 표시는 운영자만 보이게 함.
 *   주소 뒤에 #stats  → 이 브라우저에서 계속 보임
 *   주소 뒤에 #stats-off → 다시 숨김
 * 같은 사람이 새로고침해도 하루 1회만 집계됨.
 *
 * 운영자 본인 방문 제외:
 *   주소 뒤에 #nocount  → 이 브라우저는 앞으로 집계에서 빠짐
 *   주소 뒤에 #count-on → 다시 집계에 포함
 * 관리자 통계 페이지(stats-admin.html)를 열면 자동으로 제외 표시가 붙는다.
 *
 * 2026-08-10: counterapi v1 이 서비스 종료(HTTP 410)돼 집계가 통째로 멈춰 있었다.
 * v2 는 워크스페이스 등록이 필요해 자동 이전이 안 되므로 abacus 로 갈아탔다.
 * 여긴 증가(hit)와 조회(get) 엔드포인트가 분리돼 있어 통계 페이지가
 * 숫자를 부풀리지 않고 읽을 수 있고, 응답도 훨씬 빠르다.
 */
(function () {
  var API = "https://abacus.jasoncameron.dev/";
  var NS = "byeolbyeol-unse";

  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  var d = new Date();
  var dayKey = "d" + d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate());
  var visitFlag = "bb_v_" + dayKey;
  var params = new URLSearchParams(location.search);

  function safeKey(v) {
    return (v || "").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 64);
  }
  var utmSource = safeKey(params.get("utm_source"));
  var campaign = safeKey(params.get("utm_campaign"));
  var contentId = safeKey(params.get("utm_content"));

  function ls(fn, dflt) { try { return fn(); } catch (e) { return dflt; } }

  // 운영자 브라우저인지 판정 (해시로 켜고 끌 수 있음)
  if (location.hash === "#nocount") {
    ls(function () { return localStorage.setItem("bb_admin", "1"); });
  } else if (location.hash === "#count-on") {
    ls(function () { return localStorage.removeItem("bb_admin"); });
  }
  var isAdmin = ls(function () { return localStorage.getItem("bb_admin") === "1"; }, false);

  var firstVisitToday = !ls(function () { return localStorage.getItem(visitFlag); }, "1")
                        && !isAdmin;

  // 유입원 분류: 어디서 들어왔는지 (검색/SNS/직접)
  function trafficSource() {
    // Threads 같은 앱 안 브라우저는 referrer를 비우기도 하므로 UTM을 우선한다.
    if (utmSource) {
      if (/^(threads|instagram)$/.test(utmSource)) return "threads";
      if (/^(naver|google|daum|kakao|telegram|twitter|blog)$/.test(utmSource)) {
        return utmSource === "kakao" ? "daum" : utmSource;
      }
      return "etc";
    }
    var r = document.referrer || "";
    if (!r) return "direct";                        // 직접 입력·즐겨찾기·앱
    var h = "";
    try { h = new URL(r).hostname; } catch (e) { return "etc"; }
    if (h.indexOf("dudtjrdl1243.github.io") >= 0) return null; // 내부 이동은 집계 제외
    if (/naver/.test(h)) return "naver";
    if (/google/.test(h)) return "google";
    if (/daum|kakao/.test(h)) return "daum";
    if (/threads|instagram/.test(h)) return "threads";
    if (/t\.co|twitter|x\.com/.test(h)) return "twitter";
    if (/t\.me|telegram/.test(h)) return "telegram";
    if (/tistory|blog/.test(h)) return "blog";
    return "etc";
  }

  function call(key, increment) {
    return fetch(API + (increment ? "hit/" : "get/") + NS + "/" + key, { cache: "no-store" })
      .then(function (r) {
        if (r.status === 404) return 0;   // 아직 한 번도 안 올라간 카운터
        if (!r.ok) throw new Error(r.status);
        return r.json().then(function (j) {
          return typeof j.value === "number" ? j.value : null;
        });
      })
      .catch(function () { return null; });
  }

  function pageKey() {
    var name = location.pathname.split("/").pop() || "index.html";
    return safeKey(name.replace(/\.html?$/i, "")) || "home";
  }

  // 화면 표시를 기다리게 하지 않고 부가 통계를 차례대로 기록한다.
  function hitSeries(keys) {
    return keys.reduce(function (p, key) {
      return p.then(function () { return call(key, true); });
    }, Promise.resolve());
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
    p.textContent = "👀 오늘 " + (today === null ? "-" : today) + "명 · 전체 " + total + "명"
                    + (isAdmin ? " (내 방문은 집계 제외)" : "");
    footer.appendChild(p);
  }

  Promise.all([call("total", firstVisitToday), call(dayKey, firstVisitToday)])
    .then(function (res) {
      if (firstVisitToday) {
        ls(function () { return localStorage.setItem(visitFlag, "1"); });
        // 오늘 첫 방문일 때 유입원·첫 페이지를 일별/누적으로 함께 남긴다.
        var src = trafficSource();
        var extra = ["page_" + pageKey(), "page_" + pageKey() + "_" + dayKey];
        if (src) extra.push("src_" + src, "src_" + src + "_" + dayKey);
        hitSeries(extra);
      }
      // 전체 방문 집계와 별개로 캠페인 링크는 캠페인당 브라우저 1회 기록한다.
      // 같은 날 먼저 직접 방문한 사람이 나중에 Threads 링크를 눌러도 클릭을 놓치지 않는다.
      if (campaign && !isAdmin) {
        var campaignFlag = "bb_c_" + campaign;
        var firstCampaign = !ls(function () { return localStorage.getItem(campaignFlag); }, "1");
        if (firstCampaign) {
          ls(function () { return localStorage.setItem(campaignFlag, "1"); });
          var campaignKeys = ["camp_" + campaign];
          if (contentId) campaignKeys.push("content_" + contentId);
          hitSeries(campaignKeys);
        }
      }
      render(res[0], res[1]);
    });
})();
