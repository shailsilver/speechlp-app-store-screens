# SpeechLP & SpeechTherapist.app demo films

1920×1080, 30fps H.264. Made for the ASHA booth (one film per laptop, looping) and the website.

| File | Length | Use |
|---|---|---|
| `SpeechLP-Film-Booth-Loop.mp4` | 70s | Laptop 1 at the booth. Silent, seamless loop. |
| `SpeechTherapist-Laptop2-Combined-Loop.mp4` | 101s | Laptop 2 at the booth: practice film then docs film. Silent. |
| `SpeechTherapist-Film-Booth-Loop.mp4` | 46s | SLP home-practice film on its own. Silent, seamless loop. |
| `SpeechTherapist-Docs-Film-Booth-Loop.mp4` | 56s | SLP documentation film on its own. Silent, seamless loop. |
| `*-Web-Music.mp4` | — | The same three films with an original music bed, for the website. |

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
- Documentation film: the SOAP note, clinical insight and "Maya, age 5" demo client are taken verbatim
  from the public walkthrough at speechtherapist.app/demo. Document lists come from the product
  changelog (private practice: SOAP, evaluations, progress reports, parent updates, lesson plans;
  school: the nine builders). Pricing wording matches speechtherapist.app/pricing ("$20/seat/month",
  "Free plan available"). The "edit with a sentence" shortened Plan text is illustrative.
- SpeechLP live gameplay (Perry In Submarine, 5–0 win, Snaily evolving, FRIEND pack → Gooey) is from
  the founder's screen recording (296×640 source, so it is slightly soft when enlarged).
- SpeechLP games: all seven games with taglines from speechlp.com; card art from the website.
- The invite (connection code) and assign screens are stylized illustrations of the workflow,
  not screenshots of the live app.
- Music is synthesized by `demo/motion/music.py` (original, royalty-free).

## Re-rendering
Source is in `demo/motion/` (HTML scenes + `engine.js`). Render with:
`node demo/motion/render.js demo/motion/speechlp.html out.mp4` (needs Playwright + ffmpeg).
Preview a frame: open `speechlp.html?t=12.5` in a browser.
