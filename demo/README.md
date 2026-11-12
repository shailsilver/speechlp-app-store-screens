# Demo videos

Rendered from the app screenshots in the repo root by `render_videos.py`
(886×1920, 30fps H.264 — App Store iPhone preview size, silent audio track).

| File | Length | Flow |
|---|---|---|
| `videos/01-app-tour.mp4` | 28.6s | Learning path → Practice → game carousel → Choose sounds → Start Game → in-game |
| `videos/02-slp-lessons.mp4` | 19.4s | Learn tab → lesson pin → SLP video lesson |
| `videos/03-practice-games.mp4` | 25.2s | Montage of all five practice games |

Re-render: `python3 demo/render_videos.py all` (needs Pillow + ffmpeg).

Each video in `videos/` ends with a speechtherapist.app ($20/month) card for SLPs — use these
for the podcast, social and web. `videos/app-store/` has the same videos without that card
(Apple rejects App Store previews that show pricing or promote other services).
