#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build index.html from the markdown chapters (no external dependencies)."""

import re, html, json, os

BASE = os.path.dirname(os.path.abspath(__file__))

CHAPTERS = [
    ("home", "README.md", "തുടക്കം", "Start Here", "ഈ കോഴ്സ് എങ്ങനെയാണ്, എന്താണ് ഉള്ളത്"),
    ("ch00", "00-how-to-use.md", "എങ്ങനെ ഉപയോഗിക്കണം", "How to Use", "90 ദിവസത്തെ പ്ലാൻ, ദൈനംദിന ശീലങ്ങൾ"),
    ("plan", "14-30-day-plan.md", "30 ദിവസത്തെ പ്ലാൻ", "One-Month Sprint", "ഒരു മാസം · ദിവസം തോറും · പരിശോധന"),
    ("ai", "15-ai-partner.md", "AI സംഭാഷണ പങ്കാളി", "AI Speaking Partner", "Prompts · ആഴ്ചയിലെ പരിശോധന"),
    ("wb", "11-speaking-workbook.md", "സ്പീക്കിംഗ് വർക്ക്ബുക്ക്", "12-Week Workbook", "ദിവസവും 25 മിനിറ്റ് · 84 ടാസ്ക് · ഫീഡ്ബാക്ക്"),
    ("vid", "12-video-library.md", "വീഡിയോ ലൈബ്രറി", "Video Library", "വീഡിയോ · സിനിമ · സീരീസ് · ലിങ്കുകൾ"),
    ("ch01", "01-the-sounds-of-british-english.md", "ബ്രിട്ടീഷ് ശബ്ദങ്ങൾ", "The Sounds", "44 ശബ്ദങ്ങൾ, മലയാളിക്കുള്ള 8 പ്രശ്നങ്ങൾ"),
    ("ch02", "02-first-sentences.md", "ആദ്യ വാക്യങ്ങൾ", "First Sentences", "യൂണിറ്റ് 1–10: സംസാരത്തിന്റെ അടിത്തറ"),
    ("gram", "13-easy-grammar.md", "എളുപ്പ വ്യാകരണം", "Grammar Rescue", "10 Patterns · 14 ദിവസം"),
    ("ch03", "03-grammar-step-by-step.md", "വ്യാകരണം", "Grammar", "20 ചെറിയ പാഠങ്ങൾ"),
    ("ch04", "04-dialogues.md", "സംഭാഷണങ്ങൾ", "Dialogues", "24 ദൈനംദിന സന്ദർഭങ്ങൾ"),
    ("ch05", "05-vocabulary.md", "പദസമ്പത്ത്", "Vocabulary", "40 വിഷയങ്ങൾ · 1200+ വാക്കുകൾ"),
    ("ch06", "06-british-english-guide.md", "ബ്രിട്ടീഷ് ഗൈഡ്", "British English", "അക്ഷരവിന്യാസം, മര്യാദ, സംസ്കാരം"),
    ("ch07", "07-pronunciation-and-fluency.md", "ഉച്ചാരണവും ഒഴുക്കും", "Pronunciation", "ഊന്നൽ, താളം, ഷാഡോയിംഗ്"),
    ("ch08", "08-drills-and-answer-key.md", "അഭ്യാസങ്ങൾ", "Drills", "100+ അഭ്യാസങ്ങൾ · 30 ദിവസത്തെ ചലഞ്ച്"),
    ("ch09", "09-malayalam-speaker-mistakes.md", "60 തെറ്റുകൾ", "Common Mistakes", "മലയാളികൾ വരുത്തുന്ന തെറ്റുകൾ"),
    ("ch10", "10-appendices.md", "അനുബന്ധങ്ങൾ", "Appendices", "ക്രിയകൾ, സംഖ്യകൾ, 100 വാക്യങ്ങൾ"),
]

LINKMAP = {c[1]: "#" + c[0] for c in CHAPTERS}
LINKMAP["README.md"] = "#home"

# ---------------------------------------------------------------- inline

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(t):
    t = esc(t)
    def _link(m):
        href = LINKMAP.get(m.group(2), m.group(2))
        extra = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        return '<a href="%s"%s>%s</a>' % (href, extra, m.group(1))
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t

def slugify(s):
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]

# ---------------------------------------------------------------- audio

MALAYALAM = re.compile("[\u0D00-\u0D7F]")
FILE_EXT = re.compile(r"\.(md|html?|pdf|js|py|css|json|zip|txt|mp3|mp4)\b", re.I)
URLISH = re.compile(r"(https?://|www\.|@|\.(com|org|net|co\.uk|in|io)\b)", re.I)
SPEAKABLE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9'’\-.,?!():;/\"%&—–… ]*$")

def speakable(raw, max_words=9):
    """Return clean British-English text worth speaking, or None."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)   # links -> label
    t = re.sub(r"[*`]", "", t)
    t = html.unescape(t).strip()
    if not t or len(t) > 90:
        return None
    if MALAYALAM.search(t):
        # keep the English column of "English     മലയാളം" lines
        head = re.split(r"\s{2,}", t)[0].strip()
        if head and not MALAYALAM.search(head) and re.search(r"[A-Za-z]", head):
            t = head
        else:
            return None
    if FILE_EXT.search(t):
        return None
    if URLISH.search(t):
        return None
    if not re.search(r"[A-Za-z]", t):
        return None
    if not SPEAKABLE.match(t):
        return None
    if len(t.split()) > max_words:
        return None
    t = re.sub(r"\s+", " ", t).strip()
    if t.endswith(":"):
        return None
    # drop a short speaker label ("A:", "Woman:", "Ravi:") - not spoken
    m = re.match(r"^[A-Z][A-Za-z .'\-]{0,14}:\s+(.+)$", t)
    if m:
        t = m.group(1).strip()
    if len(t) < 1:
        return None
    return t

def spk(text):
    """Speaker button markup (British English)."""
    return ("<button type='button' class='spk' data-say=\"%s\" "
            "aria-label='ഉച്ചാരണം കേൾക്കുക' title='British English pronunciation'></button>"
            % html.escape(text, quote=True))

QUOTED = re.compile(r'[“"]([^“”"]{2,110})[”"]')
PAREN = re.compile(r"\(([^()]{2,110})\)")

def english_of(s):
    """Keep only ASCII English from a mixed Malayalam/English fragment."""
    s = re.sub(r"[\u0D00-\u0D7F]", " ", s)
    s = re.sub(r"[^\x20-\x7E]", " ", s)       # IPA, arrows, curly quotes
    s = re.sub(r"[|_\\]+", " ", s)
    s = re.sub(r"\s*/\s*", ", ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(' .,;:-"\'()[]')
    if URLISH.search(s) or FILE_EXT.search(s):
        return None
    words = [w for w in s.split() if len(w) > 1 or w.lower() in ("a", "i")]
    t = " ".join(words).strip(" ,;:-")
    if t.endswith(":"):
        return None
    if len(t.split()) < 2 or not re.search(r"[A-Za-z]{2}", t):
        return None
    if len(t) > 190:
        return None
    return t

def para_speech(raw):
    """Best English text to read for a paragraph that may mix Malayalam."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    t = re.sub(r"[*`]", "", t)
    t = html.unescape(t)
    if not MALAYALAM.search(t):
        s = speakable(t, 120)
        return s or english_of(t)
    parts = [english_of(q) for q in QUOTED.findall(t)]
    parts += [english_of(p) for p in PAREN.findall(t)]
    parts = [p for p in parts if p]
    if not parts:
        # cut the text at Malayalam stretches, keep English pieces
        tmp = re.sub(r"[\u0D00-\u0D7F]+", "  ", t)
        tmp = re.sub(r"[^\x20-\x7E]+", "  ", tmp)
        for chunk in re.split(r"\s{2,}", tmp):
            s = english_of(chunk)
            if s:
                parts.append(s)
    if not parts:
        return None
    seen, keep = set(), []
    for p in parts:
        if p.lower() in seen:
            continue
        seen.add(p.lower()); keep.append(p)
    txt = ". ".join(keep)
    return txt if len(txt) <= 240 else None

MDNAME = re.compile(r"\b(?:[0-9]{2}-[a-z0-9-]+|README)\.md\b")

def cardnum_guess(cid):
    return {"home": "", "wb": "W", "vid": "V", "gram": "G", "plan": "30", "ai": "AI"}.get(
        cid, cid.replace("ch", ""))

MDLABEL = {}
SPECIAL_LABEL = {
    "home": "തുടക്കം",
    "wb": "വർക്ക്ബുക്ക്",
    "vid": "വീഡിയോ ലൈബ്രറി",
    "gram": "എളുപ്പ വ്യാകരണം",
    "plan": "30 ദിവസത്തെ പ്ലാൻ",
    "ai": "AI സംഭാഷണ പങ്കാളി",
}
for c in CHAPTERS:
    MDLABEL[c[1]] = SPECIAL_LABEL.get(c[0]) or ("അധ്യായം " + cardnum_guess(c[0]))

def humanize(html_text):
    """Remove .md file names from the visible page."""
    html_text = re.sub(r"<code>((?:[0-9]{2}-[a-z0-9-]+|README)\.md)</code>",
                       lambda m: MDLABEL.get(m.group(1), "അധ്യായം"), html_text)
    html_text = MDNAME.sub(lambda m: MDLABEL.get(m.group(0), "അധ്യായം"), html_text)
    html_text = html_text.replace("<th>ഫയൽ</th>", "<th>അധ്യായം</th>")
    return html_text

# ---------------------------------------------------------------- blocks

def parse_table(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) < 2:
        return None
    aligns = []
    for c in rows[1]:
        c = c.strip()
        if c.startswith(":") and c.endswith(":"):
            aligns.append("center")
        elif c.endswith(":"):
            aligns.append("right")
        else:
            aligns.append("")
    narrow = len(rows[0]) == 2 and all(
        len(re.sub(r"[*`\[\]]", "", (r[0] if r else ""))) <= 4 for r in rows[2:])
    out = ["<div class='tw'><table%s>" % (" class='narrow'" if narrow else "")]
    out.append("<thead><tr>")
    for i, c in enumerate(rows[0]):
        al = (" class='ta'" if i < len(aligns) and aligns[i] else "")
        out.append("<th%s>%s</th>" % (al, inline(c)))
    out.append("</tr></thead><tbody>")
    for r in rows[2:]:
        out.append("<tr>")
        for i in range(len(rows[0])):
            c = r[i] if i < len(r) else ""
            al = (" class='ta'" if i < len(aligns) and aligns[i] else "")
            s = speakable(c, 16)
            if not s:
                s = para_speech(c)
            pre = spk(s) if s else ""
            out.append("<td%s>%s%s</td>" % (al, pre, inline(c)))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)

def parse_code(lines):
    parts = []
    for line in lines:
        s = speakable(line, 40)
        if s:
            parts.append("<span class='say' data-say=\"%s\">%s</span>%s" % (
                html.escape(s, quote=True), esc(line), spk(s)))
        else:
            parts.append(esc(line))
    return "<pre><code>%s</code></pre>" % "\n".join(parts)

def parse_blockquote(lines):
    raw = [re.sub(r"^>\s?", "", l) for l in lines]
    groups, cur = [], []
    for l in raw:
        if not l.strip():
            if cur:
                groups.append(" ".join(cur)); cur = []
            continue
        if re.match(r"^\*\*[^*]+:\*\*", l) and cur:
            groups.append(" ".join(cur)); cur = [l]
        else:
            cur.append(l)
    if cur:
        groups.append(" ".join(cur))
    body = []
    for g in groups:
        if not g.strip():
            continue
        full = speakable(g, 40)
        s = full or para_speech(g)
        if full:
            body.append("<p class='dlg'><span class='say' data-say=\"%s\">%s</span>%s</p>" % (
                html.escape(s, quote=True), inline(g), spk(s)))
        elif s:
            body.append("<p>%s%s</p>" % (inline(g), spk(s)))
        else:
            body.append("<p>%s</p>" % inline(g))
    return "<blockquote>%s</blockquote>" % "".join(body)

def convert(md, cid):
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    hcount = 0
    skipped_title = False
    toc = []
    while i < n:
        ln = lines[i]

        if ln.startswith("```"):
            j = i + 1
            buf = []
            while j < n and not lines[j].startswith("```"):
                buf.append(lines[j]); j += 1
            out.append(parse_code(buf))
            i = j + 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            text = m.group(2).strip()
            if lvl == 1 and not skipped_title:
                skipped_title = True
                i += 1
                continue
            hcount += 1
            hid = "%s-h%d" % (cid, hcount)
            shown = lvl if lvl >= 2 else 2
            if lvl == 1:
                shown = 2
            out.append("<h%d id='%s'>%s</h%d>" % (shown, hid, inline(text), shown))
            if lvl <= 2 and not text.startswith("സ്പോക്കൺ"):
                toc.append((lvl, text, hid))
            i += 1
            continue

        if ln.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            j = i
            buf = []
            while j < n and lines[j].strip().startswith("|"):
                buf.append(lines[j]); j += 1
            out.append(parse_table(buf))
            i = j
            continue

        if ln.startswith(">"):
            j = i
            buf = []
            while j < n and (lines[j].startswith(">") or (not lines[j].strip() and j + 1 < n and lines[j + 1].startswith(">"))):
                buf.append(lines[j]); j += 1
            out.append(parse_blockquote(buf))
            i = j
            continue

        if re.match(r"^\s*([-*]|\d+\.)\s+", ln):
            j = i
            items = []
            ordered = bool(re.match(r"^\s*\d+\.", ln))
            while j < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[j]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[j])); j += 1
            tag = "ol" if ordered else "ul"
            lis = []
            for x in items:
                full = speakable(x, 40)
                s = full or para_speech(x)
                if full:
                    lis.append("<li>%s%s</li>" % (spk(s), inline(x)))
                elif s:
                    lis.append("<li>%s%s</li>" % (inline(x), spk(s)))
                else:
                    lis.append("<li>%s</li>" % inline(x))
            out.append("<%s>%s</%s>" % (tag, "".join(lis), tag))
            i = j
            continue

        if re.match(r"^\s*(---+|\*\*\*+)\s*$", ln):
            out.append("<hr>")
            i += 1
            continue

        if not ln.strip():
            i += 1
            continue

        j = i
        buf = []
        while j < n and lines[j].strip() and not re.match(r"^(#{1,4})\s|^```|^>|^\s*\|", lines[j]) \
                and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[j]) and not re.match(r"^\s*---+$", lines[j]):
            buf.append(lines[j].strip()); j += 1
        text = " ".join(buf)
        s = para_speech(text)
        out.append("<p>%s%s</p>" % (inline(text), spk(s) if s else ""))
        i = j

    # choose toc level
    h1s = [t for (l, t, h) in toc if l == 1]
    use = 1 if len(h1s) > 1 else 2
    toc = [(l, t, h) for (l, t, h) in toc if l <= use]
    return "".join(out), toc

# ---------------------------------------------------------------- build

KICKER = {"home": "", "wb": "വർക്ക്ബുക്ക്", "vid": "വീഡിയോ", "gram": "വ്യാകരണം 0", "plan": "പ്ലാൻ", "ai": "AI"}
def cardnum(cid):
    if cid == "home": return "—"
    if cid == "ch00": return "00"
    if cid == "wb": return "W"
    if cid == "vid": return "V"
    if cid == "gram": return "G"
    if cid == "plan": return "30"
    if cid == "ai": return "AI"
    return cid.replace("ch", "")

sections, navdata = [], []
SRC_DIRS = [BASE, os.path.join(os.path.dirname(BASE), "spoken-eng-src")]

def read_md(fn):
    for d in SRC_DIRS:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return f.read()
    raise SystemExit("markdown source not found: " + fn)

for cid, fn, title, sub, desc in CHAPTERS:
    md = read_md(fn)
    body, toc = convert(md, cid)
    body = humanize(body)
    sections.append("<section class='chapter' id='%s' data-title='%s'>%s%s</section>" % (
        cid, esc(title),
        ("<div class='chead'><div class='kicker'>%s</div><h1>%s</h1><div class='csub'>%s</div></div>" % (
            KICKER.get(cid, cid.upper().replace("CH", "അധ്യായം ")), title, sub)) if cid != "home" else "",
        body))
    navdata.append({"id": cid, "title": title, "sub": sub, "desc": desc,
                    "toc": [{"level": l, "text": t, "id": h} for (l, t, h) in toc]})

# home chapter grid
grid = "".join(
    "<a class='card' href='#%s' data-go='%s'><span class='cnum'>%s</span>"
    "<span class='ct'>%s</span><span class='cs'>%s</span><span class='cd'>%s</span></a>" % (
        c["id"], c["id"],
        cardnum(c["id"]),
        c["title"], c["sub"], c["desc"])
    for c in navdata if c["id"] != "home")

HINT = ("<div class='hint'><div><b>☰</b> പട്ടിക തുറക്കുക</div>"
        "<div><b>🔍</b> അധ്യായം തിരയുക <kbd>/</kbd></div>"
        "<div><b>A+</b> അക്ഷരം വലുതാക്കുക</div>"
        "<div><b>🔊</b> വാക്ക് / വാക്യം ഉച്ചരിക്കുക</div>"
        "<div><b>☾</b> ഇരുണ്ട / വെളുത്ത</div>"
        "<div><b>PDF</b> പ്രിന്റ് / സേവ്</div>"
        "<div><b>✓</b> വിഭാഗങ്ങൾ ടിക്ക് ചെയ്യാം</div>"
        "<div><b>← →</b> അടുത്ത അധ്യായം</div></div>")
sections[0] = sections[0].replace("<section class='chapter' id='home' data-title='തുടക്കം'>",
    "<section class='chapter' id='home' data-title='തുടക്കം'>" + HINT, 1)

sections[0] = sections[0].replace("</section>",
    "<div class='homegrid'><div class='gridhead'>അധ്യായങ്ങൾ</div>%s</div></section>" % grid, 1)

CSS = r"""
:root{
  --fs:18px; --bg:#fbfaf7; --panel:#ffffff; --ink:#221f1b; --muted:#6b6560;
  --line:#e6e1d8; --accent:#0b5d55; --accent2:#b7791f; --soft:#f2efe8;
  --code:#f4f1ea; --shadow:0 1px 2px rgba(0,0,0,.05),0 8px 24px rgba(0,0,0,.05);
  --sidebar:300px;
}
html[data-theme="sepia"]{--bg:#f6efdf;--panel:#fbf6ea;--ink:#2e2a22;--muted:#6b6252;--line:#e2d7bf;--soft:#efe6d2;--code:#efe6d2;--accent:#0b5d55;}
html[data-theme="dark"]{--bg:#16181a;--panel:#1d2022;--ink:#e7e4de;--muted:#a09a92;--line:#2e3335;--soft:#23272a;--code:#1b1e20;--accent:#4fb3a4;--accent2:#d8a657;--shadow:none;}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-size:var(--fs);line-height:1.85;
  font-family:"Noto Sans Malayalam","Manjari","Malayalam Sangam MN","Noto Sans","Segoe UI",system-ui,-apple-system,sans-serif;
  -webkit-text-size-adjust:100%;}
a{color:var(--accent);text-underline-offset:3px}
a:hover{color:var(--accent2)}

/* ---------- top bar ---------- */
header{position:fixed;top:0;left:0;right:0;height:58px;z-index:60;display:flex;align-items:center;gap:10px;
  padding:0 14px;background:var(--panel);background:color-mix(in srgb,var(--panel) 92%,transparent);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line)}
.brand{font-weight:700;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}
.brand small{display:block;font-weight:500;font-size:11px;color:var(--muted);letter-spacing:.6px}
header .sp{flex:1}
.iconbtn{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:10px;
  min-width:38px;height:36px;padding:0 10px;font-size:14px;cursor:pointer;display:inline-flex;
  align-items:center;justify-content:center;gap:6px}
.iconbtn:hover{border-color:var(--accent)}
.pdfbtn{font-size:11px;font-weight:700;letter-spacing:.04em}
#progress{position:fixed;top:58px;left:0;height:3px;width:0;background:var(--accent);z-index:61;transition:width .1s}

/* ---------- layout ---------- */
.wrap{display:flex;padding-top:58px;min-height:100vh}
aside{width:var(--sidebar);flex:0 0 var(--sidebar);position:fixed;top:58px;bottom:0;left:0;overflow-y:auto;
  background:var(--panel);border-right:1px solid var(--line);padding:14px 10px 60px;z-index:50}
.search{width:100%;padding:9px 12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);
  color:var(--ink);font-size:14px;font-family:inherit;margin-bottom:10px}
.search:focus{outline:2px solid color-mix(in srgb,var(--accent) 35%,transparent);border-color:var(--accent)}
#results{display:none;margin:-4px 0 10px;border:1px solid var(--line);border-radius:10px;background:var(--bg);overflow:hidden;max-height:45vh;overflow-y:auto}
#results a{display:block;padding:8px 10px;text-decoration:none;color:var(--ink);border-bottom:1px solid var(--line);line-height:1.5}
#results a:last-child{border-bottom:0}
#results a:hover{background:var(--soft)}
#results .rt{display:block;font-weight:700;font-size:12px;color:var(--accent)}
#results .rs{display:block;font-size:11.5px;color:var(--muted);margin-top:2px}
#results .rnone{padding:10px;font-size:12px;color:var(--muted)}
.navi{display:block;padding:8px 10px;border-radius:9px;color:var(--ink);text-decoration:none;font-size:14px;
  line-height:1.45;margin-bottom:2px;border-left:3px solid transparent}
.navi .n{font-size:10.5px;color:var(--muted);display:block;letter-spacing:.8px}
.navi:hover{background:var(--soft)}
.navi.active{background:var(--soft);border-left-color:var(--accent);font-weight:600}
.navi.read .nt::after{content:" ✓";color:var(--accent);font-size:12px}
.navi{position:relative}
.nc{position:absolute;right:9px;top:50%;transform:translateY(-50%);font-size:9.5px;color:var(--muted);font-weight:700;letter-spacing:.3px}
.nc.full{color:var(--accent)}

section.chapter h2,section.chapter h3{position:relative;padding-left:1.7em}
.tick{position:absolute;left:0;top:.5em;width:1.15em;height:1.15em;padding:0;border-radius:50%;
  border:1.6px solid var(--line);border-color:color-mix(in srgb,var(--muted) 55%,transparent);background:var(--panel);cursor:pointer;display:flex;align-items:center;
  justify-content:center;color:#fff;transition:background .15s,border-color .15s;line-height:1}
.tick::before{content:"";position:absolute;inset:-9px;border-radius:50%}
.tick::after{content:"✓";font-size:.62em;font-weight:700;opacity:0}
.tick:hover{border-color:var(--accent)}
h2.is-done>.tick,h3.is-done>.tick{background:var(--accent);border-color:var(--accent)}
h2.is-done>.tick::after,h3.is-done>.tick::after{opacity:1}
h2.is-done,h3.is-done{color:var(--muted)}
td .cell{width:100%;min-height:30px;border:1px solid var(--line);border-radius:7px;background:transparent;
  cursor:pointer;color:var(--accent);font-weight:700;font-size:15px;transition:.15s}
td .cell::after{content:"";}
td .cell.on{background:var(--accent);border-color:var(--accent)}
td .cell.on::after{content:"✓";color:#fff}
td .cell:hover{border-color:var(--accent)}
.rt{width:18px;height:18px;min-width:18px;border-radius:50%;border:1.5px solid color-mix(in srgb,var(--muted) 55%,transparent);
  background:transparent;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  margin-right:7px;vertical-align:-3px;font-size:10px;color:#fff;padding:0}
.rt{position:relative}
.rt::before{content:"";position:absolute;inset:-8px;border-radius:50%}
.rt:hover{border-color:var(--accent)}
.tick:focus-visible,.rt:focus-visible,td .cell:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.rt.on{background:var(--accent);border-color:var(--accent)}
.rt.on::after{content:"✓"}
@media print{.tick,td .cell,.rt{display:none!important}section.chapter h2,section.chapter h3{padding-left:0}}
h2,h3,h4{scroll-margin-top:84px}
#home .chead{display:none}
.subnav{margin:0 0 8px 16px;display:none}
.navi.active + .subnav{display:block}
.subnav a{display:block;padding:5px 8px;font-size:12.5px;color:var(--muted);text-decoration:none;
  border-left:1px solid var(--line);line-height:1.5}
.subnav a:hover{color:var(--accent);border-left-color:var(--accent)}
main{margin-left:var(--sidebar);flex:1;min-width:0;padding:26px 30px 90px}
section.chapter{display:none;max-width:860px;margin:0 auto;animation:fade .18s ease}
section.chapter.on{display:block}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}

/* ---------- content ---------- */
.chead{border-bottom:2px solid var(--soft);padding-bottom:14px;margin-bottom:26px}
.kicker{font-size:11px;letter-spacing:.04em;color:var(--accent);font-weight:700}
.chead h1{font-size:1.9em;line-height:1.35;margin:6px 0 4px}
.csub{color:var(--muted);font-size:.82em;letter-spacing:1.5px;text-transform:uppercase}
h2{font-size:1.4em;line-height:1.45;margin:1.8em 0 .6em;padding-bottom:.3em;border-bottom:1px solid var(--line)}
h3{font-size:1.15em;margin:1.6em 0 .5em;color:var(--accent)}
h4{font-size:1.02em;margin:1.3em 0 .4em}
p{margin:.7em 0}
ul,ol{padding-left:1.4em;margin:.7em 0}
li{margin:.3em 0}
hr{border:0;border-top:1px solid var(--line);margin:2.2em 0}
blockquote{margin:1.2em 0;padding:14px 18px;background:var(--soft);border-left:4px solid var(--accent);
  border-radius:0 10px 10px 0}
blockquote p{margin:.35em 0}
blockquote p:first-child{margin-top:0}
blockquote p:last-child{margin-bottom:0}
strong{font-weight:700}
code{background:var(--code);padding:.1em .4em;border-radius:5px;font-size:.9em;
  font-family:"SF Mono",Menlo,Consolas,monospace}
pre{background:var(--code);padding:16px 18px;border-radius:12px;overflow-x:auto;line-height:1.7;
  border:1px solid var(--line);margin:1.1em 0;font-size:.86em}
pre code{background:none;padding:0;font-size:1em;white-space:pre;display:block;
  font-family:"SF Mono",Menlo,Consolas,monospace}
.tw{overflow-x:auto;margin:1.2em 0;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:.9em;background:var(--panel)}
th,td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.6}
th{background:var(--soft);font-weight:700;font-size:.92em;white-space:nowrap}
tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:color-mix(in srgb,var(--soft) 45%,transparent)}
.ta{text-align:right}
.narrow td:first-child,.narrow th:first-child{width:1%;white-space:nowrap}
.tw{scrollbar-width:thin}

/* ---------- pronunciation ---------- */
:root{
  --spk-on:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M11 5 6 9H2v6h4l5 4V5z'/%3E%3Cpath d='M15.5 8.5a5 5 0 0 1 0 7'/%3E%3Cpath d='M18.5 5.5a9 9 0 0 1 0 13'/%3E%3C/svg%3E");
  --spk-off:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M11 5 6 9H2v6h4l5 4V5z'/%3E%3Cpath d='m16 9 5 5'/%3E%3Cpath d='m21 9-5 5'/%3E%3C/svg%3E");
}
.spk{border:0;background:transparent;color:var(--accent);cursor:pointer;width:1.6em;height:1.6em;
  padding:0;margin-right:5px;border-radius:7px;opacity:.6;vertical-align:-.3em;transition:.15s;
  display:inline-flex;align-items:center;justify-content:center}
.spk::before{content:"";width:.95em;height:.95em;background:currentColor;
  -webkit-mask:var(--spk-on) center/contain no-repeat;mask:var(--spk-on) center/contain no-repeat}
.spk:hover{opacity:1;background:var(--soft)}
.spk.on{opacity:1;background:var(--accent);color:#fff}
td .spk{margin-right:6px}
p>.spk:last-child,li>.spk:last-child,blockquote p>.spk:last-child{margin-left:7px;margin-right:0}
pre .spk{width:1.4em;height:1.4em;margin-left:8px;vertical-align:-.25em;opacity:.5}
pre .spk:hover{background:transparent;color:var(--accent2)}
pre .say{cursor:pointer;border-radius:3px}
pre .say:hover{background:color-mix(in srgb,var(--accent) 12%,transparent)}
pre .say.speaking{background:color-mix(in srgb,var(--accent) 20%,transparent)}
#soundbtn::before{content:"";width:17px;height:17px;background:currentColor;
  -webkit-mask:var(--spk-on) center/contain no-repeat;mask:var(--spk-on) center/contain no-repeat}
#soundbtn.off{color:var(--muted);border-style:dashed}
#soundbtn.off::before{-webkit-mask-image:var(--spk-off);mask-image:var(--spk-off)}
body.sound-off .spk{display:none}
body.sound-off pre .say{cursor:auto}
body.sound-off pre .say:hover{background:none}

/* ---------- voice settings ---------- */
.voicepanel{position:fixed;top:64px;right:10px;z-index:80;width:258px;display:none;
  background:var(--panel);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);padding:12px 14px}
.voicepanel.on{display:block}
.vp-t{font-size:10.5px;letter-spacing:.07em;color:var(--muted);font-weight:700;margin-bottom:4px}
.vp-now{font-size:11px;color:var(--accent);margin:-2px 0 6px;min-height:14px}
.vp-row{display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:13px;padding:8px 0;border-top:1px solid var(--line)}
.vp-row:first-of-type{border-top:0}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;flex:none}
.seg button{border:0;background:transparent;color:var(--ink);font:inherit;font-size:12px;padding:6px 10px;cursor:pointer}
.seg button + button{border-left:1px solid var(--line)}
.seg button.on{background:var(--accent);color:#fff}
.vp-note{font-size:11px;color:var(--muted);line-height:1.6;margin-top:8px;border-top:1px solid var(--line);padding-top:8px}
@media (max-width:520px){.voicepanel{left:10px;right:10px;width:auto}}

/* ---------- home ---------- */
.hint{display:flex;flex-wrap:wrap;gap:8px 18px;padding:12px 14px;margin:0 0 22px;border:1px solid var(--line);
  border-radius:12px;background:var(--panel);font-size:12.5px;color:var(--muted)}
.hint b{color:var(--accent);font-size:13px}
.hint kbd{border:1px solid var(--line);border-radius:5px;padding:0 5px;font-size:11px;background:var(--bg)}
.homegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:26px 0}
.gridhead{grid-column:1/-1;font-size:12px;letter-spacing:.06em;color:var(--muted);font-weight:700;margin-bottom:2px}
.card{display:flex;flex-direction:column;gap:2px;padding:16px;border:1px solid var(--line);border-radius:14px;
  background:var(--panel);text-decoration:none;color:var(--ink);box-shadow:var(--shadow);transition:.15s}
.card:hover{transform:translateY(-2px);border-color:var(--accent)}
.cnum{font-size:11px;color:var(--accent);font-weight:700;letter-spacing:1.5px}
.ct{font-weight:700;font-size:1.02em}
.cs{font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase}
.cd{font-size:.78em;color:var(--muted);line-height:1.6;margin-top:4px}

/* ---------- chapter footer ---------- */
.cfoot{display:flex;justify-content:space-between;gap:12px;margin-top:60px;padding-top:22px;border-top:1px solid var(--line)}
.cfoot a{flex:1;padding:14px 16px;border:1px solid var(--line);border-radius:12px;text-decoration:none;
  background:var(--panel);font-size:14px;line-height:1.5}
.cfoot a:hover{border-color:var(--accent)}
.cfoot .lbl{display:block;font-size:11px;color:var(--muted);letter-spacing:.04em}
.cfoot a.nx{text-align:right}
.done{display:flex;align-items:center;gap:10px;margin:34px 0 0;padding:12px 16px;border:1px dashed var(--line);
  border-radius:12px;font-size:14px;color:var(--muted)}
.done input{width:18px;height:18px;accent-color:var(--accent)}

/* ---------- mobile ---------- */
.overlay{display:none;position:fixed;inset:58px 0 0;background:rgba(0,0,0,.35);z-index:45}
.menubtn{display:none}
@media (max-width:900px){
  aside{transform:translateX(-100%);transition:transform .22s;width:86%;max-width:340px;flex-basis:auto}
  aside.open{transform:none;box-shadow:0 0 40px rgba(0,0,0,.25)}
  main{margin-left:0;padding:20px 16px 80px}
  .menubtn{display:inline-flex}
  .overlay.on{display:block}
  body{line-height:1.9}
  h2{font-size:1.28em}
  .chead h1{font-size:1.5em}
  pre{font-size:.78em}
  .brand small{display:none}
}
@media (max-width:520px){
  .hide-sm{display:none}
  .cfoot{flex-direction:column}
}
@media print{
  header,aside,.overlay,#progress,.cfoot,.done,.homegrid,.menubtn{display:none!important}
  .spk{display:none!important}
  pre .say{background:none!important}
  body{background:#fff;color:#000;font-size:10.5pt;line-height:1.65}
  .wrap{display:block;padding:0}
  main{margin:0;max-width:none;padding:0}
  section.chapter{max-width:none}
  section.chapter.on{display:block!important}
  h2,h3{page-break-after:avoid}
  pre,table,blockquote{page-break-inside:avoid}
  a{color:#000;text-decoration:none}
  .chead h1{font-size:20pt}
}
"""

JS = r"""
const NAV = __NAV__;
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const store = {
  get(k, d){ try{ const v = localStorage.getItem(k); return v===null?d:v; }catch(e){ return d; } },
  set(k, v){ try{ localStorage.setItem(k, v); }catch(e){} }
};

/* ---------- theme ---------- */
const themes = ['light','sepia','dark'];
let theme = store.get('theme','light');
if(!themes.includes(theme)) theme='light';
document.documentElement.dataset.theme = theme;
const tbtn = $('#tbtn');
function paintTheme(){ tbtn.textContent = theme==='dark'?'☀︎':theme==='sepia'?'◐':'☾'; }
paintTheme();
tbtn.onclick = () => { theme = themes[(themes.indexOf(theme)+1)%3];
  document.documentElement.dataset.theme = theme; store.set('theme',theme); paintTheme(); };

/* ---------- font size ---------- */
let fs = parseInt(store.get('fs','18'),10); if(isNaN(fs)) fs=18;
document.documentElement.style.setProperty('--fs', fs+'px');
$('#fplus').onclick = () => { fs=Math.min(24,fs+1); document.documentElement.style.setProperty('--fs',fs+'px'); store.set('fs',fs); };
$('#fminus').onclick = () => { fs=Math.max(15,fs-1); document.documentElement.style.setProperty('--fs',fs+'px'); store.set('fs',fs); };

/* ---------- sidebar ---------- */
const side = $('#side');
const navbox = $('#navbox');
function buildNav(){
  navbox.innerHTML = '';
  NAV.forEach(c => {
    const a = document.createElement('a');
    a.className = 'navi'; a.href = '#'+c.id; a.dataset.id = c.id;
    a.innerHTML = '<span class="n">'+(c.id==='home'?'HOME':c.id.replace('ch','CHAPTER '))+'</span>'
                + '<span class="nt">'+c.title+'</span><span class="nc"></span>';
    a.addEventListener('click', () => { closeSide(); });
    navbox.appendChild(a);
    if(c.toc.length){
      const d = document.createElement('div');
      d.className='subnav'; d.dataset.for=c.id;
      c.toc.forEach(t=>{
        const s = document.createElement('a');
        s.href = '#'+t.id; s.textContent = t.text.replace(/\*\*/g,'');
        s.addEventListener('click', ()=>closeSide());
        d.appendChild(s);
      });
      navbox.appendChild(d);
    }
  });
}
buildNav();

function openSide(){ side.classList.add('open'); $('#ov').classList.add('on'); }
function closeSide(){ side.classList.remove('open'); $('#ov').classList.remove('on'); }
$('#menubtn').onclick = openSide;
$('#ov').onclick = closeSide;

/* ---------- routing ---------- */
function route(){
  const raw = (location.hash||'#home').slice(1) || 'home';
  let id = raw, deep = null;
  if(!NAV.some(c=>c.id===id)){
    const m = raw.match(/^(ch\d+|home)(-h\d+)$/);
    if(m){ id = m[1]; deep = raw; } else { id = 'home'; }
  }
  $$('section.chapter').forEach(s => s.classList.toggle('on', s.id===id));
  $$('.navi').forEach(a => a.classList.toggle('active', a.dataset.id===id));
  const ch = NAV.find(c=>c.id===id);
  $('#crumb').textContent = id==='home' ? 'Spoken English for Malayalam Speakers' : ch.title;
  document.title = (id==='home'?'Spoken English':'%s — Spoken English'.replace('%s',ch.title));
  addFooters(id);
  markRead();
  if(deep){
    const el = document.getElementById(deep);
    if(el){ requestAnimationFrame(()=> el.scrollIntoView({block:'start'})); return; }
  }
  window.scrollTo({top:0, behavior:'instant' in window ? 'instant' : 'auto'});
}
window.addEventListener('hashchange', route);

function markRead(){
  $$('.navi').forEach(a=>a.classList.toggle('read', store.get('done:'+a.dataset.id,'')==='1'));
}
function addFooters(id){
  const idx = NAV.findIndex(c=>c.id===id);
  if(id==='home') return;
  const sec = document.getElementById(id);
  if(!sec || sec.querySelector('.cfoot')) return;
  const prev = NAV[idx-1], next = NAV[idx+1];
  const done = document.createElement('label');
  done.className='done';
  done.innerHTML = '<input type="checkbox" data-done="'+id+'"> <span>ഈ അധ്യായം പഠിച്ചു</span>';
  const box = document.createElement('div');
  box.className='cfoot';
  box.innerHTML =
    (prev? '<a href="#'+prev.id+'"><span class="lbl">← മുൻപത്തേത്</span>'+prev.title+'</a>' : '<a href="#home"><span class="lbl">←</span>തുടക്കം</a>')
    + (next? '<a class="nx" href="#'+next.id+'"><span class="lbl">അടുത്തത് →</span>'+next.title+'</a>' : '<a class="nx" href="#home"><span class="lbl">തീർന്നു</span>തുടക്കത്തിലേക്ക്</a>');
  sec.appendChild(done);
  sec.appendChild(box);
  const cb = done.querySelector('input');
  cb.checked = store.get('done:'+id,'')==='1';
  cb.addEventListener('change', ()=>{ store.set('done:'+id, cb.checked?'1':'0'); markRead(); });
}

/* ---------- progress ---------- */
window.addEventListener('scroll', ()=>{
  const h = document.documentElement.scrollHeight - window.innerHeight;
  $('#progress').style.width = (h>0 ? (window.scrollY/h)*100 : 0) + '%';
});

/* ---------- search (titles + full text) ---------- */
const search = $('#search');
const results = $('#results');

function esc(t){ return t.replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }

function restoreNav(){
  $$('.navi').forEach(a=>a.style.display='block');
  $$('.subnav').forEach(d=>{ d.style.display=''; });
  results.style.display='none'; results.innerHTML='';
}

const textCache = new Map();
function chapterText(c){
  if(!textCache.has(c.id)){
    const sec = document.getElementById(c.id);
    const parts = [];
    if(sec) sec.querySelectorAll('h2,h3,h4,p,li,td,th,pre').forEach(el=>{
      parts.push(el.innerText || el.textContent || '');
    });
    textCache.set(c.id, parts.join(' ').replace(/\s+/g,' '));
  }
  return textCache.get(c.id);
}
function snippet(txt, q){
  const i = txt.toLowerCase().indexOf(q);
  if(i < 0) return '';
  const a = Math.max(0, i-35), b = Math.min(txt.length, i+q.length+45);
  let out = txt.slice(a,b);
  if(out.length > 90) out = out.slice(0,90);
  return (a>0?'…':'') + out + (b<txt.length?'…':'');
}

function runSearch(){
  const q = search.value.trim().toLowerCase();
  if(!q){ restoreNav(); return; }

  const hits = [];
  NAV.forEach(c=>{
    const inTitle = (c.title+' '+c.sub+' '+c.desc).toLowerCase().includes(q)
                 || (c.toc||[]).some(t=>t.text.toLowerCase().includes(q));
    if(inTitle){ hits.push({c, snip: c.desc, title:true}); return; }
    if(c.id === 'home') return;
    const txt = chapterText(c);
    const lower = txt.toLowerCase();
    if(lower.includes(q)){
      const count = lower.split(q).length - 1;
      hits.push({c, snip: snippet(txt, q), title:false, count});
    }
  });
  hits.sort((a,b)=> (b.title?1:0)-(a.title?1:0) || (b.count||0)-(a.count||0));

  const ids = new Set(hits.map(h=>h.c.id));
  $$('.navi').forEach(a=> a.style.display = ids.has(a.dataset.id) ? 'block' : 'none');
  $$('.subnav').forEach(d=> d.style.display='none');

  if(!hits.length){
    results.innerHTML = '<div class="rnone">ഒന്നും കണ്ടെത്തിയില്ല. വേറെ വാക്ക് ശ്രമിക്കുക.</div>';
  } else {
    results.innerHTML = hits.slice(0,10).map((h,i)=>
      '<a href="#'+h.c.id+'" data-q="'+esc(search.value.trim())+'" data-i="'+i+'">'
      + '<span class="rt">'+esc(h.c.title)+'</span>'
      + '<span class="rs">'+esc(h.snip)+'</span></a>').join('');
  }
  results.style.display='block';
}

function scrollToText(cid, q){
  const sec = document.getElementById(cid);
  if(!sec || !q) return;
  const w = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT, null);
  let n;
  while((n = w.nextNode())){
    const idx = n.nodeValue.toLowerCase().indexOf(q);
    if(idx > -1){
      const r = document.createRange();
      r.setStart(n, idx); r.setEnd(n, idx + q.length);
      const top = r.getBoundingClientRect().top + window.scrollY - 110;
      window.scrollTo({top, behavior:'smooth'});
      return;
    }
  }
}

search.addEventListener('input', runSearch);
results.addEventListener('click', e=>{
  const a = e.target.closest('a[data-q]');
  if(!a) return;
  e.preventDefault();
  const q = a.dataset.q;
  const id = a.getAttribute('href').slice(1);
  closeSide();
  location.hash = id;
  requestAnimationFrame(()=> requestAnimationFrame(()=> scrollToText(id, q.toLowerCase())));
  search.value='';
  runSearch();
});
search.addEventListener('keydown', e=>{
  if(e.key==='Enter'){
    const first = results.querySelector('a[data-q]') || $$('.navi').find(a=>a.style.display!=='none');
    if(first) first.click ? first.click() : (location.hash = first.dataset.id);
  }
  if(e.key==='Escape'){ search.value=''; runSearch(); search.blur(); }
});
document.addEventListener('keydown', e=>{
  if(e.key==='/' && document.activeElement!==search){ e.preventDefault(); search.focus(); return; }
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA') return;
  const cur = (location.hash||'#home').slice(1);
  const i = NAV.findIndex(c=>c.id===cur);
  if(e.key==='ArrowRight' && i>-1 && NAV[i+1]){ location.hash = NAV[i+1].id; }
  if(e.key==='ArrowLeft' && i>0){ location.hash = NAV[i-1].id; }
});

/* ---------- tick marks ---------- */
function isTicked(k){ return store.get('tick:'+k,'')==='1'; }
function setTicked(k,v){ store.set('tick:'+k, v?'1':'0'); }

function initTicks(){
  $$('section.chapter h2, section.chapter h3').forEach(h=>{
    if(h.querySelector(':scope > .tick')) return;
    const b=document.createElement('button');
    b.type='button'; b.className='tick';
    b.setAttribute('aria-label','ഈ ഭാഗം പൂർത്തിയായി');
    b.dataset.key='hd:'+h.id;
    const on = isTicked(b.dataset.key);
    b.setAttribute('aria-pressed', on?'true':'false');
    if(on) h.classList.add('is-done');
    b.addEventListener('click', ev=>{
      ev.preventDefault(); ev.stopPropagation();
      const now = !h.classList.contains('is-done');
      h.classList.toggle('is-done', now);
      b.setAttribute('aria-pressed', now?'true':'false');
      setTicked(b.dataset.key, now);
      updateCounts();
    });
    h.prepend(b);
  });
}

function initTrackers(){
  $$('section.chapter').forEach(sec=>{
    let i=0;
    sec.querySelectorAll('td').forEach(td=>{
      if(td.textContent.trim() !== '☐') return;
      const key = 'cell:'+sec.id+':'+(i++);
      const b=document.createElement('button');
      b.type='button'; b.className='cell';
      b.setAttribute('aria-label','ടിക്ക് ചെയ്യുക');
      if(isTicked(key)) b.classList.add('on');
      b.addEventListener('click', ()=>{
        const now = !b.classList.contains('on');
        b.classList.toggle('on', now);
        setTicked(key, now);
      });
      td.textContent='';
      td.appendChild(b);
    });
  });
}

function initRowTicks(){
  $$('section.chapter').forEach(sec=>{
    const tables=[...sec.querySelectorAll('table')];
    tables.forEach((t,ti)=>{
      const th=t.querySelector('th');
      const head=(th?th.textContent:'').trim();
      if(head!=='ദിവസം' && head!=='ആഴ്ച') return;
      if(t.textContent.includes('☐')) return;
      [...t.querySelectorAll('tbody tr')].forEach((tr,ri)=>{
        const td=tr.querySelector('td');
        if(!td || td.querySelector('.rt')) return;
        const key='row:'+sec.id+':'+ti+':'+ri;
        const b=document.createElement('button');
        b.type='button'; b.className='rt';
        b.setAttribute('aria-label','ഈ വരി പൂർത്തിയായി');
        if(isTicked(key)) b.classList.add('on');
        b.addEventListener('click', ev=>{
          ev.preventDefault(); ev.stopPropagation();
          const now=!b.classList.contains('on');
          b.classList.toggle('on', now);
          setTicked(key, now);
        });
        td.prepend(b);
      });
    });
  });
}

function updateCounts(){
  NAV.forEach(c=>{
    const sec=document.getElementById(c.id);
    const badge=document.querySelector('.navi[data-id="'+c.id+'"] .nc');
    if(!sec||!badge) return;
    const hs=[...sec.querySelectorAll('h2,h3')];
    const done=hs.filter(h=>h.classList.contains('is-done')).length;
    badge.textContent = done ? done+'/'+hs.length : '';
    badge.classList.toggle('full', done>0 && done===hs.length);
  });
}

/* ---------- British pronunciation ---------- */
const synth = window.speechSynthesis || null;
const FEMALE = /female|woman|kate|serena|stephanie|samantha|victoria|fiona|moira|karen|kathy|tessa|shelley|sandy|flo\b|grandma|libby|maisie|emma|amy|zira|hazel|susan|allison|ava|aria|jenny|michelle|sonia/i;
const MALE = /male|man\b|daniel|arthur|alex|fred|ralph|albert|eddy|reed|rocko|grandpa|rishi|oliver|george|aaron|gordon/i;
const NOVELTY = /bad news|bells|boing|bubbles|cellos|good news|organ|superstar|trinoids|whisper|wobble|zarvox|bahh|jester|albert|ralph|fred|grandma|grandpa/i;
const NICE = /flo|shelley|sandy|kate|serena|samantha|daniel|google uk english/i;

function pickVoice(gender){
  if(!synth) return null;
  const vs = synth.getVoices().filter(v => /^en/i.test(v.lang));
  const score = v => {
    let s = /^en[-_]gb/i.test(v.lang) ? 100 : 20;
    if(gender === 'f'){
      if(FEMALE.test(v.name)) s += 45;
      if(MALE.test(v.name)) s -= 35;
    } else {
      if(MALE.test(v.name)) s += 45;
      if(FEMALE.test(v.name)) s -= 35;
    }
    if(NOVELTY.test(v.name)) s -= 60;
    if(NICE.test(v.name)) s += 6;
    return s;
  };
  return vs.slice().sort((a,b) => score(b) - score(a))[0] || null;
}

let soundOn = store.get('sound','1') === '1';
let voiceGender = store.get('voice','f') === 'm' ? 'm' : 'f';
let slowMode = store.get('slow','0') === '1';
const sbtn = $('#soundbtn');
const vpanel = $('#voicepanel');

function paintVoiceName(){
  const v = pickVoice(voiceGender);
  const el = $('#vpnow');
  if(el) el.textContent = v ? (v.name + ' · ' + v.lang) : 'ഡിഫോൾട്ട് ബ്രിട്ടീഷ് ശബ്ദം';
}

function paintSound(){
  sbtn.classList.toggle('off', !soundOn);
  sbtn.title = 'ഉച്ചാരണ ക്രമീകരണം';
  $('#vp-on').classList.toggle('on', soundOn);
  $('#vp-off').classList.toggle('on', !soundOn);
  $('#vp-f').classList.toggle('on', voiceGender === 'f');
  $('#vp-m').classList.toggle('on', voiceGender === 'm');
  $('#vp-n').classList.toggle('on', !slowMode);
  $('#vp-s').classList.toggle('on', slowMode);
  document.body.classList.toggle('sound-off', !soundOn);
  if(!soundOn && synth) synth.cancel();
  paintVoiceName();
}
paintSound();
if(synth) synth.onvoiceschanged = paintVoiceName;

sbtn.onclick = e => { e.stopPropagation(); vpanel.classList.toggle('on'); paintVoiceName(); };
$('#vp-on').onclick = () => { soundOn = true; store.set('sound','1'); paintSound(); };
$('#vp-off').onclick = () => { soundOn = false; store.set('sound','0'); paintSound(); };
$('#vp-f').onclick = () => { voiceGender = 'f'; store.set('voice','f'); paintSound(); previewVoice(); };
$('#vp-m').onclick = () => { voiceGender = 'm'; store.set('voice','m'); paintSound(); previewVoice(); };
$('#vp-n').onclick = () => { slowMode = false; store.set('slow','0'); paintSound(); };
$('#vp-s').onclick = () => { slowMode = true; store.set('slow','1'); paintSound(); };
function previewVoice(){
  if(soundOn) speak('Hello, I am your British English voice.', null, false);
}
document.addEventListener('click', e => {
  if(vpanel.classList.contains('on') && !vpanel.contains(e.target) && !sbtn.contains(e.target))
    vpanel.classList.remove('on');
});
document.addEventListener('keydown', e => { if(e.key === 'Escape') vpanel.classList.remove('on'); });

let speakingEl = null;
function speak(text, el, slow){
  if(!synth || !text) return;
  synth.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const v = pickVoice(voiceGender);
  if(v){ u.voice = v; u.lang = v.lang; } else { u.lang = 'en-GB'; }
  u.rate = (slow || slowMode) ? 0.58 : 0.9;
  u.pitch = 1;
  if(speakingEl) speakingEl.classList.remove('on','speaking');
  speakingEl = el || null;
  if(speakingEl) speakingEl.classList.add(speakingEl.classList.contains('say') ? 'speaking' : 'on');
  u.onend = u.onerror = () => {
    if(speakingEl){ speakingEl.classList.remove('on','speaking'); speakingEl = null; }
  };
  synth.speak(u);
}

document.addEventListener('click', e => {
  if(!soundOn) return;
  const b = e.target.closest('.spk');
  if(b){ e.preventDefault(); e.stopPropagation(); speak(b.dataset.say, b, e.shiftKey); return; }
  const s = e.target.closest('.say');
  if(s){
    const sel = window.getSelection ? String(window.getSelection()).trim() : '';
    if(sel) return;
    speak(s.dataset.say, s, e.shiftKey);
  }
});

/* ---------- init ---------- */
initTicks();
initTrackers();
initRowTicks();
route();
updateCounts();
if(!location.hash) history.replaceState(null,'','#home');
"""

HTML = """<!DOCTYPE html>
<html lang="ml" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Spoken English for Malayalam Speakers — British English</title>
<meta name="description" content="മലയാളികൾക്കായുള്ള ബ്രിട്ടീഷ് ഇംഗ്ലീഷ് സ്പീക്കിംഗ് കോഴ്സ്">
<meta property="og:type" content="website">
<meta property="og:title" content="Spoken English for Malayalam Speakers — British English">
<meta property="og:description" content="17 അധ്യായങ്ങൾ · ബ്രിട്ടീഷ് ഉച്ചാരണം · ഓഫ്‌ലൈൻ · സൗജന്യം">
<meta name="theme-color" content="#0b5d55">
__FONTLINKS__
<style>__CSS__</style>
</head>
<body>
<header>
  <button class="iconbtn menubtn" id="menubtn" aria-label="മെനു">☰</button>
  <div class="brand">സ്പോക്കൺ ഇംഗ്ലീഷ്<small id="crumb">Spoken English for Malayalam Speakers</small></div>
  <div class="sp"></div>
  <button class="iconbtn hide-sm" id="fminus" title="അക്ഷരം ചെറുതാക്കുക">A−</button>
  <button class="iconbtn hide-sm" id="fplus" title="അക്ഷരം വലുതാക്കുക">A+</button>
  <button class="iconbtn" id="soundbtn" aria-label="ഉച്ചാരണം ഓൺ / ഓഫ്" title="ഉച്ചാരണ ബട്ടണുകൾ ഓഫ്"></button>
  <button class="iconbtn" id="tbtn" aria-label="നിറം മാറ്റുക" title="നിറം മാറ്റുക">☾</button>
  <button class="iconbtn hide-sm pdfbtn" onclick="window.print()" aria-label="പ്രിന്റ് ചെയ്യുക" title="പ്രിന്റ് / PDF">PDF</button>
</header>
<div id="progress"></div>
<div class="voicepanel" id="voicepanel" role="dialog" aria-label="ഉച്ചാരണ ക്രമീകരണം">
  <div class="vp-t">BRITISH ENGLISH VOICE</div>
  <div class="vp-now" id="vpnow">—</div>
  <div class="vp-row"><span>ശബ്ദ ബട്ടണുകൾ</span>
    <div class="seg"><button type="button" id="vp-on">ഓൺ</button><button type="button" id="vp-off">ഓഫ്</button></div></div>
  <div class="vp-row"><span>ശബ്ദം</span>
    <div class="seg"><button type="button" id="vp-f">വനിതാ</button><button type="button" id="vp-m">പുരുഷൻ</button></div></div>
  <div class="vp-row"><span>വേഗം</span>
    <div class="seg"><button type="button" id="vp-n">സാധാരണ</button><button type="button" id="vp-s">പതുക്കെ</button></div></div>
  <div class="vp-note">🔊 അമർത്തിയാൽ വാക്കും വാക്യവും കേൾക്കാം. ബട്ടണുകൾ ഓഫ് ചെയ്താൽ ഐക്കണുകൾ മറയും.</div>
</div>
<div class="overlay" id="ov"></div>
<div class="wrap">
  <aside id="side">
    <input class="search" id="search" aria-label="അധ്യായം തിരയുക" placeholder="തിരയുക…  ( / )" autocomplete="off">
    <div id="results"></div>
    <nav id="navbox"></nav>
  </aside>
  <main id="main">__SECTIONS__</main>
</div>
<script>__JS__</script>
</body>
</html>
"""

FONTS_FILE = os.path.join(BASE, "_inline-fonts.css")
GOOGLE = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
          '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
          '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam:wght@400;600;700&display=swap" rel="stylesheet">')
if os.path.exists(FONTS_FILE):
    with open(FONTS_FILE, encoding="utf-8") as f:
        FONTLINKS = "<style>%s</style>" % f.read()
else:
    FONTLINKS = GOOGLE

out = HTML.replace("__FONTLINKS__", FONTLINKS).replace("__CSS__", CSS) \
          .replace("__SECTIONS__", "\n".join(sections)) \
          .replace("__JS__", JS) \
          .replace("__NAV__", json.dumps(navdata, ensure_ascii=False))

TARGET = os.path.join(BASE, "index.html")
with open(TARGET, "w", encoding="utf-8") as f:
    f.write(out)

print("index.html written:", round(len(out)/1024), "KB")
print("speaker buttons:", out.count("class='spk'"))
