# GLOAMRUN FILMS — daily horizontal film for the Hush channel (Claude's job)
Owner: 森. ChatGPT ("チャッピー") makes the 3 daily SHORTS, comics and everything else on this channel.
Claude makes ONE horizontal FILM per day (not a Short), 2-3 minutes, and posts it. Nothing else.

## Canon (must read every time)
- `CANON.md` = the canon of Gloamrun, Rook and the Hush. Every rule there applies to films too:
  Rook / the Hush are drawn ONLY by `gloamrun_engine.py` (never change the engine, poses, colors);
  12 Rook poses; the Hush never speaks, never flies, cannot be defeated, keeps the finger at its mouth,
  points only at special moments, sinks in sunlight; Rook is the only speaker, short lines, never lies,
  puts passengers first, jokes when scared, whispers at the peak; on-screen text = simple English only.
- Do not explain the Hush's motives or origin (owner decides). Do not invent new main characters
  without first writing them into CANON.md (thoughts / personality / rules / voice / never-does).
- The Long Back (sky whale, old friend of Rook) may appear. Rook can fly only in light.

## A film
- Folder `films/filmNN/`: `film.json` {film_no, title (<=32 chars), synopsis, poster_t, note} + `act1.py`..`act4.py`
  (3-5 acts, each 26-40 s; written like `episodes/ep01.py` but with ACT_LEN; see films/film01 as the model).
- Story shape over the whole film: calm start -> the Hush appears -> chase (distance keeps changing) ->
  a clever move by Rook (new every film) -> fear in the dark ("Don't move") -> surprise / friend / light ->
  escape -> Rook's closing line. Thrill 70 / surprise 20 / fear 10. Never repeat a film's main trick
  (read `films/film_log.json`). Each film is complete in itself (a newcomer must understand it).
- `python3 film.py films/filmNN --check`, then `--preview 3` and LOOK at every sheet (Rook + Hush on screen,
  readable, not cut off, text simple English). Fix, then `python3 film.py films/filmNN` (about 10-15 min;
  run in background and wait). Output: films/filmNN/out/gloamrun_filmNN_16x9.mp4 + poster.

## Posting (Metricool brand "Rook", blogId 7473995, Asia/Tokyo)
- Upload the mp4 + poster to github ranta46/ranta-videos under `gloamrun/films/`, check raw URL = 200.
- YouTube: type "video" (NOT short), title "Gloamrun Film N: <title> | Rook and the Hush", category FILM_ANIMATION,
  madeForKids false, isAiGeneratedContent true, privacy public, videoThumbnailUrl = poster raw URL (if rejected, post without).
  Description: synopsis + "Play the ride free: https://ranta46.github.io/TheHush/" + "New film every day. Shorts every day too."
  + #Gloamrun #TheHush #animation #shortfilm
- Facebook: type POST (video), same text. (Shorts/Reels/TikTok/Instagram/Threads/Pinterest are ChatGPT's job: do not post films there.)
- Time: 20:13 JST (or now+20 min if later). Check getScheduledPosts first: never post two films the same day.
- Append to `films/film_log.json`: film_no, date, title, synopsis, clever_move, fear, surprise, closing_line, youtube post id.
