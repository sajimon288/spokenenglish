#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one share-friendly PDF of the whole course from index.html.

Usage:
    python3 make_pdf.py

Produces: Spoken-English-All.pdf  (A4, all 17 chapters, embedded fonts)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "index.html")
OUT = os.path.join(BASE, "Spoken-English-All.pdf")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

COVER = """
<section class="chapter cover">
  <div class="cover-in">
    <div class="cover-kicker">BRITISH ENGLISH &middot; FOR MALAYALAM SPEAKERS</div>
    <h1>Spoken English<br>for Malayalam Speakers</h1>
    <p class="cover-ml">മലയാളികൾക്കായുള്ള ബ്രിട്ടീഷ് ഇംഗ്ലീഷ് സ്പീക്കിംഗ് കോഴ്സ്</p>
    <p class="cover-meta">17 അധ്യായങ്ങൾ &middot; ശബ്ദങ്ങൾ, വ്യാകരണം, സംഭാഷണങ്ങൾ,<br>
       പദസമ്പത്ത്, അഭ്യാസങ്ങൾ, 30 ദിവസത്തെ പ്ലാൻ</p>
    <p class="cover-foot">ഒരു ഫയൽ &middot; ഏത് ഫോണിലും തുറക്കാം &middot; ഓഫ്‌ലൈൻ</p>
  </div>
</section>
"""

PRINT_CSS = """
<style>
@page{size:A4;margin:15mm 14mm}
html,body{background:#fff!important;color:#111!important;margin:0!important;
  font-size:11.5pt!important;line-height:1.7!important}
.wrap{display:block!important;padding:0!important;margin:0!important}
main{margin:0!important;max-width:none!important;padding:0!important;display:block!important}
section.chapter{display:block!important;max-width:none!important;margin:0!important;
  animation:none!important;padding:0!important}
section.chapter + section.chapter{break-before:page;page-break-before:always}
.hint,.tick,td .cell,.rt,.cfoot,.done,.homegrid,.menubtn,.iconbtn,.subnav,#progress,.overlay{display:none!important}
.chead{border-bottom:2px solid #ccc;padding-bottom:8px;margin-bottom:18px}
.chead h1{font-size:24pt!important;line-height:1.3}
.kicker{color:#0b5d55;font-weight:700;letter-spacing:.05em;font-size:9pt}
.csub{color:#555;font-size:9pt;letter-spacing:1px}
h2{font-size:15.5pt!important;margin:1.2em 0 .4em;break-after:avoid;page-break-after:avoid}
h3{font-size:12.5pt!important;margin:1em 0 .3em;break-after:avoid;page-break-after:avoid}
h4{font-size:11pt!important;break-after:avoid}
pre,blockquote,tr,img{break-inside:avoid;page-break-inside:avoid}
table{width:100%!important;font-size:9.5pt!important}
.tw{overflow:visible!important}
a{color:#111!important;text-decoration:none!important}
img{max-width:100%!important}
blockquote{background:#f4f2ee!important;border-left:4px solid #0b5d55;padding:8px 12px;margin:10px 0}
ul,ol{padding-left:1.2em}
.cover{text-align:center;padding-top:60mm!important;break-after:page;page-break-after:always}
.cover-in{max-width:150mm;margin:0 auto}
.cover-kicker{letter-spacing:.18em;font-size:9.5pt;color:#0b5d55;font-weight:700}
.cover h1{font-size:33pt!important;line-height:1.25;margin:8mm 0 5mm}
.cover-ml{font-size:13.5pt;color:#333}
.cover-meta{margin-top:12mm;font-size:10.5pt;color:#555;line-height:1.8}
.cover-foot{margin-top:28mm;font-size:10pt;color:#777}
.pagebreak{break-after:page;page-break-after:always}
</style>
"""


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    w = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
    if w:
        return w
    sys.exit("Chrome/Chromium not found. Install Google Chrome to build the PDF.")


def strip_chrome(src):
    def cut(s, start_pat, end_mark):
        m = re.search(start_pat, s)
        if not m:
            return s
        e = s.find(end_mark, m.start())
        if e == -1:
            return s
        return s[:m.start()] + s[e + len(end_mark):]

    src = cut(src, r"<header[^>]*>", "</header>")
    src = cut(src, r"<aside[^>]*>", "</aside>")
    src = cut(src, r'<div[^>]*id=["\']progress["\'][^>]*>', "</div>")
    src = cut(src, r'<div[^>]*class=["\'][^"\']*overlay[^"\']*["\'][^>]*>', "</div>")
    i = src.rfind("<script")
    if i != -1:
        j = src.find("</script>", i)
        if j != -1:
            src = src[:i] + src[j + len("</script>"):]
    return src


def main():
    if not os.path.exists(SRC):
        sys.exit("index.html not found. Run: python3 build.py")

    src = open(SRC, encoding="utf-8").read()
    src = strip_chrome(src)
    src = src.replace("<section class='chapter' id=", "<section class='chapter on' id=")
    src = src.replace("<section class=\"chapter\" id=", "<section class=\"chapter on\" id=")

    m = re.search(r"<main[^>]*>", src)
    if not m:
        sys.exit("Could not find <main> in index.html")
    src = src[:m.end()] + COVER + src[m.end():]
    src = src.replace("</head>", PRINT_CSS + "</head>", 1)

    fd, tmp = tempfile.mkstemp(suffix=".html", prefix="spoken-print-")
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src)

        chrome = find_chrome()
        profile = tempfile.mkdtemp(prefix="chrome-prof-")
        cmd = [
            chrome, "--headless=old", "--disable-gpu", "--no-first-run",
            "--user-data-dir=" + profile,
            "--virtual-time-budget=20000",
            "--no-pdf-header-footer",
            "--print-to-pdf=" + OUT,
            "file://" + tmp,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if not os.path.exists(OUT):
            sys.exit("PDF build failed:\n" + (res.stderr or "")[-800:])
    finally:
        os.path.exists(tmp) and os.remove(tmp)
        shutil.rmtree(profile, ignore_errors=True)

    number_pages(OUT)
    print("PDF written:", OUT, round(os.path.getsize(OUT) / 1024 / 1024, 2), "MB")


def number_pages(path):
    """Add 'page / total' at the bottom of every page except the cover."""
    try:
        import fitz  # PyMuPDF (optional)
    except Exception:
        return
    doc = fitz.open(path)
    total = doc.page_count
    for i in range(1, total):
        page = doc[i]
        w, h = page.rect.width, page.rect.height
        label = "%d / %d" % (i + 1, total)
        page.insert_text((w / 2 - 18, h - 18), label, fontsize=8.5,
                         fontname="helv", color=(0.45, 0.45, 0.45))
    doc.saveIncr()
    doc.close()


if __name__ == "__main__":
    main()
