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
- 2026-11-14: no calm start (story pace). After the cold open the film begins already in danger: Rook's first line (starting
  by 1.0 s) names the danger (e.g. "The lamps went out. It's here!"), and the Hush is on screen by 5 s of the film itself
  (was 10 s). The calm "Next stop" beat moves to the end or goes. From Film 17 (Film 16 was made before this). Judge on
  IG avg watch + 3 s skip of films 17-19 vs films 12-16 (IG 8.9-16.9 s / 40-55 %) and YouTube retention when rows return.
- 2026-11-15: back link (description text): YouTube description and Facebook post text get one line "Last film: <youtube_url of
  the newest posted film in film_log>" right after the synopsis (before "Play the ride free"). Only new films (not vault).
  From Film 17. Judge on YouTube views of films 17-19 vs films 11-16 at the same age; roll back if not better.
- 2026-11-16: cover test (14-16) CLOSED, KEEP (neutral on TikTok/IG views, no harm). New: vault Pinterest pins link to the film's own
  YouTube video: pinLink = that film's YouTube watch URL (film_log "youtube_url", or getScheduledPosts on its posted date ->
  youtube publicUrl) and the pin text gets "Watch the full film: <url>" right before "Play the ride free". New-film pins keep
  the ride link. Starts with vault Film 7 (11-17). Judge on YouTube views of vault films 7-10 (3 days after vs before).
- 2026-11-17: title hook test (12-14) CLOSED, KEEP (YouTube avg view 27-39 s vs 15-32 s for 5-11; Film 12 = 36 %, best ever). Vault hook
  KEEP so far (IG 10.6-13.6 s vs 6.5-8.7 s). New (thumbnail/poster): when post3d.py makes the poster, burn the film.json "hook" onto it as
  big easy text, 2 short lines, white with a dark outline, in a top corner, never over the Hush's face or Rook (still check it by eye).
  Poster = YouTube thumbnail + TikTok/IG cover + Pinterest pin. From the next poster made (Film 19). If the poster was already made
  without it, the posting run may add the text in the cloud before posting. Judge on YouTube views of films 19-21 vs 12-17 at the same age.
- 2026-11-18: vault hook test CLOSED, KEEP (IG avg watch vault 5-7 = 10.5-14.3 s vs 6.4-9.0 s). New (description text): Bluesky also opens with the
  hook: line 1 = hook, line 2 = "Gloamrun Film N: <title>" (vault: "From the vault: Gloamrun Film N: <title>"), then one short sentence, the ride link,
  #Gloamrun #animation, whole text under 300 chars. New films and vault posts, from vault Film 10 / Film 20. Judge on Bluesky likes+reposts of the
  next 6 posts vs the 18 before (2 likes total); roll back if not better.
- 2026-11-19: story pace test (17-19) CLOSED, KEEP (IG avg watch 12.1 / 31.4 / 16.3 s vs 10.3-16.3 s; Film 18 = 1205 IG views). New (hook wording):
  for films 21-23 the hook's 2nd sentence must NOT be "Don't move." / "Not a sound." / "Don't breathe." (7 of the last 9 hooks ended that way). Use a
  new short threat line from this film's own place (e.g. "The sea is rising. It's right behind."). The in-film fear line may still say "Don't move".
  Film 21 hook is now "It climbs to us. The stones are sliding." (burn this one on its poster). Judge on IG avg watch + TikTok/IG views of films 20-22
  vs 17-19; roll back if worse.
- 2026-11-20: hook wording test running (Film 20 already used a new threat line: IG 3 s skip 31.9 %, avg 23.6 s on day 1 vs 41-57 % / 10-16 s for
  "Don't move." hooks 12-17; keep going to Film 23). New (description text, posting run): comments are 0-1 per film on every network, so new films
  get a first comment = one easy either/or question from the film's danger (e.g. "Would you hide in the dark, or run for it?"), no names, no links.
  Send it as firstCommentText on YouTube, Facebook, Instagram and Threads (not TikTok, Bluesky, Pinterest, vault posts). If Metricool rejects it,
  post again without it. From Film 22. PC run: film.json may add "question"; if missing, the posting run writes one. Judge on comments of films
  22-24 vs films 11-21 (0-1 each); roll back if not better.
- 2026-11-21: hook wording test still running (IG better: Film 21 skip 40 % / 18.6 s vs 47-53 %; TikTok day 1 falling 78 -> 23). First-comment test starts with the next new film
  (Film 22 not posted yet; Film 23 was a 2D fallback and already got the question). New (description text, TikTok only, posting run, new films from the next one):
  TikTok hashtags = "#Gloamrun #animation #spooky #horror #creepy" (instead of "#Gloamrun #TheHush #animation #shortfilm #spooky"). Other networks unchanged.
  Judge on TikTok day-3 views of the next 3 new films vs films 19-21 (330 / 139 / 23); roll back if not better.
