"""Build one GLOAMRUN FILM (horizontal, ~2-3 min) from several acts, with the canonical engine and sound kit.
  python3 film.py films/film01 --check            # canon lint for every act
  python3 film.py films/film01 --preview 2        # contact sheet, every 2 s of every act
  python3 film.py films/film01                    # full build -> films/film01/out/
A film folder has film.json {"film_no":N,"title":"...","synopsis":"...","note":"..."} and act1.py, act2.py, ...
Each act is written like an episode module (see episodes/ep01.py) but with ACT_LEN instead of DUR and no title card.
Same canon as the shorts (CANON.md): Rook / the Hush drawn ONLY by the engine, 12 poses, simple English, Rook is the only speaker.
Film rules: each act 26-40 s, max 8 lines per act (1 line = max 9 words / 44 chars), 3-5 acts, end card 5 s.
"""
import sys, os, json, math, glob, importlib.util, subprocess
import numpy as np
from multiprocessing import Process
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gloamrun_engine as E
import gloamrun_sound as S
CARD = 5.0

def load(path):
    spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(path))[0] + "_" + str(abs(hash(path))), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.DUR = m.ACT_LEN + E.TITLE_LEN; m.EP_NO = 0; m.EP_TITLE = "act"; return m

def lint(fd):
    errs = []; meta = json.load(open(os.path.join(fd, "film.json")))
    for k in ("title", "synopsis"):
        try: E.check_english(meta[k])
        except Exception as e: errs.append(f"film.json {k}: {e}")
    acts = sorted(glob.glob(os.path.join(fd, "act*.py")))
    if not 3 <= len(acts) <= 5: errs.append("need 3-5 acts")
    for p in acts:
        a = load(p); n = os.path.basename(p)
        if not 26 <= a.ACT_LEN <= 40: errs.append(f"{n}: ACT_LEN {a.ACT_LEN} not 26-40")
        L = getattr(a, "LINES", [])
        if len(L) > 8: errs.append(f"{n}: more than 8 lines")
        last = -1
        for t0, t1, txt in L:
            try: E.check_english(txt)
            except Exception as e: errs.append(f"{n}: {e}")
            if len(txt) > 44 or len(txt.split()) > 9: errs.append(f"{n}: line too long {txt!r}")
            if t1 - t0 < 1.0 or t0 < last: errs.append(f"{n}: bad timing {txt!r}")
            last = t1
        for i in range(int(a.ACT_LEN * 4)):
            t = i / 4; st = a.rook_state(t)
            if st:
                if st.get("pose") not in E.POSES: errs.append(f"{n} t={t}: pose {st.get('pose')}"); break
                if set(st) - set(E.ROOK_DEFAULT): errs.append(f"{n}: unknown rook keys"); break
                if not 0 <= st.get("eye", 1) <= 1.6: errs.append(f"{n} t={t}: eye"); break
            hs = a.hush_state(t) if hasattr(a, "hush_state") else None
            if hs and (hs.get("hand") not in E.HANDS or set(hs) - set(E.HUSH_DEFAULT)): errs.append(f"{n} t={t}: hush state"); break
    if errs: raise SystemExit("FILM CHECK FAILED:\n  " + "\n  ".join(errs))
    print("film check: OK", len(acts), "acts"); return meta, acts

def card(t, n, title, note):
    """film end card: same look as the episode card, says FILM n"""
    ow, oh = E.SIZES["h"]; img = E.Image.new("RGBA", (ow, oh), (8, 7, 20, 255)); k = t * (7.0 / CARD)
    E.add_glow(img, ow / 2, oh * 0.30, 360, (120, 130, 255), 0.25)
    E.draw_hush_eyes(img, ow / 2, oh * 0.17, 1.1, E.ease(E.seg(k, 0.0, 1.0)) * (1 - E.ease(E.seg(k, 4.5, 6.0))))
    a_r = E.ease(E.seg(k, 0.3, 1.1))
    if a_r > 0:
        tmp = E.Image.new("RGBA", (ow, oh), (0, 0, 0, 0))
        E.draw_rook(tmp, t, E.rook(sc=0.7, x=ow / 2, y=oh * 0.52, pose="wave" if k < 3.5 else "idle", flap=0.4 if k < 3.5 else 0, look=-0.35, blink=E.blink_at(k, [2.4, 5.0])))
        if a_r < 1: tmp.putalpha(tmp.getchannel("A").point(lambda q: int(q * a_r)))
        img.alpha_composite(tmp)
    y0 = int(oh * 0.58)
    E.text_center(img, y0, "GLOAMRUN", E.font(E.FONT_SERIF, 104), E.BRASS, E.ease(E.seg(k, 0.6, 1.6)), spacing=10)
    E.text_center(img, y0 + 136, f"FILM {n}", E.font(E.FONT_MED, 32), (230, 210, 180), E.ease(E.seg(k, 1.2, 2.1)), spacing=4)
    E.text_center(img, y0 + 184, title, E.font(E.FONT_BLACK, 42), (246, 242, 236), E.ease(E.seg(k, 2.0, 3.0)))
    E.text_center(img, oh - 64, note or "The last train runs again tomorrow.", E.font(E.FONT_MED, 26), E.BRASS, E.ease(E.seg(k, 3.0, 3.8)) * (1 - E.ease(E.seg(k, 6.3, 6.9))))
    E.text_center(img, oh - 30, "© 2026 Mori. Original work.", E.font(E.FONT_MED, 16), (150, 140, 170), E.ease(E.seg(k, 3.0, 3.8)))
    out = E.ease(E.seg(k, 6.5, 7.0))
    if out > 0: img.alpha_composite(E.Image.new("RGBA", (ow, oh), (0, 0, 0, int(255 * out))))
    return img.convert("RGB")

def render_act(path, out, last):
    a = load(path); rd = E.Renderer(a, "h")
    if not last: rd.story_end = a.ACT_LEN + 100   # no fade between acts
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(E.FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(round(a.ACT_LEN * E.FPS))): p.stdin.write(rd.frame(i / E.FPS).tobytes())
    p.stdin.close(); p.wait()

def render_card(out, n, title, note):
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(E.FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(CARD * E.FPS)): p.stdin.write(card(i / E.FPS, n, title, note).tobytes())
    p.stdin.close(); p.wait()

def main():
    fd = sys.argv[1]; meta, acts = lint(fd)
    if "--check" in sys.argv: return
    tmp = os.path.join(fd, "tmp"); out = os.path.join(fd, "out"); os.makedirs(tmp, exist_ok=True); os.makedirs(out, exist_ok=True)
    if "--preview" in sys.argv:
        step = float(sys.argv[sys.argv.index("--preview") + 1]); sheets = []
        for p in acts:
            a = load(p); times = [float(round(float(x), 1)) for x in np.arange(0.2, a.ACT_LEN, step)]
            sheets.append(E.preview(a, times, os.path.join(tmp, os.path.basename(p)[:-3]), "h"))
        print("\n".join(sheets)); return
    procs = []
    for i, p in enumerate(acts):
        pr = Process(target=render_act, args=(p, os.path.join(tmp, f"a{i}.mp4"), i == len(acts) - 1)); pr.start(); procs.append(pr)
    pc = Process(target=render_card, args=(os.path.join(tmp, "card.mp4"), meta["film_no"], meta["title"], meta.get("note"))); pc.start(); procs.append(pc)
    # sound: every act on one master score
    lens = [load(p).ACT_LEN for p in acts]; total = sum(lens) + CARD
    master = S.Score(total); off = 0.0
    for p, L in zip(acts, lens):
        a = load(p); sc = S.Score(L + 0.01); a.score(sc); i0 = int(off * S.SR); n = min(len(sc.L), master.N - i0)
        master.L[i0:i0 + n] += sc.L[:n]; master.R[i0:i0 + n] += sc.R[:n]; off += L
    t0 = total - CARD
    master.add(master.drone(CARD, 38), t0, 0.4); master.play([(74, 1), (77, 1), (81, 2)], t0 + 0.2, 0.4, 0.22)
    for i, m in enumerate([62, 69, 74, 81]): master.add(master.bell(m, 3.5), t0 + 1.8 + i * 0.05, 0.09, -0.3 + i * 0.2)
    wav = os.path.join(tmp, "audio.wav"); master.write(wav)
    for pr in procs: pr.join()
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(os.path.join(tmp, f'a{i}.mp4'))}'\n" for i in range(len(acts))) + f"file '{os.path.abspath(os.path.join(tmp, 'card.mp4'))}'\n")
    tag = f"gloamrun_film{meta['film_no']:02d}"; vid = os.path.join(out, f"{tag}_16x9.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", vid], check=True)
    poster = os.path.join(out, f"{tag}_poster.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(meta.get("poster_t", 20)), "-i", vid, "-frames:v", "1", "-q:v", "3", poster], check=True)
    info = dict(meta, duration=round(total, 1), video=os.path.basename(vid), poster=os.path.basename(poster), size_mb=round(os.path.getsize(vid) / 1e6, 1))
    json.dump(info, open(os.path.join(out, f"{tag}_meta.json"), "w"), indent=1); print(json.dumps(info))

if __name__ == "__main__":
    main()
