// node snap.js page.html out.png t1 t2 ... -> contact sheet of frames (for review)
const { chromium } = require('playwright');
const path = require('path');
const [page_, out, ...ts] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.resolve(page_));
  await p.evaluate(() => window.__ready);
  const shots = [];
  for (const t of ts) { await p.evaluate(t => window.__seek(t), +t); shots.push(await p.screenshot({ type: 'png' })); }
  // tile with a second page
  const html = `<body style="margin:0;background:#000;display:grid;grid-template-columns:repeat(3,640px);gap:4px">` +
    shots.map((s, i) => `<div style="position:relative"><img style="width:640px;display:block" src="data:image/png;base64,${s.toString('base64')}"><span style="position:absolute;left:6px;top:4px;color:#ff0;font:bold 20px sans-serif">${ts[i]}s</span></div>`).join('') + '</body>';
  const q = await b.newPage({ viewport: { width: 1928, height: 400 } });
  await q.setContent(html); await q.waitForTimeout(200);
  await q.screenshot({ path: out, fullPage: true });
  await b.close();
})();
