# -*- coding: utf-8 -*-
"""Threads 정보글/일상글 보충 문구를 주 1회 만든다.

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
POST_SCRIPT = os.path.join(ROOT, "scripts", "post_threads.py")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
MODEL = os.environ.get("OPENAI_MODEL", "").strip() or "gpt-5-mini"
KST = datetime.timezone(datetime.timedelta(hours=9))


def norm(text):
    return re.sub(r"\s+", "", text or "").lower()


def static_texts():
    """post_threads.py를 실행하지 않고 TIPS/DAILY 리터럴만 안전하게 읽는다."""
    with open(POST_SCRIPT, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in ("TIPS", "DAILY"):
                    found[target.id] = ast.literal_eval(node.value)
    return list(found.get("TIPS", [])) + list(found.get("DAILY", []))


def load_current():
    try:
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("posts", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


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
    prompt = """별별운세 Threads 계정에 앞으로 올릴 새 문구 14개를 만들어줘.
- tips 7개: 저장해두고 쓸 만한 생활·정리·디지털 저위험 팁. 실제로 확실한 내용만.
- daily 7개: 한국어 반말 혼잣말/공감글. 억지 질문과 과장 없이 사람이 쓴 듯 짧게.
- 각 2~4줄, 20~180자. URL, 해시태그, 이모지, 광고, 운세 홍보는 넣지 마.
- 의료·건강·투자·대출·지원금·법률·식품 안전·전기 수리·세제 혼합 팁은 금지.
- 아래 기존 글과 소재나 표현이 겹치지 않게 해.

기존 글:
""" + examples
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "posts": {
                "type": "array", "minItems": 14, "maxItems": 14,
                "items": {
                    "type": "object", "additionalProperties": False,
                    "properties": {
                        "type": {"type": "string", "enum": ["tips", "daily"]},
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
    return (kind in ("tips", "daily") and 20 <= len(text) <= 180
            and not banned.search(text) and norm(text) not in seen)


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

    kinds = {k: sum(1 for p in accepted if p["type"] == k) for k in ("tips", "daily")}
    if kinds["tips"] < 4 or kinds["daily"] < 4:
        print("검수 통과 문구가 부족해 파일을 바꾸지 않습니다:", kinds)
        return

    # 너무 커지지 않게 종류별 최신 90개까지만 보관(약 3개월치 여유분).
    merged = current + accepted
    kept = []
    for kind in ("tips", "daily"):
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
