"""Build Instagram story mockups (1080x1920). Run: python3 stories.py && node render.js"""
import pathlib, html
HERE = pathlib.Path(__file__).parent

def poll(opts):
    return '<div class="poll">' + "".join(f'<div class="opt">{o}</div>' for o in opts) + "</div>"
def poll2(a, b):
    return f'<div class="poll2"><div>{a}</div><div>{b}</div></div>'
def question(q):
    return f'<div class="qs"><div class="qh">{q}</div><div class="qi">Type something…</div></div>'
def countdown(t, d):
    return f'<div class="cd"><div class="ct">{t}</div><div class="cn"><b>08</b>:<b>14</b>:<b>22</b>:<b>05</b></div><div class="cl">days · hrs · min · sec</div><div class="cdate">{d}</div></div>'
def link(t):
    return f'<div class="link">🔗 {t}</div>'

S = [
 # ---------- SLP set ----------
 ("slp-1", "grad-a", "For SLPs · 1 of 4", "We're heading back to <span>ASHA!</span>",
  "Indianapolis · Nov 19–21 · Booth 2046",
  countdown("ASHA 2026 starts", "Thu, Nov 19") + poll2("Yes! 🙋", "Wish I were"), "🐧", "Poll: Will you be there?"),
 ("slp-2", "grad-b", "For SLPs · 2 of 4", "What language does your caseload practice in at home?",
  "Help us decide what to build next.",
  poll(["English only","Spanish","Another language","A mix"]) + question("Which language should SpeechLP add next?"), "🌎", ""),
 ("slp-3", "grad-c", "For SLPs · 3 of 4", "Where are you joining us from?",
  "We're hearing from SLPs well beyond the US.",
  poll(["🇺🇸 US","🇨🇦 Canada","🇦🇺 Australia","🌍 Elsewhere"]), "📍", ""),
 ("slp-4", "grad-d", "For SLPs · 4 of 4", "Be honest: how do you know if home practice actually happens?",
  "",
  poll(["I ask parents","Data sheets","An app","Honestly, I don't 😅"]) +
  '<div class="foot">See how we solve this at <b>Booth 2046</b>.<br>Free posters, plus our book when<br>you start a SpeechTherapist.app trial.</div>', "📋", ""),
 # ---------- Parent set ----------
 ("parent-1", "grad-e", "For parents · 1 of 4", "What language do you speak with your kids at home?",
  "We're making SpeechLP for more families.",
  poll(["English","Spanish","Another language","More than one!"]), "💜", ""),
 ("parent-2", "grad-b", "For parents · 2 of 4", "Would your family use SpeechLP in another language?",
  "Tell us which one, and we'll let you know when it's ready.",
  '<div class="slider"><div class="sq">Slide to answer</div><div class="track"><div class="fill"></div><div class="knob">😍</div></div></div>' +
  question("Which language? Where do you live?"), "🗣️", ""),
 ("parent-3", "grad-a", "For parents · 3 of 4", "How often does your child practice speech at home?",
  "No judgment. Every family is different!",
  poll(["Every day","A few times a week","Rarely","We're just starting"]), "🏠", ""),
 ("parent-4", "grad-c", "For parents · 4 of 4", "What makes home practice hardest?",
  "",
  poll(["Getting them to sit","Not sure I'm doing it right","Finding the time","Knowing which words"]) +
  '<div class="foot">Kids say the words out loud,<br>and the game responds. Free to try.</div>' + link("app.speechlp.com"), "🎮", ""),
]

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#222;font-family:Inter,Arial,sans-serif;display:flex;flex-wrap:wrap;gap:40px;padding:40px}
.story{width:1080px;height:1920px;position:relative;overflow:hidden;color:#fff;display:flex;flex-direction:column;align-items:center;padding:260px 90px 300px;text-align:center}
.grad-a{background:linear-gradient(165deg,#7b4fe0,#4a22b0)}
.grad-b{background:linear-gradient(165deg,#0f8f6a,#0b5a45)}
.grad-c{background:linear-gradient(165deg,#e8554e,#a72d5c)}
.grad-d{background:linear-gradient(165deg,#3a46b8,#1f1d3a)}
.grad-e{background:linear-gradient(165deg,#d94fad,#7b4fe0)}
.blob{position:absolute;border-radius:50%;background:#fff;opacity:.08}
.b1{width:700px;height:700px;top:-250px;right:-260px}.b2{width:520px;height:520px;bottom:-200px;left:-200px}
.brand{position:absolute;top:120px;left:90px;display:flex;align-items:center;gap:18px;font-weight:700;font-size:40px}
.brand i{font-style:normal;background:#fff;border-radius:18px;width:72px;height:72px;display:grid;place-items:center;font-size:44px}
.tag{position:absolute;top:140px;right:90px;font-size:28px;font-weight:600;opacity:.8;letter-spacing:.04em;text-transform:uppercase}
.emoji{font-size:150px;line-height:1;margin-bottom:30px}
h1{font-family:"Inter Display",Inter,sans-serif;font-weight:800;font-size:86px;line-height:1.06;letter-spacing:-.01em;margin-bottom:26px}
h1 span{color:#ffe36e}
.sub{font-size:40px;opacity:.92;margin-bottom:56px;line-height:1.3}
.poll{background:#fff;border-radius:40px;padding:26px;width:780px;display:flex;flex-direction:column;gap:18px;box-shadow:0 20px 50px rgba(0,0,0,.25);margin-bottom:44px}
.opt{background:#f1eef8;color:#1f1d3a;border-radius:24px;padding:26px 30px;font-size:42px;font-weight:700;text-align:left}
.poll2{display:flex;background:#fff;border-radius:40px;overflow:hidden;width:780px;box-shadow:0 20px 50px rgba(0,0,0,.25);margin-top:10px}
.poll2 div{flex:1;padding:44px 10px;font-size:52px;font-weight:800;color:#6b3fd4}
.poll2 div+div{border-left:3px solid #eee;color:#e8554e}
.qs{background:#fff;color:#1f1d3a;border-radius:40px;width:780px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.25)}
.qh{background:#1f1d3a;color:#fff;padding:34px 36px;font-size:42px;font-weight:700;line-height:1.2}
.qi{padding:34px;font-size:38px;color:#999;background:#f4f4f6;margin:24px;border-radius:20px}
.cd{background:#fff;color:#1f1d3a;border-radius:40px;width:780px;padding:40px 30px;box-shadow:0 20px 50px rgba(0,0,0,.25);margin-bottom:40px}
.ct{font-size:44px;font-weight:800;margin-bottom:16px}
.cn{font-size:92px;font-weight:800;color:#6b3fd4;letter-spacing:.02em}
.cl{font-size:28px;color:#888;margin-top:4px}
.cdate{font-size:32px;color:#6b3fd4;font-weight:600;margin-top:16px}
.foot{font-size:42px;line-height:1.35;font-weight:500;margin-bottom:36px}
.foot b{color:#ffe36e}
.link{background:#fff;color:#2b6ef2;font-weight:700;font-size:44px;border-radius:24px;padding:24px 40px;box-shadow:0 20px 50px rgba(0,0,0,.25)}
.slider{background:#fff;border-radius:40px;width:780px;padding:40px 50px 56px;box-shadow:0 20px 50px rgba(0,0,0,.25);margin-bottom:44px}
.sq{color:#1f1d3a;font-size:42px;font-weight:700;margin-bottom:40px}
.track{height:22px;border-radius:11px;background:#eee;position:relative}
.fill{position:absolute;inset:0 30% 0 0;border-radius:11px;background:linear-gradient(90deg,#ffb36e,#e8554e)}
.knob{position:absolute;left:62%;top:-44px;font-size:96px}
"""

out = ['<!doctype html><html><head><meta charset="utf-8"><style>', CSS, '</style></head><body>']
for sid, grad, tag, h, sub, stickers, emo, _ in S:
    out.append(f'<div class="story {grad}" id="{sid}"><div class="blob b1"></div><div class="blob b2"></div>'
               f'<div class="brand"><i>🐧</i>SpeechLP</div><div class="tag">{tag}</div>'
               f'<div class="emoji">{emo}</div><h1>{h}</h1>' + (f'<div class="sub">{sub}</div>' if sub else '<div style="height:30px"></div>') +
               f'{stickers}</div>')
out.append('</body></html>')
(HERE / "stories.html").write_text("".join(out))
print("ok", len(S))
