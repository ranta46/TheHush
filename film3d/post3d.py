"""Finish a 3D GLOAMRUN film (cloud). Input: raw.mp4 encoded by Blender (no sound, no text).
  python3 post3d.py films/film01 raw.mp4      -> films/film01/out/gloamrun_filmNN_16x9.mp4 + poster
films/filmNN/film.json: {"film_no","title","synopsis","poster_t","note","lines":[[t0,t1,"text"],...]}
films/filmNN/score.py: def score(S): ...   (gloamrun_sound cues, seconds from film start)
Rook's lines are drawn exactly like the 2D canon (engine.draw_line). End card = film card from film_kit/film.py.
"""
import sys, os, json, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.join(HERE, "..", "film_kit"); sys.path.insert(0, KIT)
import gloamrun_engine as E, gloamrun_sound as S, film as FK
from PIL import Image
def run(a): subprocess.run(a, check=True)
def main():
    fd, raw = sys.argv[1], sys.argv[2]; meta = json.load(open(os.path.join(fd, "film.json")))
    for _, _, t in meta["lines"]:
        E.check_english(t); assert len(t) <= 44 and len(t.split()) <= 9, t
    tmp = os.path.join(fd, "tmp"); out = os.path.join(fd, "out"); os.makedirs(tmp, exist_ok=True); os.makedirs(out, exist_ok=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", raw]).decode().strip())
    # subtitle overlays (one transparent PNG per line, same look as the 2D films)
    ins, flt, last = ["-i", raw], "", "[0:v]"
    for i, (t0, t1, txt) in enumerate(meta["lines"]):
        img = Image.new("RGBA", (1280, 720), (0, 0, 0, 0)); E.draw_line(img, (t0 + t1) / 2, [(t0, t1, txt)], "h")
        p = os.path.join(tmp, f"line{i}.png"); img.save(p); ins += ["-i", p]
        flt += f"{last}[{i+1}:v]overlay=0:0:enable='between(t,{t0},{t1})'[v{i}];"; last = f"[v{i}]"
    flt += f"{last}fade=t=out:st={dur-0.6}:d=0.6,format=yuv420p[vo]"
    body = os.path.join(tmp, "body.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", flt, "-map", "[vo]", "-r", "24", "-c:v", "libx264", "-crf", "19", "-preset", "medium", body])
    card = os.path.join(tmp, "card.mp4"); FK.render_card(card, meta["film_no"], meta["title"], meta.get("note"))
    lst = os.path.join(tmp, "list.txt"); open(lst, "w").write(f"file '{os.path.abspath(body)}'\nfile '{os.path.abspath(card)}'\n")
    vid = os.path.join(tmp, "video.mp4"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    total = dur + FK.CARD; sc = S.Score(total)
    spec = importlib.util.spec_from_file_location("score", os.path.join(fd, "score.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.score(sc, dur)
    t0 = total - FK.CARD; sc.add(sc.drone(FK.CARD, 38), t0, 0.4); sc.play([(74, 1), (77, 1), (81, 2)], t0 + 0.2, 0.4, 0.22)
    for i, mm in enumerate([62, 69, 74, 81]): sc.add(sc.bell(mm, 3.5), t0 + 1.8 + i * 0.05, 0.09, -0.3 + i * 0.2)
    wav = os.path.join(tmp, "audio.wav"); sc.write(wav)
    tag = f"gloamrun_film{meta['film_no']:02d}"; final = os.path.join(out, f"{tag}_16x9.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final])
    poster = os.path.join(out, f"{tag}_poster.jpg")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(meta.get("poster_t", 30)), "-i", raw, "-frames:v", "1", "-q:v", "3", poster])
    info = dict(meta, duration=round(total, 1), video=os.path.basename(final), poster=os.path.basename(poster), size_mb=round(os.path.getsize(final) / 1e6, 1))
    info.pop("lines", None); json.dump(info, open(os.path.join(out, f"{tag}_meta.json"), "w"), indent=1); print(json.dumps(info))
if __name__ == "__main__":
    main()
