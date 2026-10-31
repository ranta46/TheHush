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

## Finishing (when all frames exist)
blender_encode.py (TremenVR films/tuck/tools) encode(dir) -> raw.mp4 (wait until size stops changing; never call twice)
-> device_stage_files -> cloud: python3 film3d/post3d.py film3d/films/filmNN <raw.mp4> -> look at 4 frames
-> push mp4 + poster to ranta-videos gloamrun/films/ (raw URL 200) -> film_log status "stock".

## Posting (cloud, 20:13 JST): see ../film_kit/FILM_RUNBOOK.md "Posting" (brand Rook 7473995; YouTube type video,
title "Gloamrun Film N: <title> | Rook and the Hush", thumbnail = poster; Facebook POST). Mark "posted".
