# Release/privacy-policy.md と support.md から、アプリと同じ見た目の HTML を作る
# （背景グラデーション #FDFBFB→#EBEDEE、見出し Bold 34、白いカード r16、本文 16 / 補足 13 #565656、
#   ページの切り替えは言語ピルと同じ形：灰色 #EAEAEA／選択中は黒）
# 日本語・English・繁體中文を1ページに入れ、上のタブで切り替える（Oo-peh-hip と同じ仕組み。最初は日本語）
# usage: cd Release/site && python3 build.py
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent

CSS = """
:root{--page-top:#FDFBFB;--page-bottom:#EBEDEE;--surface:#FFFFFF;--chip:#EAEAEA;--ink:#000000;--heading:#1A1A1A;--secondary:#565656;--tertiary:#ADADAD}
*{box-sizing:border-box}
html{background:var(--page-bottom)}
body{margin:0;min-height:100vh;background:linear-gradient(180deg,var(--page-top),var(--page-bottom));color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
main{max-width:520px;margin:0 auto;padding:56px 32px 64px}
.app{display:flex;align-items:center;gap:12px;margin-bottom:24px}
.app img{width:44px;height:44px;border-radius:10px}
.app span{font-size:13px;font-weight:700}
/* 言語の切り替え（JavaScript なし。アプリの How scores work の言語切り替えと同じ形） */
.lang-radio{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.tabs{display:flex;background:var(--chip);border-radius:999px;padding:3px;margin-bottom:40px}
.tabs label{flex:1;text-align:center;font-size:13px;font-weight:500;padding:7px 0;border-radius:999px;cursor:pointer;color:var(--ink)}
#lang-ja:checked ~ .tabs label[for="lang-ja"],#lang-en:checked ~ .tabs label[for="lang-en"],#lang-zh:checked ~ .tabs label[for="lang-zh"]{background:var(--surface);font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.lang-radio:focus-visible ~ .tabs{outline:2px solid var(--ink);outline-offset:3px}
.doc{display:none}
#lang-ja:checked ~ .doc[data-lang="ja"],#lang-en:checked ~ .doc[data-lang="en"],#lang-zh:checked ~ .doc[data-lang="zh"]{display:block}
.other{font-size:13px;margin-top:8px}
.other a{color:var(--ink);font-weight:700}
h1{font-size:34px;line-height:41px;letter-spacing:.4px;font-weight:700;color:var(--heading);margin:0 0 8px}
.updated{font-size:13px;color:var(--secondary);margin:0 0 40px}
.intro{font-size:16px;line-height:1.6;margin:0 0 40px}
section{margin-bottom:32px}
h2{font-size:13px;font-weight:700;margin:0 0 12px}
.card{background:var(--surface);border-radius:16px;padding:16px 20px}
.card p{font-size:16px;line-height:1.6;margin:0 0 12px}
.card p:last-child{margin-bottom:0}
.card ul{margin:0;padding-left:20px}
.card li{font-size:16px;line-height:1.6;margin-bottom:8px}
.card li:last-child{margin-bottom:0}
.faq .q{font-size:16px;font-weight:700;line-height:1.2;margin:0 0 8px}
.faq .a{font-size:13px;line-height:1.6;color:var(--secondary);margin:0}
.faq + .faq{margin-top:12px}
a.mail{color:var(--ink);font-weight:700}
footer{margin-top:48px;font-size:11px;line-height:1.6;color:var(--tertiary)}
"""

def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+)", r'<a class="mail" href="mailto:\1">\1</a>', t)
    return t

def parse(md):
    """# タイトル / Last updated / 前置き / ## 見出しごとの本文 に分ける"""
    title, intro, sections, cur = "", [], [], None
    for line in md.splitlines():
        if line.startswith("# "):
            title = line[2:].split(" — ")[0]
        elif line.startswith("## "):
            cur = {"h": line[3:], "lines": []}; sections.append(cur)
        elif line.strip():
            (cur["lines"] if cur else intro).append(line)
    return title, intro, sections

def body_html(lines, faq=False):
    if faq:
        # **質問** の次の行が答え
        out, q = [], None
        for l in lines:
            m = re.fullmatch(r"\*\*(.+)\*\*", l.strip())
            if m: q = m.group(1)
            elif q is not None:
                out.append(f'<div class="card faq"><p class="q">{inline(q)}</p><p class="a">{inline(l)}</p></div>'); q = None
        return "\n".join(out)
    out, items = [], []
    for l in lines:
        if l.startswith("- "): items.append(f"<li>{inline(l[2:])}</li>"); continue
        if items: out.append("<ul>" + "".join(items) + "</ul>"); items = []
        out.append(f"<p>{inline(l)}</p>")
    if items: out.append("<ul>" + "".join(items) + "</ul>")
    return '<div class="card">' + "\n".join(out) + "</div>"

LANGS = [("ja", "日本語"), ("en", "English"), ("zh", "繁體中文")]
# もう一方のページへのリンクの文言
OTHER = {"privacy": {"ja": "サポート", "en": "Support", "zh": "支援"},
         "support": {"ja": "プライバシーポリシー", "en": "Privacy Policy", "zh": "隱私權政策"}}

def doc(src, lang, kind):
    title, intro, sections = parse((SRC / src).read_text())
    updated = intro[0] if intro and re.match(r"(Last updated|最終更新|最後更新)", intro[0]) else None
    rest = [l for l in intro if l != updated]
    secs = []
    for s in sections:
        faq = any(s["h"].startswith(w) for w in ("Frequently", "よくある", "常見"))
        secs.append(f'<section><h2>{inline(s["h"])}</h2>\n{body_html(s["lines"], faq)}</section>')
    other = "support" if kind == "privacy" else "privacy"
    return f"""<article class="doc" data-lang="{lang}" lang="{'zh-Hant' if lang == 'zh' else lang}">
<h1>{html.escape(title)}</h1>
{f'<p class="updated">{inline(updated)}</p>' if updated else ''}
{''.join(f'<p class="intro">{inline(l)}</p>' for l in rest)}
{chr(10).join(secs)}
<p class="other"><a href="{other}.html">{OTHER[kind][lang]}</a></p>
</article>"""

def page(kind, srcs, out):
    radios = "".join(f'<input class="lang-radio" type="radio" name="lang" id="lang-{c}"{" checked" if c == "ja" else ""}>' for c, _ in LANGS)
    tabs = "".join(f'<label for="lang-{c}">{n}</label>' for c, n in LANGS)
    docs = "\n".join(doc(srcs[c], c, kind) for c, _ in LANGS)
    title = "Privacy Policy" if kind == "privacy" else "Support"
    html_doc = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — Score Up 990</title><style>{CSS}</style></head>
<body><main>
<div class="app"><img src="icon.png" alt=""><span>Score Up 990</span></div>
{radios}
<nav class="tabs" aria-label="言語 / Language">{tabs}</nav>
{docs}
<footer>© 2026 Sheep Shih<br>TOEIC is a registered trademark of ETS. This app is not endorsed or approved by ETS.</footer>
</main></body></html>
"""
    (ROOT / out).write_text(html_doc)

page("privacy", {"ja": "privacy-policy.ja.md", "en": "privacy-policy.md", "zh": "privacy-policy.zh.md"}, "privacy.html")
page("support", {"ja": "support.ja.md", "en": "support.md", "zh": "support.zh.md"}, "support.html")
print("built privacy.html, support.html")
