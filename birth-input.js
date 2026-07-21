/* ===== 생년월일 입력 자동 포맷 =====
 * 숫자만 쭉 입력하면 YYYY-MM-DD로 자동 변환 (19950412 → 1995-04-12)
 * data-birth 속성이 있는 input에 자동 적용
 */
function formatBirthValue(raw) {
  const d = raw.replace(/\D/g, "").slice(0, 8);
  let out = d.slice(0, 4);
  if (d.length > 4) out += "-" + d.slice(4, 6);
  if (d.length > 6) out += "-" + d.slice(6, 8);
  return out;
}

function isValidBirth(v) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
  if (!m) return false;
  const y = +m[1], mo = +m[2], d = +m[3];
  if (y < 1930 || y > new Date().getFullYear()) return false;
  if (mo < 1 || mo > 12) return false;
  return d >= 1 && d <= new Date(y, mo, 0).getDate();
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("input[data-birth]").forEach(function (el) {
    el.addEventListener("input", function () {
      el.value = formatBirthValue(el.value);
    });
  });
});
