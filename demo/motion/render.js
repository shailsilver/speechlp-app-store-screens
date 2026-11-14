// Render a motion page to MP4 frame by frame.
// node render.js <page.html> <out.mp4> [audio.wav] [--fps 30] [--from s] [--to s] [--w 1920 --h 1080]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const [page_, out, audio] = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && args[i - 1].startsWith('--')));
const FPS = +opt('--fps', 30), W = +opt('--w', 1920), H = +opt('--h', 1080);

(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(page_));
  await page.evaluate(() => window.__ready);
  const dur = await page.evaluate(() => window.__duration);
  const from = +opt('--from', 0), to = +opt('--to', dur);
  const n = Math.round((to - from) * FPS);

  const ff = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-'];
  if (audio) ff.push('-ss', String(from), '-i', audio);
  ff.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
    '-profile:v', 'high', '-movflags', '+faststart');
  if (audio) ff.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
  ff.push(out);
  const proc = spawn('ffmpeg', ff, { stdio: ['pipe', 'inherit', 'inherit'] });

  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const t = from + i / FPS;
    await page.evaluate(t => window.__seek(t), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!proc.stdin.write(buf)) await new Promise(r => proc.stdin.once('drain', r));
    if (i % 150 === 0) process.stderr.write(`${out}: ${i}/${n} (${((Date.now() - t0) / 1000).toFixed(0)}s)\n`);
  }
  proc.stdin.end();
  await new Promise(r => proc.on('close', r));
  await browser.close();
  console.log(`wrote ${out} (${(n / FPS).toFixed(1)}s)`);
})();
