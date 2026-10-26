# Release/privacy-policy.md と support.md から、アプリと同じ見た目の HTML を作る
# （背景グラデーション #FDFBFB→#EBEDEE、見出し Bold 34、白いカード r16、本文 16 / 補足 13 #565656、
#   ページの切り替えは言語ピルと同じ形：灰色 #EAEAEA／選択中は黒）
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
nav{display:flex;gap:8px;margin-bottom:32px}
nav a{font-size:11px;font-weight:600;padding:6px 8px;border-radius:999px;background:var(--chip);color:var(--ink);text-decoration:none}
nav a.on{background:var(--ink);color:#fff}
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

def page(src, out, active):
    title, intro, sections = parse((SRC / src).read_text())
    updated = next((l for l in intro if l.startswith("Last updated")), None)
    rest = [l for l in intro if l != updated]
    secs = []
    for s in sections:
        faq = s["h"].lower().startswith("frequently")
        secs.append(f'<section><h2>{inline(s["h"])}</h2>\n{body_html(s["lines"], faq)}</section>')
    on = ' class="on"'
    nav = "".join(f'<a href="{href}"{on if href == active else ""}>{name}</a>'
                  for href, name in [("privacy.html", "Privacy Policy"), ("support.html", "Support")])
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Score Up 990</title><style>{CSS}</style></head>
<body><main>
<div class="app"><img src="icon.png" alt=""><span>Score Up 990</span></div>
<nav>{nav}</nav>
<h1>{html.escape(title)}</h1>
{f'<p class="updated">{inline(updated)}</p>' if updated else ''}
{''.join(f'<p class="intro">{inline(l)}</p>' for l in rest)}
{chr(10).join(secs)}
<footer>© 2026 Sheep Shih<br>TOEIC is a registered trademark of ETS. This app is not endorsed or approved by ETS.</footer>
</main></body></html>
"""
    (ROOT / out).write_text(doc)

page("privacy-policy.md", "privacy.html", "privacy.html")
page("support.md", "support.html", "support.html")
print("built privacy.html, support.html")
