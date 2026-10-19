"""Rebuild builder.html and index.html from template.html and the files in src/.

Run from the repository root:  python3 src/build.py
Uses only the Python standard library.
"""
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
tpl = (root / "template.html").read_text(encoding="utf-8")
css = re.search(r"<style>.*?</style>", tpl, re.S).group(0)
sky = [m.group(0) for m in re.finditer(r"<script>.*?</script>", tpl, re.S) if "shared moving wallpaper" in m.group(0)][-1]

builder = (root / "src" / "builder.src.html").read_text(encoding="utf-8")
builder = (builder.replace("__BASE_CSS__", css)
                  .replace("__SKY_SCRIPT__", sky)
                  .replace("__TEMPLATE_JSON__", json.dumps(tpl).replace("</", "<\\/")))
(root / "builder.html").write_text(builder, encoding="utf-8")

index = (root / "src" / "index.src.html").read_text(encoding="utf-8")
(root / "index.html").write_text(index.replace("__BASE_CSS__", css).replace("__SKY_SCRIPT__", sky), encoding="utf-8")
print("Rebuilt builder.html and index.html")
