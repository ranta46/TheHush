# GLOAMRUN 3D FILMS — made on the owner's PC (Blender), posted daily on the Hush channel
Owner 森 approved the 3D look on 2026-10-31 (hush_lookdev.blend, look_05.png). ChatGPT makes the shorts/comics;
Claude makes ONE horizontal 3D film per day (90-120 s, not a Short) and posts it (YouTube video + Facebook).

## Canon
Read ../film_kit/CANON.md every time (Rook / the Hush: thoughts, personality, voice, never-does; the Hush never
speaks, never flies, can't be defeated, finger at its mouth, sinks in sunlight; Rook only speaks, short simple
English, never lies, passengers first). 3D models = the approved ones in hush_lookdev.blend. Never redesign them.

## PC / GPU safety (Intel UHD laptop) — never break
EEVEE only, 1280x720, 24 samples, no raytracing, NO volumetrics, light shadows off for small lights.
Previews 40 % / 8 samples / 0.5 s rest. Final render ONLY with TremenVR films/tuck/tools/blender_render_timer.py
(start(ep_dir, END)), never two heavy renders at once. Empty/instant frames = GPU broken -> stop and report.

## Files
PC: C:\Users\81803\TremenFilm\hush\  hush_lookdev.blend (base), filmNN\hush_filmNN.blend, filmNN\frames\, filmNN\raw.mp4
Repo: film3d/films/filmNN/ build_scene.py (run in Blender on top of hush_lookdev.blend), film.json (film_no, title,
synopsis, poster_t, note, lines), score.py; film3d/film_log.json (status rendering -> stock -> posted).
Fetch repo files inside Blender with the GitHub API (no cache):
  urllib Request("https://api.github.com/repos/ranta46/TheHush/contents/<path>", headers {Accept: application/vnd.github.raw})
Open the base file in one execute_blender_code call, run the build in the NEXT call (context is empty right after open).

## Making a new film (filmNN)
1. Story (90-120 s, 9-12 shots): calm start -> the Hush appears -> chase (distance changes) -> Rook's clever move
   (NEW each film; see film_log + ../film_kit/films/film_log.json) -> fear in the dark -> surprise -> escape -> closing line.
   Newcomers must understand it. Lines: Rook only, max 9 words / 44 chars, simple English, 10-15 lines.
2. Copy films/film01/build_scene.py, change the set pieces (new places: bridge, station, river, snowfield, city,
   cliff, Long Back...), animation keys, cameras (one per shot, markers). Keep the helper code and the rules.
3. Build, then preview 10-14 frames (40 %, 8 samples), LOOK at them: Rook and the Hush readable, faces toward camera,
   not too dark, cameras not inside objects. Fix (max 3 rounds). Save, then start the timer render (END = frames).
4. film.json + score.py (gloamrun_sound cues). Push. film_log: status "rendering".
5. Cold open (from 2026-11-07): set film.json "cold_open": [t0, t1] (about 3 s) on the scariest shot where the Hush is
   big and close to Rook/the train (check the preview of that shot). post3d.py puts that clip (with its line and sound)
   in front of the film, then the film starts from 0. If missing, post3d.py uses the first "Don't move" line.
6. Follow every rule in "Current rules (auto-updated)" at the end of this file. They change after each post.

## Finishing (when all frames exist)
blender_encode.py (TremenVR films/tuck/tools) encode(dir) -> raw.mp4 (wait until size stops changing; never call twice)
-> device_stage_files -> cloud: python3 film3d/post3d.py film3d/films/filmNN <raw.mp4> -> look at 4 frames
-> push mp4 + poster to ranta-videos gloamrun/films/ (raw URL 200) -> film_log status "stock".

## Posting (cloud, 20:13 JST): see ../film_kit/FILM_RUNBOOK.md "Posting" (brand Rook 7473995; YouTube type video,
title "Gloamrun Film N: <title> | Rook and the Hush", thumbnail = poster; Facebook POST). Mark "posted".

## If device_stage_files is refused (folder not connected)
Pull raw.mp4 through Blender instead: execute_blender_code printing base64 of 1.5 MB slices ('CHUNKn' + data), ONE call
at a time (parallel calls time out); the big output is saved to a tool-results file -> decode, join, check md5/ffprobe.
Previews the same way (PNG base64). Pick poster_t on a frame where the Hush's face is lit (not a dark tunnel frame).

## Review after EVERY post (the 20:13 posting run does this, no permission needed)
Stats: Metricool brand 7473995, YouTube "videos published in range" (YTVP17 title, YTVP06 views, YTVP08 avg view
duration s, YTVP09 likes, YTVP11 comments, YTVP12 shares) for every "Gloamrun Film" + channel subscribers (YTEV01).
Save film3d/stats/YYYY-MM-DD.json. Compare each film's views and avg view duration / length (retention %) with
the others. Write 1-3 findings + the change made at the top of film3d/insights.md (keep all past entries).
Then APPLY the change right away by editing "Current rules (auto-updated)" below (the PC run reads it every film):
allowed = cold open choice, story pace (when the Hush appears), shot length, line count/wording, title style
(posting title "Gloamrun Film N: <title> | Rook and the Hush" may get a short hook before it), thumbnail/poster
choice, description text. Never change: canon, the approved 3D models, GPU safety, one film per day, posting time.
One change at a time, keep it if numbers improve over the next 3 films, otherwise roll it back.

## Current rules (auto-updated)
- 2026-11-07: films 1-4 kept only 14-27 s of 105 s on average. Start with a ~3 s cold open of the Hush close to
  Rook (see Making a new film step 5). The Hush must be on screen within the first 10 s of the film itself.
- 2026-11-10: cold open KEEP (Film 8: 41 % retention vs 14-28 % for films 2-7). New test = title hook: every film.json
  gets "hook": 4-7 easy English words from the scariest beat, two short sentences, no names (e.g. "The line ends. It
  keeps coming."). The posting run uses YouTube title "<hook> | Gloamrun Film N: <title> | Rook and the Hush" (Facebook
  title and post first line too). If film.json has no hook, the posting run writes one from the fear line. Judge on
  views of films 12-14; roll back if they do worse than films 5-11 at the same age.
- 2026-11-11: hook also goes FIRST LINE of the post text on YouTube, Facebook, TikTok, Instagram, Threads and Pinterest
  (line 2 = "Gloamrun Film N: <title>"). Bluesky keeps the title first (300-char limit). Judge with the title test on
  films 12-14 (TikTok/Instagram baseline: Film 11 day 1 = 55 / 125 views). PC run: always write film.json "hook".
- 2026-11-12: cover test: TikTok and Instagram Reel posts (new films and vault posts) also send videoThumbnailUrl =
  poster raw URL (if Metricool rejects it, post again without). Judge on TikTok/IG views of films 14-16 vs films 11-13;
  roll back if worse. PC run: the poster must show the Hush and Rook clearly (it is now the cover on 4 networks).
- 2026-11-13: vault hook: vault reposts (TikTok, Instagram, Threads, Pinterest) put a hook line FIRST (4-7 easy words from
  the scariest beat, two short sentences, like the film hooks), then "From the vault: Gloamrun Film N: <title>". Use the
  film's "hook" from the log if it has one, otherwise write one from its fear line. Bluesky keeps the title first.
  Starts with vault Film 5. Judge on IG avg watch of vault films 5-7 vs vault films 1-2 (6.5 / 8.0 s); roll back if not better.
