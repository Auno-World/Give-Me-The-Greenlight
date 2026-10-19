"""Build a finished review page from a review.json file and optional page images.

Usage:
    python3 make_review.py examples/lumen-cell

The folder must contain review.json. For any change that has an "img" value,
put that image file in the same folder; it is built into the review so the
result is a single file. The finished review is saved in the same folder,
named after the document and revision, for example:
    "Incoming Cell Inspection Procedure Rev C Review.html"

Uses only the Python standard library. Nothing is uploaded anywhere.
"""
import base64
import copy
import json
import mimetypes
import pathlib
import re
import sys
import uuid
from urllib.parse import urlparse

VERSION = "1.1"
START = "const REVIEW = "
END = "\n/* ================== END OF EDITABLE BLOCK"
REQUIRED = ["docName", "toRev", "author", "summary", "steps", "stops", "questions"]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def fail(msg):
    sys.exit(f"Could not build the review: {msg}")


def file_name(review):
    clean = lambda t: re.sub(r"\s+", " ", re.sub(r'[\\/:*?"<>|]+', " ", str(t or ""))).strip()
    name, rev = clean(review.get("docName")), clean(review.get("toRev"))
    return f"{name}{' ' + rev if rev else ''} Review.html" if name else "Untitled Review.html"


def embed_images(review, folder):
    root = folder.resolve()
    for stop in review["stops"]:
        for key in ("img", "fullImg"):
            ref = stop.get(key)
            if not ref:
                continue
            if not isinstance(ref, str):
                fail(f'image for change "{stop["title"]}" must be a path or web link')
            if ref.startswith(("data:", "https://", "http://")):
                continue
            candidate = pathlib.Path(ref)
            if candidate.is_absolute() or ".." in candidate.parts:
                fail(f'image "{ref}" must stay inside {folder}')
            path = (root / candidate).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                fail(f'image "{ref}" must stay inside {folder}')
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                fail(f'image "{ref}" must be PNG, JPEG, GIF, or WebP')
            if not path.is_file():
                fail(f'image "{ref}" for change "{stop.get("title", "")}" was not found in {folder}')
            if path.stat().st_size > MAX_IMAGE_SIZE:
                fail(f'image "{ref}" is over 5 MB; use a smaller image')
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            stop[key] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def filled(value):
    return isinstance(value, str) and bool(value.strip())


def check(review):
    missing = [k for k in REQUIRED if k not in review or not review[k]]
    if missing:
        fail("review.json is missing or has empty " + ", ".join(missing))
    for key in ("docName", "toRev", "author"):
        if not filled(review[key]):
            fail(f'{key} must not be empty')
    if not isinstance(review["summary"], list) or any(not isinstance(x, list) or len(x) < 2 or not all(filled(v) for v in x[:2]) for x in review["summary"]):
        fail("summary must contain complete label and text pairs")
    if not isinstance(review["steps"], list) or any(not filled(x) for x in review["steps"]):
        fail("steps must contain non-empty text")
    if not isinstance(review["stops"], list) or not isinstance(review["questions"], list):
        fail("stops and questions must be lists")
    ids = set()
    for i, stop in enumerate(review["stops"], 1):
        if not isinstance(stop, dict) or not filled(stop.get("id")) or stop["id"] in ids:
            fail(f"change {i} needs a unique id")
        ids.add(stop["id"])
        if not filled(stop.get("title")) or not isinstance(stop.get("text"), list) or not stop["text"] or any(not filled(x) for x in stop["text"]):
            fail(f"change {i} needs a title and wording")
        if type(stop.get("page")) is not int or stop["page"] < 1:
            fail(f"change {i} needs a whole page number of 1 or more")
    question_ids = set()
    for i, q in enumerate(review["questions"], 1):
        if not isinstance(q, dict) or not filled(q.get("id")) or q["id"] in question_ids:
            fail(f"question {i} needs a unique id")
        question_ids.add(q["id"])
        if not filled(q.get("q")):
            fail(f"question {i} needs text")
        if q.get("stop") not in ids:
            fail(f'question {i} links to change "{q.get("stop")}", which does not exist')
    pages = review.get("totalPages")
    if pages is not None and (type(pages) is not int or pages < 1 or any(s["page"] > pages for s in review["stops"])):
        fail("totalPages must be a whole number at least as large as every change page")
    link = review.get("fullDocUrl")
    if link and (not isinstance(link, str) or urlparse(link).scheme not in ("http", "https") or not urlparse(link).hostname):
        fail("fullDocUrl must be a web link")


def assign_identity(review):
    changed = False
    if not review.get("reviewId"):
        review["reviewId"] = str(uuid.uuid4())
        changed = True
    for question in review.get("questions", []):
        if isinstance(question, dict) and not question.get("id"):
            question["id"] = str(uuid.uuid4())
            changed = True
    return changed


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = pathlib.Path(sys.argv[1])
    data = folder / "review.json"
    if not data.is_file():
        fail(f"no review.json in {folder}")
    template = pathlib.Path(__file__).resolve().parent / "template.html"
    html = template.read_text(encoding="utf-8")
    review = json.loads(data.read_text(encoding="utf-8"))
    changed = assign_identity(review)
    check(review)
    output_review = copy.deepcopy(review)
    embed_images(output_review, folder)
    if changed:
        data.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    a, b = html.index(START), html.index(END)
    serialized = json.dumps(output_review, indent=2, ensure_ascii=False)
    serialized = serialized.translate(str.maketrans({"<": "\\u003c", ">": "\\u003e", "&": "\\u0026", "\u2028": "\\u2028", "\u2029": "\\u2029"}))
    html = html[:a] + START + serialized + ";" + html[b:]
    html = re.sub(r'<meta name="generator" content="[^"]*">',
                  f'<meta name="generator" content="Aūno Review Builder {VERSION} (script)">', html)
    out = folder / file_name(review)
    out.write_text(html, encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
