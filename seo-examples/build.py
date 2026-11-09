"""Generate example SEO word-list pages + printable sheets.

Mockups only: emoji stand in for SpeechLP's real word art.
Run: python3 build.py   (writes <slug>.html next to this file)
"""
import json, re, pathlib, html

HERE = pathlib.Path(__file__).parent
QR = (HERE / "qr-app.svg").read_text()
QR = re.sub(r"<\?xml[^>]*\?>", "", QR)

SOUNDS = [
  {
    "slug": "k-words-initial",
    "sym": "/k/", "name": "K", "pos": "beginning",
    "title": "K Words for Speech Therapy: Beginning of Words (Free Printable)",
    "meta": "Free list of initial /k/ words with pictures, phrases and sentences, plus a printable practice sheet. Made by speech-language pathologists.",
    "h1": "/k/ words at the beginning",
    "intro": "Practice words that start with the /k/ sound, like <b>cat</b>, <b>cup</b> and <b>cookie</b>. Print the free practice sheet, or have your child say these words out loud in SpeechLP and hear right away if they got it.",
    "age": "Most children say /k/ clearly by about age 3½ to 4 (Crowe &amp; McLeod, 2020). Before that, saying “tat” for “cat” is common.",
    "words": [("🐱","cat"),("☕","cup"),("🚗","car"),("🔑","key"),("🎂","cake"),("🐄","cow"),
              ("🍪","cookie"),("🪁","kite"),("🌽","corn"),("🥕","carrot"),("🧁","cupcake"),("🏰","castle")],
    "more": ["coat","comb","candy","camel","kitten","coconut","cowboy","coffee","can","cap","cone","cub"],
    "phrases": ["cute cat","cold cup","cookie cake","cool car"],
    "sentences": ["The cat is in the car.","Can I have a cookie?","The cow ate the corn.","Fly the kite with me!"],
    "tips": [
      ("Where it’s made","/k/ is a “back” sound. The back of the tongue lifts up to touch the roof of the mouth, then lets go with a puff of air."),
      ("What you might hear","Kids often swap in /t/, the front sound: “tup” for cup, “tar” for car."),
      ("Make it a game","Say each word 5 times and color a star. Model the word slowly, then let them try. Praise the try, not just the right answer."),
    ],
    "faq": [
      ("At what age should a child say the /k/ sound?","Most children say /k/ by about age 3½ to 4. Every child is different. If you’re concerned, talk with a speech-language pathologist."),
      ("Why does my child say “t” instead of “k”?","This is called fronting: a back sound like /k/ is replaced with a front sound like /t/. It’s common in young children and usually goes away on its own. An SLP can tell you if it’s lasting longer than expected."),
      ("How often should we practice?","Short and often beats long and rare. A few minutes most days is a great goal, especially when it’s the practice your SLP assigned."),
    ],
    "related": [("k-words-middle","/k/ middle"),("k-words-end","/k/ end"),("g-words-initial","/g/ beginning"),("r-words-initial","/r/ beginning")],
  },
  {
    "slug": "r-words-initial",
    "sym": "/r/", "name": "R", "pos": "beginning",
    "title": "R Words for Speech Therapy: Beginning of Words (Free Printable)",
    "meta": "Free list of initial /r/ words with pictures, phrases and sentences, plus a printable practice sheet. Made by speech-language pathologists.",
    "h1": "/r/ words at the beginning",
    "intro": "Practice words that start with the /r/ sound, like <b>rabbit</b>, <b>rainbow</b> and <b>rocket</b>. Print the free practice sheet, or have your child say these words out loud in SpeechLP and hear right away if they got it.",
    "age": "/r/ is one of the last sounds children learn. Many kids say it clearly between ages 5 and 6 (Crowe &amp; McLeod, 2020), so “wabbit” for “rabbit” is common in younger children.",
    "words": [("🐰","rabbit"),("🌧️","rain"),("🌈","rainbow"),("💍","ring"),("🚀","rocket"),("🤖","robot"),
              ("🌹","rose"),("🪨","rock"),("📖","read"),("🏃","run"),("🦝","raccoon"),("📏","ruler")],
    "more": ["red","rope","radio","rooster","roof","rug","race","rake","rice","road","room","rest"],
    "phrases": ["red rose","run, rabbit, run","rainbow rocket","read a book"],
    "sentences": ["The rabbit ran to the rock.","I see a big rainbow.","The robot has a ring.","Let’s race on the road!"],
    "tips": [
      ("Why /r/ is tricky","The tongue has to pull back and bunch up or curl, without touching anything. It’s hard to see, which makes it hard to copy."),
      ("What you might hear","Young kids often swap in /w/: “wabbit” for rabbit, “wed” for red."),
      ("Make it a game","Be the listener: say a word right or wrong and let your child judge it. Hearing the difference is a big first step."),
    ],
    "faq": [
      ("At what age should a child say the /r/ sound?","/r/ comes late. Many children master it between ages 5 and 6, and some later. If your child is older and still working on /r/, an SLP can help."),
      ("Why does my child say “w” instead of “r”?","This is called gliding, and it’s common while /r/ is developing. If it continues past the typical age, talk with a speech-language pathologist."),
      ("Can an app help with /r/?","Practice at home helps most when it follows what your SLP is working on. SpeechLP lets SLPs assign the exact words and positions, and shows them how practice went."),
    ],
    "related": [("r-words-middle","/r/ middle"),("r-words-end","/r/ end"),("r-blends","/r/ blends"),("k-words-initial","/k/ beginning")],
  },
]

CSS = """
:root{--ink:#1f1d3a;--muted:#5b5875;--purple:#6b3fd4;--purple-2:#7b4fe0;--soft:#f3effd;--line:#e6e1f3;--bg:#ffffff;--card:#ffffff;--green:#0f6b4f}
@media (prefers-color-scheme: dark){:root{--ink:#eceaf6;--muted:#aaa6c4;--soft:#26213d;--line:#353052;--bg:#15131f;--card:#1d1a2b}}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:Inter,"Helvetica Neue",Arial,sans-serif;line-height:1.55}
a{color:var(--purple)}
.site-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;max-width:960px;margin:0 auto}
.logo{display:flex;align-items:center;gap:8px;font-weight:700;color:var(--ink);text-decoration:none}
.logo span{background:var(--purple);color:#fff;border-radius:8px;width:28px;height:28px;display:grid;place-items:center}
.btn{display:inline-block;border-radius:999px;padding:11px 18px;font-weight:600;text-decoration:none;font-size:15px;cursor:pointer;border:0}
.btn-primary{background:var(--purple);color:#fff}
.btn-ghost{background:var(--soft);color:var(--purple)}
main{max-width:960px;margin:0 auto;padding:0 16px 48px}
.crumbs{font-size:13px;color:var(--muted);margin:8px 0 6px}
.crumbs a{color:var(--muted)}
h1{font-family:"Inter Display",Inter,sans-serif;font-size:clamp(28px,5vw,42px);line-height:1.1;margin-bottom:12px}
h2{font-family:"Inter Display",Inter,sans-serif;font-size:22px;margin:36px 0 12px}
.intro{font-size:17px;max-width:680px;color:var(--ink)}
.ctas{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 6px}
.byline{font-size:13px;color:var(--muted);margin-top:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
.w{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 10px;text-align:center}
.w .pic{font-size:44px;line-height:1.1}
.w .word{font-weight:700;font-size:18px;margin-top:6px}
.more{display:flex;flex-wrap:wrap;gap:8px}
.more span{background:var(--soft);border-radius:999px;padding:5px 12px;font-size:15px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:640px){.two{grid-template-columns:1fr}}
.box{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.box ul{padding-left:18px}
.tips{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.tips .box b{display:block;color:var(--purple);margin-bottom:4px}
.app{margin:36px 0 0;border-radius:18px;padding:22px;background:linear-gradient(120deg,#5a2fc2,#7b4fe0);color:#fff;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.app h2{margin:0 0 6px;color:#fff}
.app p{opacity:.95;max-width:520px}
.app .btn{background:#fff;color:#5a2fc2;margin-left:auto}
details{border-bottom:1px solid var(--line);padding:12px 0}
summary{font-weight:600;cursor:pointer}
details p{margin-top:8px;color:var(--muted)}
.related{display:flex;flex-wrap:wrap;gap:8px}
.related a{border:1px solid var(--line);border-radius:999px;padding:6px 14px;text-decoration:none;font-size:15px}
.disclaimer{font-size:12.5px;color:var(--muted);margin-top:28px}
.mock-note{background:#fff7d6;color:#5c4a00;border-radius:10px;padding:8px 12px;font-size:13px;margin:8px 0 4px}

/* ---------- Printable sheet ---------- */
.sheet{display:none}
@media print{
  @page{size:letter;margin:0}
  body{background:#fff;color:#1f1d3a}
  .site-head,main{display:none !important}
  .sheet{display:flex}
}
.sheet{width:8.5in;height:11in;padding:.45in .5in .4in;flex-direction:column;gap:.16in;background:#fff;color:#1f1d3a;font-family:Inter,Arial,sans-serif}
.sheet .top{display:flex;align-items:center;gap:.2in;border-bottom:3px solid #6b3fd4;padding-bottom:.12in}
.sheet .sym{font-family:"Inter Display",Inter,sans-serif;font-size:44pt;font-weight:800;color:#6b3fd4;line-height:1}
.sheet h3{font-family:"Inter Display",Inter,sans-serif;font-size:22pt;line-height:1.1}
.sheet .sub{font-size:10.5pt;color:#5b5875}
.sheet .name{margin-left:auto;font-size:10pt;color:#5b5875;text-align:right;line-height:2}
.sheet .name i{display:inline-block;border-bottom:1px solid #999;width:1.7in}
.sheet .cards{display:grid;grid-template-columns:repeat(4,1fr);gap:.13in;flex:1}
.sheet .c{border:2px solid #e6e1f3;border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:.06in}
.sheet .c .pic{font-size:46pt;line-height:1.05}
.sheet .c .word{font-weight:800;font-size:17pt;margin:.02in 0 .04in}
.sheet .c .stars{font-size:13pt;letter-spacing:2px;color:#b9b0dc}
.sheet .bottom{display:flex;gap:.2in;align-items:center;background:#f3effd;border-radius:14px;padding:.12in .18in}
.sheet .bottom .qr{width:.9in;height:.9in;background:#fff;border-radius:8px;padding:4px;flex:none}
.sheet .bottom .qr svg{width:100%;height:100%;display:block}
.sheet .bottom b{font-size:12pt;color:#6b3fd4;display:block}
.sheet .bottom p{font-size:9.5pt}
.sheet .how{font-size:10pt;color:#1f1d3a}
.sheet .fine{font-size:7.5pt;color:#7a7695;text-align:center}
"""

def page(s):
    e = html.escape
    words = "".join(f'<div class="w"><div class="pic" aria-hidden="true">{p}</div><div class="word">{w}</div></div>' for p,w in s["words"])
    more = "".join(f"<span>{w}</span>" for w in s["more"])
    phrases = "".join(f"<li>{x}</li>" for x in s["phrases"])
    sentences = "".join(f"<li>{x}</li>" for x in s["sentences"])
    tips = "".join(f'<div class="box"><b>{a}</b>{b}</div>' for a,b in s["tips"])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in s["faq"])
    related = "".join(f'<a href="{slug}.html">{label}</a>' for slug,label in s["related"])
    cards = "".join(f'<div class="c"><div class="pic">{p}</div><div class="word">{w}</div><div class="stars">☆☆☆☆☆</div></div>' for p,w in s["words"])
    ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in s["faq"]]}
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(s['title'])}</title>
<meta name="description" content="{e(s['meta'])}">
<link rel="canonical" href="https://speechlp.com/words/{s['slug']}/">
<script type="application/ld+json">{json.dumps(ld)}</script>
<style>{CSS}</style>
</head>
<body>
<header class="site-head">
  <a class="logo" href="#"><span>🐧</span>SpeechLP</a>
  <a class="btn btn-primary" href="https://app.speechlp.com">Try SpeechLP free</a>
</header>
<main>
  <div class="mock-note">Mockup: emoji stand in for SpeechLP's real word pictures.</div>
  <nav class="crumbs"><a href="#">Speech sounds</a> › <a href="#">{s['name']}</a> › {s['pos'].capitalize()}</nav>
  <h1>{s['h1']}</h1>
  <p class="intro">{s['intro']}</p>
  <div class="ctas">
    <button class="btn btn-primary" onclick="window.print()">⬇ Free printable practice sheet</button>
    <a class="btn btn-ghost" href="https://app.speechlp.com">▶ Practice these out loud in SpeechLP</a>
  </div>
  <p class="byline">Written and reviewed by Alissa Fox, M.S., CCC-SLP and Mari Gottlieb, M.A., CCC-SLP</p>

  <h2>Picture words</h2>
  <div class="grid">{words}</div>

  <h2>More {s['sym']} words</h2>
  <div class="more">{more}</div>

  <div class="two">
    <div><h2>Phrases</h2><div class="box"><ul>{phrases}</ul></div></div>
    <div><h2>Sentences</h2><div class="box"><ul>{sentences}</ul></div></div>
  </div>

  <h2>Tips from our SLPs</h2>
  <div class="tips">{tips}</div>

  <h2>When do kids learn {s['sym']}?</h2>
  <p>{s['age']}</p>

  <section class="app">
    <div>
      <h2>Say it out loud. SpeechLP listens.</h2>
      <p>These same {s['sym']} words come to life in 7 games. Your child says the word, and the game responds. SLPs can assign exact sounds and positions and see how home practice went.</p>
    </div>
    <a class="btn" href="https://app.speechlp.com">Play free</a>
  </section>

  <h2>Questions parents ask</h2>
  {faq}

  <h2>Practice other sounds</h2>
  <div class="related">{related}</div>

  <p class="disclaimer">This page is for practice and information. It isn't a substitute for an evaluation or therapy with a licensed speech-language pathologist.</p>
</main>

<section class="sheet" aria-hidden="true">
  <div class="top">
    <div class="sym">{s['sym']}</div>
    <div><h3>{s['name']} words: {s['pos']}</h3><div class="sub">Say each word 5 times. Color a star each time!</div></div>
    <div class="name">Name <i></i><br>Week of <i></i></div>
  </div>
  <div class="cards">{cards}</div>
  <div class="bottom">
    <div class="qr">{QR}</div>
    <div>
      <b>Want the words to talk back?</b>
      <p class="how">Scan to play these {s['sym']} words in SpeechLP. Your child says the word out loud and the game responds. Free to try at app.speechlp.com</p>
    </div>
  </div>
  <div class="fine">© SpeechLP · speechlp.com · Free to print and share for home and therapy use · Not a substitute for speech-language therapy.</div>
</section>
</body>
</html>"""

for s in SOUNDS:
    (HERE / f"{s['slug']}.html").write_text(page(s))
    print("wrote", s["slug"])
