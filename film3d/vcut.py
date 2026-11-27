"""Vertical viral cut (9:16, 1080x1920) from a finished 16:9 Gloamrun film.  RUNBOOK_3D "Viral format" (2026-11-27).
  python3 vcut.py <film_16x9.mp4> <cut.json> <out.mp4>
cut.json: {"segs": [[t0,t1], ...]   seconds in the 16:9 video, in play order (20-35 s total),
           "hook": "4-7 easy words, the scariest fact",   shown big on top for the first 3.2 s
           "ask": "the question that keeps people watching",  shown on top after the hook
           "end": "Part 2? Follow.",                         shown on top for the last 2.5 s
           "x": 0.5}   horizontal centre of the square crop (0..1) - keep the Hush's face inside
Layout: square 720x720 crop of the film (its own subtitles stay readable) scaled to 1080x1080 in the middle,
big white text with dark outline above it, "GLOAMRUN" small below. Hard cuts, original sound.
"""
import sys, json, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
W, H, SQ, Y0 = 1080, 1920, 1080, 430
def run(a): subprocess.run(a, check=True)
def text_png(path, lines, size=92, y=0, color=(255, 255, 255)):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, size)
    while max(d.textlength(t, font=f) for t in lines) > W * 0.9: size -= 4; f = ImageFont.truetype(FONT, size)
    for t in lines:
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=color, stroke_width=max(5, size // 10), stroke_fill=(8, 10, 20))
        y += int(size * 1.2)
    im.save(path)
def split2(s):
    for sep in (". ", "? ", "! "):
        if sep in s.strip()[:-1]:
            a, b = s.split(sep, 1); return [a + sep.strip(), b]
    w = s.split(); k = (len(w) + 1) // 2; return [" ".join(w[:k]), " ".join(w[k:])]
def main():
    src, cfg, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
    tmp = tempfile.mkdtemp(); parts = []
    cx = float(cfg.get("x", 0.5)); x = int(max(0, min(1280 - 720, 1280 * cx - 360)))
    for i, (a, b) in enumerate(cfg["segs"]):
        p = os.path.join(tmp, f"s{i}.mp4"); parts.append(p)
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", src,
             "-vf", f"crop=720:720:{x}:0,scale={SQ}:{SQ}:flags=lanczos,pad={W}:{H}:0:{Y0}:color=0x07080f,setsar=1,fps=30",
             "-af", "aresample=48000", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", p])
    lst = os.path.join(tmp, "l.txt"); open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    body = os.path.join(tmp, "body.mp4"); run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", body])
    dur = sum(b - a for a, b in cfg["segs"])
    text_png(os.path.join(tmp, "hook.png"), split2(cfg["hook"]), 104, 110)
    text_png(os.path.join(tmp, "ask.png"), split2(cfg.get("ask", "Would you stay still?")), 84, 130, (255, 226, 140))
    text_png(os.path.join(tmp, "end.png"), split2(cfg.get("end", "Part 2? Follow.")), 96, 120, (255, 226, 140))
    text_png(os.path.join(tmp, "brand.png"), ["GLOAMRUN"], 54, Y0 + SQ + 70, (200, 205, 230))
    e0 = dur - 2.5
    flt = (f"[0:v][1:v]overlay=0:0:enable='lt(t,3.2)'[a];[a][2:v]overlay=0:0:enable='between(t,3.2,{e0})'[b];"
           f"[b][3:v]overlay=0:0:enable='gte(t,{e0})'[c];[c][4:v]overlay=0:0,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", body, *sum([["-i", os.path.join(tmp, n)] for n in ("hook.png", "ask.png", "end.png", "brand.png")], []),
         "-filter_complex", flt, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", out])
    print(out, round(dur, 1), "s")
if __name__ == "__main__":
    main()
