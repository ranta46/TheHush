"""GLOAMRUN sound kit — canonical instruments and mastering.
Sound canon:
  - The train: wheel clacks (clack-clack), steam whistle, the station bell.
  - The Hush: a low drone that rises when it is near, a breathy "shhh", heavy steps. When the Hush is very close, music drops out (it eats sound).
  - Thrill: a pulsing D-minor ostinato (pluck + bass) — the main music of every chase.
  - Surprise: one stinger hit. Fear: silence + one heartbeat.
  - The Long Back: a slow whale call. Dawn / hope: bell chime in D major.
  - THEME (brass bell): D F A G F E D. The end card always plays snd.title_music().
"""
import numpy as np, math, wave
from scipy.signal import lfilter, butter

SR = 44100
TITLE_LEN = 3.5
THEME = [(74, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 2)]      # D F A G F E D
THEME_HOPE = [(74, 1), (78, 1), (81, 1), (86, 2)]                          # D F# A D (major, only at dawn / relief)
MINOR = [62, 65, 69, 72, 74, 77]      # D minor arpeggio pool

def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def tt(dur): return np.arange(int(dur * SR)) / SR

class Score:
    def __init__(self, dur, seed=5):
        self.dur = dur; self.N = int(SR * dur); self.L = np.zeros(self.N); self.R = np.zeros(self.N)
        self.rng = np.random.default_rng(seed); self.duck = np.ones(self.N)

    def add(self, sig, t0, gain=1.0, pan=0.0, music=False):
        i0 = int(t0 * SR)
        if i0 >= self.N or i0 < 0 or len(sig) == 0: return
        sig = sig[: self.N - i0] * gain
        if music: sig = sig * self.duck[i0:i0 + len(sig)]
        l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
        self.L[i0:i0 + len(sig)] += sig * l * 1.41; self.R[i0:i0 + len(sig)] += sig * r * 1.41

    def silence_music(self, t0, t1, depth=0.9):
        """the Hush eats sound: music added AFTER this call is ducked between t0..t1"""
        a, b = int(t0 * SR), int(t1 * SR); n = b - a
        if n <= 0: return
        ramp = np.ones(n); k = min(int(0.25 * SR), n // 2)
        ramp[:k] = np.linspace(1, 1 - depth, k); ramp[k:n - k] = 1 - depth; ramp[n - k:] = np.linspace(1 - depth, 1, k)
        self.duck[a:b] = np.minimum(self.duck[a:b], ramp)

    # ---------- instruments
    def _filt(self, x, lo=None, hi=None):
        if lo and hi: b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
        elif hi: b, a = butter(2, hi / (SR / 2), "low")
        else: b, a = butter(2, lo / (SR / 2), "high")
        return lfilter(b, a, x)

    def bell(self, m, dur=2.6):
        t = tt(dur); f = mtof(m); s = np.zeros_like(t)
        for ratio, amp, dec in ((1, 1, 2.2), (2.0, .5, 3.5), (2.76, .35, 4.5), (5.4, .2, 7), (8.9, .1, 10)):
            s += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
        return s * np.minimum(1, t / 0.002) * 0.6

    def pluck(self, m, dur=0.35):
        t = tt(dur); f = mtof(m)
        s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (8 + k * 3)) for k in range(1, 7))
        return s * np.minimum(1, t / 0.003)

    def bass(self, m, dur):
        t = tt(dur); f = mtof(m)
        return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)

    def clack(self):
        t = tt(0.09); n = self.rng.normal(size=len(t))
        return (self._filt(n, 1500, 5000) * 0.8 + np.sin(2 * np.pi * 320 * t)) * np.exp(-t * 70)

    def whistle(self, dur=1.4):
        t = tt(dur); f = 880 * (1 + 0.03 * np.minimum(1, t / 0.15)) * (1 - 0.04 * np.maximum(0, t - dur + 0.3))
        ph = np.cumsum(f) / SR * 2 * np.pi
        s = np.sin(ph) + 0.6 * np.sin(ph * 1.26) + 0.3 * self._filt(self.rng.normal(size=len(t)), 700, 2400)
        return s * np.minimum(1, t / 0.08) * np.clip((dur - t) / 0.25, 0, 1) * 0.4

    def drone(self, dur, base=38):
        t = tt(dur); f = mtof(base)
        s = sum(np.sin(2 * np.pi * f * k * (1 + 0.002 * j) * t + j) / k for k in (1, 2, 3) for j in (-1, 1))
        trem = 0.75 + 0.25 * np.sin(2 * np.pi * 0.35 * t)
        return s * trem * np.minimum(1, t / 1.2) * np.clip((dur - t) / 1.0, 0, 1) * 0.3

    def shh(self, dur=1.6):
        t = tt(dur); n = self._filt(self.rng.normal(size=len(t)), 2500, 9000)
        return n * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 * 0.9

    def thump(self):
        t = tt(0.7); return (np.sin(2 * np.pi * (60 - 25 * t) * t) + 0.3 * self._filt(self.rng.normal(size=len(t)), None, 300)) * np.exp(-t * 7)

    def heartbeat(self):
        t = tt(0.5); b = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 18)
        out = np.zeros(int(0.5 * SR)); out[:len(b)] += b; k = int(0.18 * SR); out[k:] += 0.7 * b[:len(out) - k]; return out

    def stinger(self):
        t = tt(1.8); boom = np.sin(2 * np.pi * (50 - 15 * t) * t) * np.exp(-t * 3)
        hi = sum(np.sin(2 * np.pi * mtof(m) * t) for m in (86, 87, 93)) * np.exp(-t * 4) * 0.25
        return (boom + hi) * np.minimum(1, t / 0.004)

    def whale(self, dur=3.0):
        t = tt(dur); f = 210 - 90 * (t / dur) + 8 * np.sin(2 * np.pi * 5 * t)
        ph = np.cumsum(f) / SR * 2 * np.pi
        return (np.sin(ph) + 0.4 * np.sin(2 * ph)) * np.sin(np.pi * t / dur) ** 0.8 * 0.6

    def wind(self, dur, amt=1.0):
        n = self._filt(self.rng.normal(size=int(dur * SR)), 200, 1400); t = tt(dur)
        return n * (0.6 + 0.4 * np.sin(t * 0.7)) * amt * 0.5

    # ---------- helpers
    def train_rhythm(self, t0, t1, period=0.42, gain=0.18):
        """clack-clack every `period` seconds while the train runs (faster train = smaller period)"""
        for ts in np.arange(t0, t1, period):
            self.add(self.clack(), ts, gain, -0.2); self.add(self.clack(), ts + period * 0.22, gain * 0.8, 0.2)

    def chase(self, t0, t1, bpm=150, gain=0.16, root=50):
        """the thrill ostinato (D minor): pluck 8ths + bass on the beat"""
        beat = 60 / bpm; i = 0
        for ts in np.arange(t0, t1, beat / 2):
            m = MINOR[[0, 2, 1, 2, 3, 2, 1, 2][i % 8]] + 12
            self.add(self.pluck(m), ts, gain * (1.0 if i % 2 == 0 else 0.7), 0.3 if i % 2 else -0.3, music=True)
            if i % 2 == 0: self.add(self.bass(root if (i // 8) % 2 == 0 else root - 2, beat * 0.9), ts, gain * 1.3, 0, music=True)
            i += 1

    def play(self, seq, t0, beat, gain, transpose=0, inst="bell"):
        t = t0
        for m, d_ in seq:
            if m: self.add((self.bell if inst == "bell" else self.pluck)(m + transpose), t, gain, 0.2 * (1 if m % 2 else -1), music=True)
            t += d_ * beat
        return t

    def steps(self, t0, t1, period=0.9, gain=0.5):
        """the Hush walking"""
        for ts in np.arange(t0, t1, period): self.add(self.thump(), ts, gain)

    def title_music(self):
        """Canonical end card (TITLE_LEN). Bell THEME head (D F A), then a soft open fifth. Do not change."""
        t0 = self.dur - TITLE_LEN
        self.add(self.drone(TITLE_LEN, 38), t0, 0.4)
        self.play([(74, 1), (77, 1), (81, 2)], t0 + 0.1, 0.34, 0.22)
        for i, m in enumerate([62, 69, 74, 81]): self.add(self.bell(m, 2.8), t0 + 1.5 + i * 0.05, 0.09, -0.3 + i * 0.2)

    def write(self, path):
        def reverb(x):
            y = x.copy()
            for d_, g in ((0.043, .35), (0.071, .3), (0.101, .24), (0.151, .18), (0.227, .13), (0.331, .09)):
                k = int(d_ * SR); y[k:] += x[:-k] * g
            return y
        L, R = self.L, self.R
        L2 = L + 0.3 * reverb(R) + reverb(L) * 0.35; R2 = R + 0.3 * reverb(L) + reverb(R) * 0.35
        t = np.arange(self.N) / SR; fade = np.minimum(1, t / 0.05) * np.clip((self.dur - t) / 1.0, 0, 1)
        st = np.stack([L2 * fade, R2 * fade], 1); st = np.tanh(st / (np.max(np.abs(st)) + 1e-9) * 1.4) * 0.88
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
