# Release/privacy-policy(.ja/.zh).md と support(.ja/.zh).md から公開用の HTML を作る
# 見出しの構成は Oo-peh-hip と同じ：小さいラベル → アプリ名（大）＋サブタイトル → 線の下に情報 →
# 言語ボタン → 前置き → 01・02… の番号付きの項目 → フッター
# 色・書体はアプリに合わせる（背景グラデーション #FDFBFB→#EBEDEE、黒がアクセント、SF Pro、白いカード r16）
# 日本語・English・繁體中文を1ページに入れ、ボタンで切り替える（JavaScript なし。最初は日本語）
# usage: cd Release/site && python3 build.py
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent
EMAIL = "stf0830@icloud.com"

CSS = """
:root{--page-top:#FDFBFB;--page-bottom:#EBEDEE;--surface:#FFFFFF;--ink:#000000;--heading:#1A1A1A;--secondary:#565656;--tertiary:#ADADAD;--hair:#D0D0D0}
*{box-sizing:border-box}
html{background:var(--page-bottom)}
body{margin:0;min-height:100vh;background:linear-gradient(180deg,var(--page-top),var(--page-bottom));color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Hiragino Sans","PingFang TC","Helvetica Neue",Arial,sans-serif;
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;-webkit-text-size-adjust:100%}
.wrap{max-width:640px;margin:0 auto;padding:0 32px}
.mono{font-family:ui-monospace,"SF Mono",Menlo,monospace}

/* 見出し：ラベル → アプリ名 → 情報 */
header{padding-top:64px}
.eyebrow{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:12.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
  color:var(--ink);margin:0 0 18px;display:flex;align-items:center;gap:10px}
.eyebrow::before{content:"";width:26px;height:9px;border-radius:5px;background:var(--ink);display:inline-block}
h1{font-weight:800;font-size:clamp(38px,9vw,56px);line-height:1.02;letter-spacing:-.02em;color:var(--heading);margin:0}
h1 .sub{display:block;font-size:.4em;font-weight:600;letter-spacing:.01em;color:var(--secondary);margin-top:14px}
.meta{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:12.5px;color:var(--secondary);margin-top:26px;padding-top:22px;
  border-top:1px solid var(--hair);display:flex;flex-wrap:wrap;gap:6px 22px}
.meta b{color:var(--ink);font-weight:700}

/* 言語ボタン（Oo-peh-hip と同じ枠線の丸ボタン。選んだボタンは黒く塗る） */
.lang-radio{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:34px 0 8px}
nav label{font-size:13px;font-weight:700;letter-spacing:.04em;color:var(--secondary);background:transparent;
  border:1px solid var(--hair);border-radius:999px;padding:8px 18px;cursor:pointer;transition:.18s ease;user-select:none}
nav label:hover{color:var(--ink);border-color:var(--secondary)}
#lang-ja:checked ~ nav label[for="lang-ja"],#lang-en:checked ~ nav label[for="lang-en"],#lang-zh:checked ~ nav label[for="lang-zh"]{color:#fff;background:var(--ink);border-color:var(--ink)}
.lang-radio:focus-visible ~ nav label{outline:2px solid var(--ink);outline-offset:3px}

/* 本文 */
main{padding:24px 0 8px}
.doc{display:none}
#lang-ja:checked ~ main .doc[data-lang="ja"],#lang-en:checked ~ main .doc[data-lang="en"],#lang-zh:checked ~ main .doc[data-lang="zh"]{display:block;animation:fade .4s ease both}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.lede{font-size:18px;line-height:1.62;margin:8px 0 32px}

/* 番号付きの項目（白いカード） */
.clause{display:grid;grid-template-columns:34px 1fr;gap:0 18px;background:var(--surface);border-radius:16px;padding:20px;margin-bottom:12px}
.num{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-size:13px;font-weight:700;color:var(--ink);padding-top:3px}
.clause h2{font-size:20px;font-weight:700;letter-spacing:-.01em;line-height:1.25;margin:0 0 8px;color:var(--heading)}
.clause p{margin:0 0 10px;color:var(--secondary)}
.clause p:last-child{margin-bottom:0}
.clause strong{color:var(--ink);font-weight:600}
ul.mini{margin:6px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:9px}
ul.mini li{position:relative;padding-left:20px;color:var(--secondary)}
ul.mini li::before{content:"";position:absolute;left:2px;top:11px;width:6px;height:6px;border-radius:2px;background:var(--ink)}
a.mail{color:var(--ink);text-decoration:none;font-weight:600;border-bottom:1.5px solid var(--hair)}
a.mail:hover{border-bottom-color:var(--ink)}

footer{margin-top:28px;padding:30px 0 60px;border-top:1px solid var(--hair);font-size:12.5px;color:var(--secondary);
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}
footer .tm{flex-basis:100%;color:var(--tertiary)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:460px){
  header{padding-top:44px}
  .clause{grid-template-columns:1fr;gap:8px}
  .num{padding-top:0}
  .eyebrow,.meta{font-size:13.5px}
}
"""

def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+)", r'<a class="mail" href="mailto:\1">\1</a>', t)
    return t

def parse(md):
    """前置き / ## 見出しごとの本文 に分ける（# タイトルと最終更新の行は見出しの情報に回すので使わない）"""
    intro, sections, cur = [], [], None
    for line in md.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            cur = {"h": line[3:], "lines": []}; sections.append(cur)
        elif line.strip() and not re.match(r"(Last updated|最終更新|最後更新)", line):
            (cur["lines"] if cur else intro).append(line)
    return intro, sections

def body(lines):
    out, items = [], []
    for l in lines:
        if l.startswith("- "): items.append(f"<li>{inline(l[2:])}</li>"); continue
        if items: out.append('<ul class="mini">' + "".join(items) + "</ul>"); items = []
        out.append(f"<p>{inline(l)}</p>")
    if items: out.append('<ul class="mini">' + "".join(items) + "</ul>")
    return "".join(out)

def clauses(sections):
    """項目を 01・02… の番号付きにする。よくある質問は質問ごとに1項目"""
    items = []
    for s in sections:
        if any(s["h"].startswith(w) for w in ("Frequently", "よくある", "常見")):
            q = None
            for l in s["lines"]:
                m = re.fullmatch(r"\*\*(.+)\*\*", l.strip())
                if m: q = m.group(1)
                elif q is not None: items.append((q, [l])); q = None
        else:
            items.append((s["h"], s["lines"]))
    return "\n".join(f'<div class="clause"><div class="num">{i:02d}</div><div><h2>{inline(h)}</h2>{body(ls)}</div></div>'
                     for i, (h, ls) in enumerate(items, 1))

LANGS = [("ja", "日本語"), ("en", "English"), ("zh", "繁體中文")]

def doc(src, lang):
    intro, sections = parse((SRC / src).read_text())
    return f"""<section class="doc" data-lang="{lang}" lang="{'zh-Hant' if lang == 'zh' else lang}">
{''.join(f'<p class="lede">{inline(l)}</p>' for l in intro)}
{clauses(sections)}
</section>"""

def page(kind, srcs, out):
    label = "Privacy Policy" if kind == "privacy" else "Support"
    if kind == "privacy":
        meta = f'<span>最終更新 <b>2026-10-27</b></span><span>連絡先 <b>{EMAIL}</b></span><span><b>データ収集ゼロ</b></span>'
    else:
        meta = f'<span>サポート <b>{EMAIL}</b></span><span>バージョン <b>1.0</b></span>'
    radios = "".join(f'<input class="lang-radio" type="radio" name="lang" id="lang-{c}"{" checked" if c == "ja" else ""}>' for c, _ in LANGS)
    tabs = "".join(f'<label for="lang-{c}">{n}</label>' for c, n in LANGS)
    docs = "\n".join(doc(srcs[c], c) for c, _ in LANGS)
    html_doc = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{label} — Score Up 990</title><style>{CSS}</style></head>
<body><div class="wrap">
{radios}
<header>
  <p class="eyebrow">{label}</p>
  <h1>Score Up 990<span class="sub">Daily English test prep</span></h1>
  <div class="meta">{meta}</div>
</header>
<nav aria-label="言語 / Language">{tabs}</nav>
<main>
{docs}
</main>
<footer><span>Score Up 990</span><span>© 2026 Sheep Shih</span>
<span class="tm">TOEIC is a registered trademark of ETS. This app is not endorsed or approved by ETS.</span></footer>
</div></body></html>
"""
    (ROOT / out).write_text(html_doc)

page("privacy", {"ja": "privacy-policy.ja.md", "en": "privacy-policy.md", "zh": "privacy-policy.zh.md"}, "privacy.html")
page("support", {"ja": "support.ja.md", "en": "support.md", "zh": "support.zh.md"}, "support.html")
print("built privacy.html, support.html")
