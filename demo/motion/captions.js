
// ---------- captions (enable with ?cc=1) — timed to the recorded voiceover
(function () {
  if (!new URLSearchParams(location.search).has('cc')) return;
  const bar = document.createElement('div');
  bar.id = 'ccbar';
  bar.style.cssText = 'position:absolute; left:0; right:0; margin:0 auto; width:fit-content; max-width:1700px; white-space:nowrap; bottom:26px; padding:10px 28px; border-radius:16px; background:rgba(8,6,28,.72); color:#fff; font-family:Inter, sans-serif; font-weight:600; font-size:34px; line-height:1.3; text-align:center; z-index:999; backdrop-filter:blur(4px); box-shadow:0 10px 30px rgba(0,0,0,.25); opacity:0';
  document.getElementById('stage').appendChild(bar);
  const prevG = window.GLOBAL;
  window.GLOBAL = t => {
    if (prevG) prevG(t);
    const c = window.CAPTIONS.find(([a, b]) => t >= a && t < b);
    if (c) { if (bar.textContent !== c[2]) bar.textContent = c[2];
      bar.style.opacity = Math.min(1, (t - c[0]) / 0.15, (c[1] - t) / 0.15); }
    else bar.style.opacity = 0;
  };
})();
