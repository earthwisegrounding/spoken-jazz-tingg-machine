#!/usr/bin/env python3
"""Build the site from _src/site.src.html.

Emits two things from one source:
  index.html          -- standalone page, assets loaded from ./assets/
  _dist/artifact.html -- body-only page with every asset inlined as a data URI
"""
import base64, mimetypes, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src" / "site.src.html"
ASSETS = ROOT / "assets"
DIST = ROOT / "_dist"

TOKEN = re.compile(r"\{\{ASSET:([^}]+)\}\}")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Spoken Jazz &amp; the tingg* Machine — an epicsodic jazz audio musical by Bub Pratt. Two acts, twenty-two scenes, one Remington portable, and a renaissance in a drab Navy town outside Seattle.">
<meta name="theme-color" content="#0d0b0a">
<meta property="og:title" content="Spoken Jazz &amp; the tingg* Machine">
<meta property="og:description" content="An epicsodic jazz audio musical by Bub Pratt. Bremerton, Washington, spring 2000.">
<meta property="og:type" content="book">
<meta property="og:image" content="assets/cover.jpg">
<link rel="icon" href="assets/emblem.jpg">
<style>*{margin:0}html,body{background:#0d0b0a}</style>
</head>
<body>
"""
FOOT = "\n</body>\n</html>\n"


def data_uri(name: str) -> str:
    p = ASSETS / name
    if not p.exists():
        sys.exit(f"missing asset: {p}")
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def main() -> None:
    src = SRC.read_text(encoding="utf-8")

    linked = TOKEN.sub(lambda m: f"assets/{m.group(1)}", src)
    (ROOT / "index.html").write_text(HEAD + linked + FOOT, encoding="utf-8")

    DIST.mkdir(exist_ok=True)
    inlined = TOKEN.sub(lambda m: data_uri(m.group(1)), src)
    (DIST / "artifact.html").write_text(inlined, encoding="utf-8")

    # QA-only copy: honours ?y=<px> so headless screenshots land where asked,
    # and ?side=b so the setlist drum can be shot on its far face.
    qa = ROOT / "_qa"
    qa.mkdir(exist_ok=True)
    qa_head = HEAD.replace("<head>", '<head>\n<base href="/">')
    # Headless Chrome paints a blank frame after a programmatic scroll, so the
    # QA build shifts the document with a negative margin instead.
    qa_js = (
        "<script>(function(){"
        # the drum takes 1.15s to turn, so the flip goes first and the shot
        # budget covers it
        "if(/[?&]side=b/.test(location.search)){"
        "var t=document.getElementById('tab-b'); if(t) t.click();}"
        "var m=/[?&]y=(\\d+)/.exec(location.search); if(!m) return;"
        "var s=document.createElement('style');"
        "s.textContent='body{margin-top:-'+m[1]+'px!important}';"
        "document.body.appendChild(s);"
        "document.querySelectorAll('.rise').forEach(function(e){e.classList.add('in');});"
        "document.querySelectorAll('.mis').forEach(function(e){e.classList.add('reg');});"
        "var b=document.createElement('div');"
        "b.style.cssText='position:fixed;left:0;bottom:0;z-index:99999;background:#0f0;color:#000;"
        "font:11px monospace;padding:2px 5px';"
        "b.textContent=innerWidth+'x'+innerHeight+' sw'+document.documentElement.scrollWidth;"
        "document.body.appendChild(b);"
        "})();</script>"
    )
    (qa / "index.html").write_text(qa_head + linked + qa_js + FOOT, encoding="utf-8")

    # Chrome will not open a window narrower than ~500px, so phone widths are
    # captured through an iframe of the exact viewport size instead.
    (qa / "frame.html").write_text(
        "<!doctype html><meta charset=utf-8>"
        "<style>html,body{margin:0;background:#222}"
        "body{display:flex;justify-content:center}"
        "iframe{border:0;display:block}</style>"
        "<script>"
        "var q=new URLSearchParams(location.search);"
        "var w=q.get('w')||390,h=q.get('h')||844,y=q.get('y')||0,sd=q.get('side')||'a';"
        "document.write('<iframe width='+w+' height='+h+"
        "' src=\"/_qa/index.html?y='+y+'&side='+sd+'&r='+Math.random()+'\"></iframe>');"
        "</script>",
        encoding="utf-8",
    )

    kb = lambda p: f"{p.stat().st_size/1024:.0f} KB"
    print("index.html         ", kb(ROOT / "index.html"))
    print("_dist/artifact.html", kb(DIST / "artifact.html"))


if __name__ == "__main__":
    main()
