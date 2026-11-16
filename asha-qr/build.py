"""Build ASHA 2026 QR signs.
Usage: python3 build.py [STAY_CONNECTED_FORM_URL]
Without a form URL, the Stay Connected QR spots show a 'QR coming' placeholder.
"""
import sys, re, pathlib, qrcode, qrcode.image.svg
HERE = pathlib.Path(__file__).parent
import base64
def img(name):
    return "data:image/png;base64," + base64.b64encode((HERE / "logos" / f"{name}.png").read_bytes()).decode()
UTM = "utm_source=asha2026&utm_medium=qr&utm_campaign=booth2046"
LINKS = {
    "speechlp": f"https://app.speechlp.com/?{UTM}",
    "st": f"https://speechtherapist.app/?{UTM}",
}
FORM = sys.argv[1].strip() if len(sys.argv) > 1 else ""

def qr(url):
    if not url:
        return '<div class="ph">QR code goes here<br><small>once the Google Form link is ready</small></div>'
    svg = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1,
                      error_correction=qrcode.constants.ERROR_CORRECT_M).to_string(encoding="unicode")
    return re.sub(r"<\?xml[^>]*\?>", "", svg)

CSS = """
@page{size:%s;margin:0}*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,'Helvetica Neue',Arial,sans-serif;color:#1f1d3a;background:#fff}
.page{width:%s;height:%s;padding:.45in .5in;display:flex;flex-direction:column}
.top{text-align:center;margin-bottom:.25in}
.top .kick{font-size:11pt;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#6b3fd4}
.top h1{font-family:'Inter Display',Inter,sans-serif;font-size:34pt;line-height:1.05;margin:.06in 0}
.top p{font-size:13pt;color:#5b5875}
.qrbox{background:#fff;border-radius:14px;padding:10px}
.qrbox svg{width:100%%;height:100%%;display:block}
.ph{width:100%%;height:100%%;border:3px dashed #b9b0dc;border-radius:12px;display:flex;flex-direction:column;gap:4px;align-items:center;justify-content:center;text-align:center;color:#7a7695;font-size:12pt;font-weight:600;padding:8px}
.ph small{font-weight:400;font-size:9pt}
.foot{margin-top:auto;text-align:center;font-size:10pt;color:#7a7695}
"""

def option_a():
    cards = [
        ("speechlp", "Try SpeechLP", "Speech sound practice kids do out loud", "app.speechlp.com", "#6b3fd4", "#f3effd"),
        ("st", "Try SpeechTherapist.app", "Document once. SOAP notes, goals and parent updates.", "speechtherapist.app", "#0f6b4f", "#e6f4ee"),
        ("form", "Stay Connected", "Get updates, request a demo, or explore research", "30-second form", "#d9534f", "#fdecea"),
    ]
    html = ""
    for key, title, sub, url, c, bg in cards:
        code = qr(FORM) if key == "form" else qr(LINKS[key])
        html += f'''<div class="card" style="background:{bg};border-top:8px solid {c}">
          <h2 style="color:{c}">{title}</h2><p class="sub">{sub}</p>
          <div class="qrbox q">{code}</div>
          <div class="url">{url}</div></div>'''
    css = CSS % ("11in 8.5in", "11in", "8.5in") + """
    .row{display:grid;grid-template-columns:repeat(3,1fr);gap:.3in;flex:1}
    .card{border-radius:18px;padding:.25in .22in;display:flex;flex-direction:column;align-items:center;text-align:center}
    .card h2{font-family:'Inter Display',Inter,sans-serif;font-size:22pt;line-height:1.1;min-height:.75in;display:flex;align-items:center}
    .card .sub{font-size:11.5pt;color:#3d3a5c;margin:.08in 0 .18in;min-height:.6in}
    .q{width:2.55in;height:2.55in}
    .url{margin-top:.15in;font-weight:700;font-size:12pt}
    """
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>ASHA QR Sign - 3 codes</title><style>{css}</style></head><body><div class="page">
      <div class="top"><div class="kick">ASHA 2026 · Booth 2046</div><h1>Scan to explore</h1><p>Point your phone camera at a code</p></div>
      <div class="row">{html}</div>
      <div class="foot">SpeechLP &amp; SpeechTherapist.app · Built by practicing SLPs · HIPAA &amp; COPPA compliant</div>
    </div></body></html>'''

def option_b():
    css = CSS % ("8.5in 11in", "8.5in", "11in") + """
    .big{width:4.3in;height:4.3in;margin:.1in auto .25in;border:6px solid #6b3fd4;border-radius:22px;padding:14px}
    .opts{display:grid;gap:.14in;width:5.6in;margin:0 auto}
    .opt{display:flex;align-items:center;gap:.16in;border-radius:14px;padding:.14in .2in}
    .opt b{font-size:15pt;display:block}.opt span{font-size:11pt;color:#3d3a5c}
    .dot{width:.48in;height:.48in;border-radius:12px;flex:none;color:#fff;font-weight:800;display:grid;place-items:center;font-size:16pt}
    .ico{width:.48in;height:.48in;flex:none;object-fit:contain}
    .logos{display:flex;align-items:center;justify-content:center;gap:.45in;margin-bottom:.22in}
    .logos img{height:.5in;width:auto}
    .logos img.lp{height:.66in}
    .logos .sep{width:1px;height:.4in;background:#ddd}
    """
    opts = [(f'<img class="ico" src="{img("speechlp-icon")}" alt="">',"Try SpeechLP","Speech sound practice kids do out loud","#6b3fd4","#f3effd"),
            (f'<img class="ico" src="{img("speechtherapist-icon")}" alt="">',"Try SpeechTherapist.app","SLP documentation + assign SpeechLP for home practice","#0f6b4f","#e6f4ee"),
            ('<div class="dot" style="background:#d9534f">&#9993;</div>',"Stay Connected","Get updates, request a demo, or explore research","#d9534f","#fdecea")]
    oh = "".join(f'<div class="opt" style="background:{bg}">{ic}<div><b style="color:{c}">{t}</b><span>{s}</span></div></div>' for ic,t,s,c,bg in opts)
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>ASHA QR Sign - 1 code</title><style>{css}</style></head><body><div class="page">
      <div class="logos"><img class="lp" src="{img("speechlp-logo")}" alt="SpeechLP"><div class="sep"></div><img src="{img("speechtherapist-logo")}" alt="SpeechTherapist.app"></div>
      <div class="top"><div class="kick">ASHA 2026 · Booth 2046</div><h1>Great meeting you!</h1><p>Scan once to try our apps or stay in touch</p></div>
      <div class="qrbox big">{qr(FORM)}</div>
      <div class="opts">{oh}</div>
      <div class="foot">Built by practicing SLPs · HIPAA &amp; COPPA compliant</div>
    </div></body></html>'''

(HERE / "asha-sign-3-qr-codes.html").write_text(option_a())
(HERE / "asha-sign-1-qr-code.html").write_text(option_b())
print("built", "with form" if FORM else "WITHOUT form link (placeholders)")
