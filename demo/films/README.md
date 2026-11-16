# SpeechLP & SpeechTherapist.app demo films

1920×1080, 30fps H.264. Made for the ASHA booth (one film per laptop, looping) and the website.

| File | Length | Use |
|---|---|---|
| `SpeechLP-Film-Booth-Loop.mp4` | 70s | Laptop 1 at the booth. Silent, seamless loop. |
| `SpeechTherapist-Laptop2-Combined-Loop.mp4` | 115s | Laptop 2: SLP practice film, then documentation film. Silent. |
| `SpeechTherapist-Film-Booth-Loop.mp4` | 46s | SLP home-practice film on its own. Silent, seamless loop. |
| `SpeechTherapist-Docs-Film-Booth-Loop.mp4` | 70s | SLP documentation film on its own. Silent, seamless loop. |
| `*-Voiceover.mp4` | — | **Narrated** versions (founder voiceover over ducked music). Best for the website and social. |
| `*-Web-Music.mp4` | — | The same films with music only (SpeechLP also has the game's own sound effects). |

4K (3840×2160) versions of every file are made in `demo/films/4K/` but are not committed
(about 450 MB); they were delivered directly. The 1080p files are downscaled from the 4K renders.

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
- Invite and assign screens in both SLP films are real frames from the SpeechTherapist.app ×
  SpeechLP home-practice demo video (connection code 8WF-R99, demo student Leo M.).
- Documentation film: the SOAP note, clinical insight and "Maya, age 5" demo client are taken verbatim
  from the public walkthrough at speechtherapist.app/demo. Document lists come from the product
  changelog (private practice: SOAP, evaluations, progress reports, parent updates, lesson plans;
  school: the nine builders). Pricing wording matches speechtherapist.app/pricing ("$20/seat/month",
  "Free plan available"). The "edit with a sentence" shortened Plan text is illustrative.
- SpeechLP live gameplay (Perry In Submarine, 5–0 win, Snaily evolving, FRIEND pack → Gooey) is from
  the founder's screen recording (296×640 source, so it is slightly soft when enlarged).
- SpeechLP games: all seven games with taglines from speechlp.com; card art from the website.
- Music is synthesized by `demo/motion/music.py` (original, royalty-free).

## Re-rendering
Source is in `demo/motion/` (HTML scenes + `engine.js`). Render with:
`node demo/motion/render.js demo/motion/speechlp.html out.mp4` (needs Playwright + ffmpeg).
Preview a frame: open `speechlp.html?t=12.5` in a browser.

## Voiceover
Script: `voiceover-scripts.md` / `Voiceover-Script.pdf`. Lines are cut from the founder's two recordings
with Whisper word timestamps and placed on each scene by `demo/motion/voiceover.py`; music is
side-chain ducked about 10 dB under the voice. Raw recordings are not committed.

## Captions
Booth loops of the two SpeechTherapist.app films have 4 burned-in key-line captions (silent playback).
Voiceover and Web-Music versions have **no** burned-in captions; use the `.srt` files for switchable
captions on YouTube/website. The SpeechLP film has no captions (its headlines carry every line).
