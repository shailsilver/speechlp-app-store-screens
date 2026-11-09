// Same stories with the mock stickers hidden, so the real Instagram stickers go in the empty space.
const { chromium } = require('playwright');
(async () => {
  const dir = __dirname + '/';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 2000 } });
  await p.goto('file://' + dir + 'stories.html');
  await p.addStyleTag({ content: '.poll,.poll2,.qs,.cd,.slider,.link{visibility:hidden}' });
  await p.waitForTimeout(400);
  const ids = await p.$$eval('.story', els => els.map(e => e.id));
  for (const id of ids) await (await p.$('#' + id)).screenshot({ path: dir + 'clean/' + id + '-clean.png' });
  await b.close(); console.log('ok');
})();
