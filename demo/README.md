# Demo videos

Rendered by `render_videos.py` (886×1920, 30fps H.264 — App Store iPhone preview size, silent).
Uses current-UI screens in `assets/current/` (from the ESSA evidence packet) plus the
game-card / lesson screenshots in the repo root with the old Learn/Practice tab bar removed.

| File | Flow |
|---|---|
| `videos/01-app-tour.mp4` | Learning path → tap Level ▶ → say the word ("mother") → Post Game Report → level 17 |
| `videos/02-slp-lessons.mp4` | Learning path → lesson marker → SLP video lesson → "Words in this game" |
| `videos/03-practice-games.mp4` | Beary Hungry, Baby Talk, Chicken Little, Pilot Penguin → Choose sounds → Start → say the word → in-game |

Each video in `videos/` ends with a speechtherapist.app ($20/month) card showing the SLP dashboard —
use these for the podcast, social and web. `videos/app-store/` has the same videos without that card
(Apple rejects App Store previews that show pricing or promote other services).

Re-render: `python3 demo/render_videos.py all` (needs Pillow + ffmpeg).
