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
import json
import mimetypes
import pathlib
import re
import sys

VERSION = "1.0"
START = "const REVIEW = "
END = "\n/* ================== END OF EDITABLE BLOCK"
REQUIRED = ["docName", "toRev", "author", "summary", "steps", "stops", "questions"]


def fail(msg):
    sys.exit(f"Could not build the review: {msg}")


def file_name(review):
    clean = lambda t: re.sub(r"\s+", " ", re.sub(r'[\\/:*?"<>|]+', " ", str(t or ""))).strip()
    name, rev = clean(review.get("docName")), clean(review.get("toRev"))
    return f"{name}{' ' + rev if rev else ''} Review.html" if name else "Untitled Review.html"


def embed_images(review, folder):
    for stop in review["stops"]:
        for key in ("img", "fullImg"):
            ref = stop.get(key)
            if not ref or ref.startswith("data:"):
                continue
            path = folder / ref
            if not path.is_file():
                fail(f'image "{ref}" for change "{stop.get("title", "")}" was not found in {folder}')
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            stop[key] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def check(review):
    missing = [k for k in REQUIRED if k not in review]
    if missing:
        fail("review.json is missing " + ", ".join(missing))
    ids = {s.get("id") for s in review["stops"]}
    for i, q in enumerate(review["questions"], 1):
        if q.get("stop") not in ids:
            fail(f'question {i} links to change "{q.get("stop")}", which does not exist')


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
    check(review)
    embed_images(review, folder)
    a, b = html.index(START), html.index(END)
    html = html[:a] + START + json.dumps(review, indent=2, ensure_ascii=False) + ";" + html[b:]
    html = re.sub(r'<meta name="generator" content="[^"]*">',
                  f'<meta name="generator" content="Aūno Review Builder {VERSION} (script)">', html)
    out = folder / file_name(review)
    out.write_text(html, encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
