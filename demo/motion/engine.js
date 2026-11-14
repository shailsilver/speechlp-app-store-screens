// Deterministic motion engine: every frame is a pure function of time t (seconds).
// The page defines window.SCENES = [{start, end, el, fn(lt, dur)}] and calls Engine.boot().
// render.js calls window.__seek(t) for each frame and screenshots the page.

const Ease = {
  lin: t => t,
  out: t => 1 - Math.pow(1 - t, 3),
  out5: t => 1 - Math.pow(1 - t, 5),
  in: t => t * t * t,
  inOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  back: t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
  spring: t => (t <= 0 ? 0 : t >= 1 ? 1 : 1 - Math.exp(-7 * t) * Math.cos(11 * t)),
};

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;

// progress of t through [a, b], eased
function prog(t, a, b, ease = Ease.inOut) { return ease(clamp((t - a) / (b - a))); }

// keyframes: [[time, value], ...]; ease applied per segment
function kf(t, frames, ease = Ease.inOut) {
  if (t <= frames[0][0]) return frames[0][1];
  for (let i = 0; i < frames.length - 1; i++) {
    const [t0, v0] = frames[i], [t1, v1] = frames[i + 1];
    if (t <= t1) return lerp(v0, v1, ease(clamp((t - t0) / (t1 - t0))));
  }
  return frames[frames.length - 1][1];
}

// set transform/opacity/filter on an element from a props object
function put(el, p) {
  if (typeof el === 'string') el = document.querySelector(el);
  if (!el) return;
  const tr = [];
  if (p.x !== undefined || p.y !== undefined) tr.push(`translate3d(${p.x || 0}px, ${p.y || 0}px, ${p.z || 0}px)`);
  if (p.rx !== undefined) tr.push(`rotateX(${p.rx}deg)`);
  if (p.ry !== undefined) tr.push(`rotateY(${p.ry}deg)`);
  if (p.r !== undefined) tr.push(`rotate(${p.r}deg)`);
  if (p.s !== undefined) tr.push(`scale(${p.s})`);
  el.style.transform = tr.join(' ');
  if (p.o !== undefined) el.style.opacity = clamp(p.o);
  if (p.blur !== undefined) el.style.filter = p.blur > 0.05 ? `blur(${p.blur}px)` : 'none';
}

// fade a scene in/out at its edges
function edge(lt, dur, fin = 0.5, fout = 0.5) {
  return Math.min(prog(lt, 0, fin, Ease.out), 1 - prog(lt, dur - fout, dur, Ease.in));
}

// split element text into word spans (for kinetic type)
function words(el) {
  if (typeof el === 'string') el = document.querySelector(el);
  if (el.dataset.split) return [...el.querySelectorAll('.w')];
  const parts = el.innerHTML.split(/(\s+|<br>)/);
  el.innerHTML = parts.map(p => (p.trim() && p !== '<br>' ? `<span class="w">${p}</span>` : p)).join('');
  el.dataset.split = 1;
  return [...el.querySelectorAll('.w')];
}

function count(el, t, a, b, from, to, fmt = v => Math.round(v).toLocaleString()) {
  if (typeof el === 'string') el = document.querySelector(el);
  el.textContent = fmt(lerp(from, to, prog(t, a, b, Ease.out)));
}

const Engine = {
  boot() {
    window.__duration = Math.max(...window.SCENES.map(s => s.end));
    window.__seek = t => {
      for (const s of window.SCENES) {
        const el = typeof s.el === 'string' ? document.querySelector(s.el) : s.el;
        const on = t >= s.start && t < s.end;
        el.style.display = on ? '' : 'none';
        if (on) s.fn(t - s.start, s.end - s.start, t);
      }
      if (window.GLOBAL) window.GLOBAL(t);
    };
    window.__ready = Promise.all([...document.images].map(i => i.decode().catch(() => {})))
      .then(() => document.fonts.ready);
    const q = new URLSearchParams(location.search);
    if (q.has('t')) window.__ready.then(() => window.__seek(parseFloat(q.get('t'))));
  },
};
