#!/usr/bin/env python3
"""Build the RSOS Language site: tools/site/<page>.html bodies -> docs/<page>.html with shared chrome.

Run from the repo root: python3 tools/build_site.py
docs/editor.html and docs/keyboard.html are standalone tools and are not touched.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "site"
OUT = ROOT / "docs"
REPO = "https://github.com/r-a-elu-architecture/RSOS-Language"
CUE = "https://r-a-elu-architecture.github.io/RSOS-Multimodal-Cue-Framework/"
SITE = "https://r-a-elu-architecture.github.io/RSOS-Language/"

PAGES = [  # file, nav label, <title>, description
    ("index", "Home", "RSOS Language: an executable language for human–AI and AI–AI communication",
     "An executable spatial-symbolic language for human–AI and AI–AI communication, with a cross-domain engine. On "
     "real AI agents it kept every copy of the shared state true and healed every drift without a model call."),
    ("results", "Results", "Results: every pre-registered test, failures included | RSOS Language",
     "A1, A2, A3 and A3b on real LLM agents, HT1 on a person, and the full failure map."),
    ("try", "Try it", "Try it: editor and keyboard | RSOS Language",
     "Compose RSOS programs as paintings in the editor, or key them in with the RSOS keyboard layer."),
    ("paper", "Paper", "Whitepaper, citation and reproduction | RSOS Language",
     "Whitepaper v2 and v1, software DOIs, how to cite and how to reproduce every result."),
    ("programme", "Programme", "Research programme and responsible use | RSOS Language",
     "Twenty-four domains, each with a first measurable test and its safeguards."),
    ("family", "Family", "The RSOS family: language and cue framework | RSOS Language",
     "How the RSOS Language and the RSOS Multimodal Cue Framework relate."),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="family" role="navigation" aria-label="RSOS family"><div class="wrap">
<b>RSOS</b>
<a class="here" href="index.html" aria-current="page">Language</a>
<a href="{cue}">Multimodal Cue Framework ↗</a>
</div></div>
<div class="wrap">
<header class="top">
<a class="mark" href="index.html"><span class="dot" aria-hidden="true"></span>RSOS Language</a>
<nav class="main" aria-label="Site">{nav}</nav>
</header>
</div>
<main id="main">
"""

FOOT = """</main>
<footer><div class="wrap">
<div>R. A. Elu · ORCID <a href="https://orcid.org/0009-0000-1456-2467">0009-0000-1456-2467</a> · Code Apache 2.0 ·
Text CC BY 4.0<br>Research and development software, not a medical device.</div>
<div><a href="{repo}">Source on GitHub</a> · <a href="https://doi.org/10.5281/zenodo.24304403">Whitepaper DOI</a> ·
<a href="{repo}/blob/main/RESPONSIBLE_USE.md">Responsible use</a></div>
</div></footer>
</body>
</html>
"""


def nav_for(current: str) -> str:
    out = []
    for f, label, _, _ in PAGES:
        cur = ' aria-current="page"' if f == current else ""
        out.append(f'<a href="{f}.html"{cur}>{label}</a>')
    return "".join(out)


def main() -> None:
    for f, _, title, desc in PAGES:
        body = (SRC / f"{f}.html").read_text(encoding="utf-8")
        body = body.replace("{REPO}", REPO).replace("{CUE}", CUE)
        url = SITE + ("" if f == "index" else f + ".html")
        html = HEAD.format(title=title, desc=desc, url=url, cue=CUE, nav=nav_for(f)) + body + FOOT.format(repo=REPO)
        assert not re.search(r"\{[A-Z]+\}", html), f"unfilled placeholder in {f}"
        (OUT / f"{f}.html").write_text(html, encoding="utf-8")
        print(f"docs/{f}.html  {len(html):>6} bytes")


if __name__ == "__main__":
    main()
