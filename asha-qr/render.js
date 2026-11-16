const { chromium } = require('playwright');
(async () => {
  const d = __dirname + '/', b = await chromium.launch(), p = await b.newPage();
  for (const [f, w, h] of [['asha-sign-3-qr-codes', 1056, 816], ['asha-sign-1-qr-code', 816, 1056]]) {
    await p.setViewportSize({ width: w, height: h });
    await p.goto('file://' + d + f + '.html'); await p.waitForTimeout(300);
    await p.pdf({ path: d + f + '.pdf', preferCSSPageSize: true, printBackground: true });
    await p.screenshot({ path: d + f + '.png' });
    console.log(f, await p.evaluate(() => { const e = document.querySelector('.page'); return e.scrollHeight - e.clientHeight; }));
  }
  await b.close();
})();
