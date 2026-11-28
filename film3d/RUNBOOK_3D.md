# GLOAMRUN 3D FILMS — made on the owner's PC (Blender), posted daily on the Hush channel
Owner 森 approved the 3D look on 2026-10-31 (hush_lookdev.blend, look_05.png). ChatGPT makes the 2D Ep shorts/comics.
FROM 2026-11-27 (owner's order: "make every single video to go BIG viral, care about results"): Claude makes VERTICAL 3D
shorts (9:16, 22-35 s) built to go viral - see "VIRAL FORMAT" below. It overrides every older rule that conflicts
(horizontal 90-120 s, calm start, end card, 3 s cold open + film from 0).

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

## VIRAL FORMAT (from 2026-11-27) - read this first, it beats every rule below
Why: Nov 2026 data. Horizontal 108 s films: YouTube 10-160 views each, subs flat at 53 for 4 weeks. Vertical ~23 s Gloamrun
Shorts on the same channel: 1,000-1,400 YouTube views EVERY time, subs +4-6/day while they ran daily. TikTok/IG stuck at
100-450 = the feed's free test pool; nothing broke out because people swipe in 3-8 s. The goal now is a HIT on every post
(target: 10,000+ views on one network within 7 days), not "one more film".
1. Shape: 720x1280 render (same pixel count as 1280x720 = same GPU load; GPU safety unchanged), camera sensor_fit
   VERTICAL, 24 fps, 22-35 s (END 528-840 frames = about 1/3 of the old render time). No title card, no end card,
   no calm start. post3d.py sees the vertical raw and finishes it (hook top 3.2 s, then "ask", Rook's lines, score).
2. ONE premise you can say in one sentence, built on a proven viral pattern. Pick from this library, never the same
   pattern two films in a row; use the best-scoring pattern most (film3d/patterns.md keeps the score):
   P1 SCALE REVEAL - what looked like a hill / tower / tree / cloud is the Hush ("That is not a hill.").
   P2 SPOT IT - the Hush is hidden in the frame from frame 1; text "Can you find it?"; it moves at the end -> rewatch + comments.
   P3 POV - the camera is YOUR eyes (a passenger); Rook talks to you ("Don't look out the window.").
   P4 THE RULE - one rule ("If the lamps go out, don't move."), then the rule is tested / broken.
   P5 CLOSE CALL - the Hush's finger closes on the last lantern; 3..2..1 in Rook's voice.
   P6 WRONG SAFE PLACE - the hiding place / tunnel / station is the Hush itself.
   P7 PART 2 - answer last film's cliffhanger in the first 2 s, end on a new one (series hook).
3. Second 0 = the money shot: the Hush big (>= 1/3 of the frame height), face LIT and readable on a phone, high contrast
   (the old films were too dark navy - add a rim light / moon light on the Hush, brighter sky gradient). Hook text on
   top: 4-7 easy words, a fact that makes you need the answer ("That is not a hill."). Never start on Rook alone.
4. Something changes every 2-4 s (cut, camera push, reveal, sound). 3-6 lines of Rook, max 7 words / 36 chars each.
   "ask" (film.json) = the question shown on top after the hook ("Can you see its face?").
5. Ending: either a LOOP (the last 0.5 s cuts back to the first shot, same sound, so it replays without a seam) or a
   CLIFFHANGER that the next film answers (then the next film is P7). Never a quiet ending, never a card.
6. Sound: near silence, Rook's whisper, then ONE loud sting at the reveal (gloamrun_sound cues), Hush hum under it.
7. Gate before render (write it in film.json "gate"): premise sentence, pattern, why a stranger stops scrolling at frame 0,
   the moment people will comment about. Preview frames at 0 s, 1.5 s, 3 s, the reveal and the last frame (40 %, 8 samples)
   and LOOK: if frame 0 is not instantly readable on a phone (dark / small / unclear), fix it before rendering.
8. film.json keys: film_no, title, pattern, hook, ask, question (first comment, either/or), synopsis, poster_t, lines, gate.
   Canon is unchanged (CANON.md, approved models, the Hush never speaks / never flies / can't be defeated).

## Old horizontal films still in the pipeline (Film 28 The Fog Sea)
Finish them as before (post3d.py makes the 16:9 film). Then the posting run makes the vertical cut with vcut.py.

## (old, horizontal) Making a new film

0. SUPERSEDED by VIRAL FORMAT for every new film. Kept for reference.
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

## Review (from 2026-11-27, replaces the old hashtag-by-hashtag tests)
Every posting run: Metricool views / avg watch / likes / comments / shares of every Gloamrun short on YouTube (YTVP), TikTok
(TKPO) and Instagram reels, at 48 h and 7 d. Write film3d/patterns.md: per pattern the median 48 h views and best result,
and the list of HITS (>= 5,000 views on any network). Then ONE big lever per review, not hashtags: which pattern next,
hook wording style, first-frame look, length, loop vs cliffhanger. Double down on hits: a hit's pattern goes again within
2 days, and its footage gets a "Part 2" or a new cut. A pattern with 3 misses in a row (< 1,000 views everywhere) is dropped
for 2 weeks. Write the change under "Current rules" with the date.

## Current rules (auto-updated)
- 2026-11-28: subtitle lines must fit the centre 720 px of a 1280 frame (about 38 characters max, split longer lines into two shots) so every shot can be used in vertical cuts. Vertical (9:16) films from the PC are preferred over horizontal ones.
- 2026-11-27 (owner's order, big change): VIRAL FORMAT replaces horizontal films. The older entries below were tests on
  108 s horizontal films; keep only what still fits a vertical short (hook wording = a new threat line from this film's
  place, not "Don't move."; first-comment either/or question; horror hashtags on TikTok/IG/YouTube).
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
- 2026-11-21 (ops fix, not a test): right after a push, raw.githubusercontent.com/.../main/ URLs can 404 for minutes (YouTube thumbnail failed on Films 20-21). Posting runs send media and
  videoThumbnailUrl as https://raw.githubusercontent.com/ranta46/ranta-videos/<commit sha>/<path> (git log -1 --format=%H on the commit that added the file).
- 2026-11-22: hook wording test (21-23) CLOSED, KEEP (IG avg watch 19-28 s vs 12-16 s for "Don't move." hooks): keep writing hooks whose 2nd sentence is a new threat line
  from this film's place, not "Don't move." / "Not a sound." / "Don't breathe.". New (story pace, from the next film made, 3D and 2D): the first big scare comes earlier: the Hush
  reaches the last car (very close, Rook flinches, a short line like "...It's at the last car!") by 9 s of the film itself (was ~15 s), because viewers leave at 15-25 s on every
  network. The rest of the act keeps its shape. Judge on IG avg watch of the next 3 new films vs films 20 / 21 / 23 (27.6 / 19.2 / 21.5 s); roll back if worse.
- 2026-11-23: IG avg watch is now good (19-28 s on films 20-24) but IG views stay at 115-175 per Reel, so test reach (description text, Instagram only, posting run,
  new films from Film 25; vault and other networks unchanged): Instagram hashtags = "#Gloamrun #animation #horror #creepy #scary #spooky" (instead of
  "#Gloamrun #TheHush #animation #shortfilm #spooky"). Judge on IG views of the next 3 new films vs films 20 / 21 / 23 / 24 (174 / 131 / 153 / 124); roll back if not
  better. Poster-hook test: judge again on films 22 / 24 / 25 (YouTube thumbnail failed on 20-21).
- 2026-11-24: TikTok horror hashtags look good (Film 24: 11 -> 140 views on day 2, 17 likes); YouTube is the weakest network for films (13-74 views). New (description text, YouTube only, posting
  run, new films from Film 26; vault, Facebook and other networks unchanged): YouTube description hashtags = "#Gloamrun #animation #horror #creepy #scary" (instead of
  "#Gloamrun #TheHush #animation #shortfilm") and youtubeData tags = ["Gloamrun","Rook and the Hush","horror animation","creepy","scary","animated short film","monster"].
  Judge on YouTube views at day 3-5 of films 26-28 vs 3D films 19-21 (39 / 54 / 74); roll back if not better.
- 2026-11-25: first-comment test (22-24) CLOSED, KEEP (IG 1 comment on every film since 22 vs 0 on 17-21; YouTube 23/24 got 1 each). New (cold open): the film.json "hook" is
  burned as big text over the 3 s cold open (same look and corner as the poster; post3d.py does it automatically when film.json has "hook"; 2D fallback films do the same
  over their first 3 s). PC run: keep writing "hook" and "hook_corner" (corner away from the Hush's face and Rook), check one cold-open frame by eye. From the next film
  finished (Film 27). Judge on IG 3 s skip of the next 3 new films vs films 20-25 (~39 % avg); roll back if not lower.
- 2026-11-25 (ops fix, not a test): Metricool can say "Tiktok internal error" while the video still goes up (Film 25 is on TikTok twice). Before re-sending a TikTok post
  marked ERROR, wait ~10 min and check TikTok posts (getAnalyticsDataByMetrics TKPO02, TKPO05) or the account for that film; re-send only if it is not there.
- 2026-11-26: TikTok horror-tags test (22 / 24 / 25) CLOSED, KEEP (197 / 140 / 112 views, 17 / 17 / 11 likes vs 139 / 137 and 9 / 11 for 20-21). New (description text, TikTok only, posting
  run, new films from Film 28; vault and other networks unchanged): TikTok has no first comment and 0 comments on every film, so the TikTok caption gets the film's either/or
  "question" as its own line right before "Full ride link in bio.". Judge on TikTok comments + likes of films 28-30 vs 22 / 24 / 25 / 26 (0 comments; 17 / 17 / 11 / 0 likes);
  roll back if not better. Still running: IG horror tags (25 / 26 / 27), YouTube tags (26-28), cold-open hook text (27-29).
