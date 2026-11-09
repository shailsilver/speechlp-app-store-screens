const { chromium } = require('playwright');
(async () => {
  const dir = __dirname + '/';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 2000 } });
  await p.goto('file://' + dir + 'stories.html'); await p.waitForTimeout(400);
  const ids = await p.$$eval('.story', els => els.map(e => e.id));
  for (const id of ids) { await (await p.$('#' + id)).screenshot({ path: dir + id + '.png' }); }
  // contact sheet
  await p.setContent('<body style="margin:0;background:#111;display:grid;grid-template-columns:repeat(4,270px);gap:16px;padding:20px">' +
    ids.map(i => `<img src="file://${dir}${i}.png" style="width:270px">`).join('') + '</body>');
  await p.setViewportSize({ width: 1180, height: 1040 }); await p.waitForTimeout(400);
  await p.screenshot({ path: dir + 'all-stories-preview.png', fullPage: true });
  await b.close(); console.log(ids.join(' '));
})();
