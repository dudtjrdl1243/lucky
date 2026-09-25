# -*- coding: utf-8 -*-
"""Threads 운세/관계/정보/공감 문구를 주 1회 보충한다.

OPENAI_API_KEY가 없거나 호출이 실패하면 기존 큐를 건드리지 않고 종료한다.
게시 여부는 post_threads.py가 실제 Threads 최근 글을 보고 결정하므로 별도 사용 상태는 없다.
"""
import ast
import datetime
import hashlib
import json
import os
import re
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "threads-generated.json")
INSIGHTS = os.path.join(ROOT, "threads-insights.json")
POST_SCRIPT = os.path.join(ROOT, "scripts", "post_threads.py")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
MODEL = os.environ.get("OPENAI_MODEL", "").strip() or "gpt-5-mini"
KST = datetime.timezone(datetime.timedelta(hours=9))


def norm(text):
    return re.sub(r"\s+", "", text or "").lower()


def static_texts():
    """post_threads.py를 실행하지 않고 정적 문구 리터럴만 안전하게 읽는다."""
    with open(POST_SCRIPT, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in ("TIPS", "DAILY", "RELATION", "FORTUNE"):
                    found[target.id] = ast.literal_eval(node.value)
    texts = list(found.get("TIPS", [])) + list(found.get("DAILY", []))
    texts += [item[0] for item in found.get("RELATION", []) if isinstance(item, tuple) and item]
    texts += [item[0] for item in found.get("FORTUNE", []) if isinstance(item, tuple) and item]
    return texts


def load_current():
    try:
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("posts", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


def performance_context():
    """실제 계정의 조회·대화·클릭 상하위 글을 짧게 요약해 프롬프트에 넣는다."""
    try:
        with open(INSIGHTS, encoding="utf-8") as f:
            posts = json.load(f).get("posts", [])
    except (OSError, ValueError):
        return "아직 참고할 성과 데이터가 없음"
    posts = [p for p in posts if p.get("text") and p.get("type") != "deal"]
    if not posts:
        return "아직 참고할 성과 데이터가 없음"

    def value(p):
        return (int(p.get("link_clicks", 0)) * 500
                + int(p.get("views", 0))
                + int(p.get("score", 0)) * 20)

    top = sorted(posts, key=value, reverse=True)[:8]
    weak_pool = [p for p in posts if int(p.get("views", 0)) >= 5 and p not in top]
    weak = sorted(weak_pool, key=value)[:6]

    def line(p):
        text = re.sub(r"\s+", " ", p.get("text", "")).strip()[:150]
        return "[{} / {}] 조회 {} · 댓글 {} · 클릭 {} | {}".format(
            p.get("type", "?"), p.get("format", "미분류"),
            p.get("views", 0), p.get("replies", 0), p.get("link_clicks", 0), text)

    return "성과 상위(구조만 참고, 문장 복사 금지):\n{}\n\n성과 하위(피할 패턴):\n{}".format(
        "\n".join(line(p) for p in top),
        "\n".join(line(p) for p in weak) if weak else "표본 부족")


def output_text(response):
    for item in response.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return content.get("text", "")
    return ""


def request_posts(existing):
    examples = "\n---\n".join(existing[-60:])
    performance = performance_context()
    prompt = """별별운세 Threads 계정에 앞으로 올릴 새 문구 28개를 만들어줘.
- fortune_tti 4개: 오늘 계산값을 넣을 수 있는 띠 운세 템플릿. {t1}, {t2}, {t3}, {tlast}, {day_name}, {day_elem}만 필요할 때 사용해. 최소 하나의 플레이스홀더를 반드시 넣어.
- fortune_zodiac 3개: 오늘 계산값을 넣을 수 있는 별자리 운세 템플릿. {z1}, {z2}, {z3}, {moon}, {sun_sign}만 필요할 때 사용해. 최소 하나의 플레이스홀더를 반드시 넣어.
- relation 7개: 연락, 표현 방식, 화해, 데이트, 친구 관계처럼 누구나 답하기 쉬운 구체적인 상황 질문. 두 선택지를 자연스럽게 제시하고 댓글로 자기 경험을 말하고 싶게 써줘.
- tips 7개: 연애·친구·직장 관계에서 써볼 수 있는 짧은 대화법이나 생각거리. 심리학적 사실처럼 단정하지 말고, 구체적인 상황과 바로 써볼 한 문장을 중심으로.
- daily 7개: 운, 선택, 관계를 소재로 한 한국어 반말 혼잣말/공감글. 둘 중 하나를 답하기 쉬운 질문형과 담백한 관찰형을 섞고, 억지 질문과 과장 없이 사람이 쓴 듯 짧게.
- 운세 글은 순위를 말하고 끝내지 말고, 가볍게 해볼 행동·현실적인 해석·솔직한 반응 중 하나를 남겨. "여기 OO띠 있음?", "다들 무슨 띠임?", "손 들어봐" 형식은 금지.
- fortune 7개 중 1위·12위 순위를 직접 훅으로 쓰는 글은 최대 2개. 나머지는 상위권, 관심 운(돈/연애/일), 오늘 할 행동, 운세를 대하는 태도처럼 결을 바꿔.
- 질문은 답이 한 단어나 실제 경험으로 나올 만큼 구체적으로. 내용과 무관한 댓글 유도, 과장, 공포, 당첨·성공 보장은 금지.
- 각 2~4줄, 20~180자. URL, 해시태그, 이모지, 광고, 운세 홍보는 넣지 마.
- 의료·건강·투자·대출·지원금·법률·식품 안전·전기 수리·세제 혼합 팁은 금지.
- 성별·혈액형·MBTI·별자리만으로 성격을 단정하거나 갈등을 조장하지 마.
- 성과 상위 문장을 바꿔 쓰지 말고, 왜 반응했는지 구조만 참고해. 표본이 적으므로 조회수 하나를 절대 법칙으로 취급하지 마.
- 아래 기존 글과 소재나 표현이 겹치지 않게 해.

실제 계정 성과:
""" + performance + """

기존 글:
""" + examples
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "posts": {
                "type": "array", "minItems": 28, "maxItems": 28,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "properties": {
                        "type": {"type": "string", "enum": [
                            "fortune_tti", "fortune_zodiac", "relation", "tips", "daily"
                        ]},
                        "text": {"type": "string"},
                    },
                    "required": ["type", "text"],
                },
            }
        },
        "required": ["posts"],
    }
    body = {
        "model": MODEL,
        "instructions": "너는 짧고 자연스러운 한국어 SNS 글을 쓰는 편집자다. 검증하기 어려운 사실은 만들지 않는다.",
        "input": prompt,
        "text": {"format": {"type": "json_schema", "name": "threads_posts", "strict": True, "schema": schema}},
        "store": False,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        response = json.loads(r.read().decode("utf-8"))
    return json.loads(output_text(response)).get("posts", [])


def valid(item, seen):
    kind = item.get("type")
    text = item.get("text", "").strip()
    banned = re.compile(r"https?://|#|의사|약|질병|대출|투자|주식|지원금|법률|표백제.*식초|락스.*(?:식초|세제)")
    allowed = {"fortune_tti", "fortune_zodiac", "relation", "tips", "daily"}
    if kind not in allowed or not (20 <= len(text) <= 180) or banned.search(text) or norm(text) in seen:
        return False
    fields = set(re.findall(r"\{([a-z0-9_]+)\}", text))
    if kind == "fortune_tti":
        return bool(fields) and fields <= {"t1", "t2", "t3", "tlast", "day_name", "day_elem"}
    if kind == "fortune_zodiac":
        return bool(fields) and fields <= {"z1", "z2", "z3", "moon", "sun_sign"}
    return not fields and "{" not in text and "}" not in text


def main():
    if not API_KEY:
        print("OPENAI_API_KEY 없음 - 기존 보충 문구를 유지합니다.")
        return

    current = load_current()
    all_existing = static_texts() + [p.get("text", "") for p in current]
    try:
        new_items = request_posts(all_existing)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError) as e:
        print("문구 생성 실패 - 기존 파일을 유지합니다:", e)
        return

    seen = {norm(x) for x in all_existing}
    accepted = []
    now = datetime.datetime.now(KST).isoformat(timespec="seconds")
    for item in new_items:
        if not valid(item, seen):
            continue
        text = item["text"].strip()
        seen.add(norm(text))
        accepted.append({
            "id": hashlib.sha1(norm(text).encode("utf-8")).hexdigest()[:10],
            "type": item["type"], "text": text, "created_at": now,
        })

    expected = ("fortune_tti", "fortune_zodiac", "relation", "tips", "daily")
    kinds = {k: sum(1 for p in accepted if p["type"] == k) for k in expected}
    minimum = {"fortune_tti": 2, "fortune_zodiac": 2, "relation": 4, "tips": 4, "daily": 4}
    if any(kinds[k] < minimum[k] for k in expected):
        print("검수 통과 문구가 부족해 파일을 바꾸지 않습니다:", kinds)
        return

    # 너무 커지지 않게 종류별 최신 90개까지만 보관(약 3개월치 여유분).
    merged = current + accepted
    kept = []
    for kind in expected:
        kept.extend([p for p in merged if p.get("type") == kind][-90:])
    payload = {"updated_at": now, "posts": kept}
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, OUT)
    print("새 문구 {}개 추가: {}".format(len(accepted), kinds))


if __name__ == "__main__":
    main()
