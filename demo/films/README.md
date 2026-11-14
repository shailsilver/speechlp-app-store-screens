# SpeechLP & SpeechTherapist.app demo films

1920×1080, 30fps H.264. Made for the ASHA booth (one film per laptop, looping) and the website.

| File | Length | Use |
|---|---|---|
| `SpeechLP-Film-Booth-Loop.mp4` | 53s | Laptop 1 at the booth. Silent, seamless loop. |
| `SpeechTherapist-Film-Booth-Loop.mp4` | 46s | Laptop 2 at the booth. Silent, seamless loop. |
| `SpeechLP-Film-Web-Music.mp4` | 53s | Website / social, with an original music bed. |
| `SpeechTherapist-Film-Web-Music.mp4` | 46s | Website / social, with an original music bed. |

**Looping on a Mac:** open in QuickTime Player → View → Loop (⌥⌘L) → View → Enter Full Screen.
The last frame matches the first, so there is no visible jump.

## Content sources
- Claims come from the SpeechLP ESSA Evidence Packet (Nov 2026): ~15-word age-based screeners for
  ages 3–9, 1,500+ target words across all 24 English consonants, two CCC-SLPs modeling every sound,
  SLP workflow (invite with a connection code → assign sounds/positions/blends → monitor → plan),
  COPPA/FERPA/HIPAA/PIPEDA, "SpeechLP never receives any audio".
- SpeechTherapist.app shows **no overall accuracy %** and no accuracy trend (accuracy is only
  meaningful per phoneme). It shows home sessions, words practiced, words per day, and accuracy by
  sound. Numbers are the demo account's (labelled "Demo data"); the weekly breakdown is illustrative.
- The invite (connection code) and assign screens are stylized illustrations of the workflow,
  not screenshots of the live app.
- Music is synthesized by `demo/motion/music.py` (original, royalty-free).

## Re-rendering
Source is in `demo/motion/` (HTML scenes + `engine.js`). Render with:
`node demo/motion/render.js demo/motion/speechlp.html out.mp4` (needs Playwright + ffmpeg).
Preview a frame: open `speechlp.html?t=12.5` in a browser.
