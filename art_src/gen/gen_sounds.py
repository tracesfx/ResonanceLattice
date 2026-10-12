"""Synthesise every Resonance Lattice weapon sound from scratch (no vanilla or third-party samples).

python art_src/gen/gen_sounds.py            # writes sounds/rsl/*.ogg (mono 44.1 kHz Vorbis via ffmpeg)

Sound language: the Choir's guns are rail accelerators that *ring*. Every fire sound = a sharp electromagnetic crack
(filtered noise burst + falling "zhoom" chirp) + a tuned, inharmonic bell/string partial set that gives each weapon
its own note (small guns high, large guns low) + a low thump scaled to the calibre. Impacts: shields ring like struck
glass, hull cracks like stressed metal. Ids are registered in data/config/sounds.json by tools/gen_data.py.
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "sounds", "rsl")
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
for cand in ("C:/ffmpeg/ffmpeg.exe", "C:/ffmpeg/bin/ffmpeg.exe"):
    if os.path.isfile(cand):
        FFMPEG = cand
RNG = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def env(t, attack, decay, hold=0.0):
    """Linear attack, optional hold, exponential decay (decay = time constant in s)."""
    e = np.where(t < attack, t / max(attack, 1e-5), np.exp(-np.maximum(0.0, t - attack - hold) / decay))
    return e


def band_noise(dur, lo, hi):
    n = RNG.standard_normal(int(dur * SR))
    f = np.fft.rfft(n)
    fr = np.fft.rfftfreq(len(n), 1 / SR)
    mask = 1 / (1 + ((fr - (lo + hi) / 2) / max(1.0, (hi - lo) / 2)) ** 4)
    out = np.fft.irfft(f * mask, len(n))
    return out / (np.abs(out).max() + 1e-9)


def chirp(t, f0, f1, tau):
    """Exponential glide f0 -> f1 with time constant tau."""
    f = f1 + (f0 - f1) * np.exp(-t / tau)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def bell(t, f0, decay, partials=((1, 1.0), (2.76, 0.5), (5.40, 0.25), (8.93, 0.12)), detune=0.0):
    out = np.zeros_like(t)
    for k, a in partials:
        out += a * np.sin(2 * np.pi * f0 * k * (1 + detune * (k - 1) * 0.001) * t) * np.exp(-t * k ** 0.5 / decay)
    return out


def pluck(dur, f0, damp=0.996):
    """Karplus-Strong string (the Pizzicato is literally plucked)."""
    n = int(dur * SR)
    p = int(SR / f0)
    buf = RNG.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def thump(t, f0, decay):
    return np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2 * np.exp(-t / 0.01))) / SR) * np.exp(-t / decay)


def mix(*parts):
    n = max(len(p) for p, _ in parts)
    out = np.zeros(n)
    for p, g in parts:
        out[:len(p)] += g * p
    return out


def crack(dur, lo, hi, decay):
    t = t_axis(dur)
    return band_noise(dur, lo, hi) * env(t, 0.0008, decay)


def rail(dur, note, weight, zhoom=(2400, 300, 0.05), ring=0.35):
    """Generic rail shot: crack + zhoom + tuned bell + thump. weight 0.5 (small) .. 2 (large)."""
    t = t_axis(dur)
    return mix((crack(dur, 1500, 9000, 0.012 * weight), 0.9),
               (crack(dur, 200, 1800, 0.035 * weight), 0.6 * weight),
               (chirp(t, *zhoom) * env(t, 0.002, 0.06 * weight), 0.45),
               (bell(t, note, ring * weight, detune=3) * env(t, 0.004, 9), 0.5),
               (thump(t, 55 / weight ** 0.3, 0.06 * weight), 0.5 * weight))


def finish(x, fade=0.03):
    x = x - x.mean()
    n = int(fade * SR)
    if n and len(x) > n:
        x[-n:] *= np.linspace(1, 0, n)
    x[:32] *= np.linspace(0, 1, 32)
    return 0.89 * x / (np.abs(x).max() + 1e-9)


def write(name, x):
    os.makedirs(OUT, exist_ok=True)
    pcm = (finish(x) * 32767).astype("<i2")
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, name + ".wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        ogg = os.path.join(OUT, name + ".ogg")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "6", "-ac", "1",
                        ogg], check=True)
    print("%-26s %.2f s" % (name + ".ogg", len(pcm) / SR))


# note frequencies (equal temperament)
def hz(n):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1,
             "B": 2}
    return 440.0 * 2 ** ((names[n[:-1]] + 12 * (int(n[-1]) - 4)) / 12)


def main():
    # point defence: a tiny tick + a high glass chime
    t = t_axis(0.3)
    write("rsl_chime_fire", mix((crack(0.3, 3000, 12000, 0.004), 0.7),
                                (bell(t, hz("E7"), 0.12, ((1, 1), (2.4, 0.4), (4.1, 0.2))), 0.6),
                                (chirp(t, 5000, 1500, 0.01) * env(t, 0.001, 0.015), 0.3)))
    # Pizzicato: plucked rail string
    t = t_axis(0.55)
    write("rsl_pizzicato_fire", mix((crack(0.55, 2000, 10000, 0.008), 0.8),
                                    (pluck(0.55, hz("A5"), 0.9965), 0.7),
                                    (chirp(t, 3200, 500, 0.03) * env(t, 0.001, 0.04), 0.4),
                                    (thump(t, 70, 0.04), 0.35)))
    # Shard rail (Shard Caster, Crystal Flechette): crack + crystal shatter
    t = t_axis(0.5)
    shatter = np.zeros_like(t)
    for _ in range(9):
        t0 = RNG.uniform(0.0, 0.06)
        f = RNG.uniform(3000, 8000)
        tt = np.maximum(0, t - t0)
        shatter += (t >= t0) * np.sin(2 * np.pi * f * tt) * np.exp(-tt / RNG.uniform(0.02, 0.07))
    write("rsl_shard_fire", mix((crack(0.5, 1200, 9000, 0.015), 0.9), (shatter / 4, 0.7),
                                (thump(t, 65, 0.05), 0.5), (bell(t, hz("F#6"), 0.15), 0.25)))
    write("rsl_flechette_fire", mix((crack(0.6, 800, 7000, 0.022), 0.9), (shatter / 4, 0.6),
                                    (thump(t_axis(0.6), 55, 0.07), 0.6), (bell(t_axis(0.6), hz("C#6"), 0.2), 0.3)))
    # medium rails
    write("rsl_lance_fire", rail(0.8, hz("E5"), 1.2, (2600, 260, 0.06), 0.45))
    write("rsl_arpeggio_fire", rail(0.6, hz("C#6"), 1.0, (3000, 400, 0.04), 0.35))
    # Sostenuto: punchy heavy rail with a sustained hum (it fires fast; the hum overlaps into a held note)
    t = t_axis(0.5)
    hum = np.sin(2 * np.pi * hz("G3") * t) + 0.4 * np.sin(2 * np.pi * hz("G3") * 2.01 * t)
    write("rsl_sostenuto_fire", mix((rail(0.5, hz("G4"), 1.5, (1800, 200, 0.05), 0.3), 1.0),
                                    (hum * env(t, 0.01, 0.25), 0.35)))
    # Harmonic Driver: charge whine (fireSoundOne) + a deep, ringing heavy shot
    t = t_axis(1.6)
    whine = np.sin(2 * np.pi * np.cumsum(180 + 1700 * (t / 1.6) ** 2) / SR)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(6 + 30 * t / 1.6) / SR)
    crackle = band_noise(1.6, 2000, 8000) * (t / 1.6) ** 3 * (RNG.random(len(t)) < 0.02)
    write("rsl_charge", mix((whine * trem * np.minimum(1, t / 0.2), 0.6), (crackle, 0.5),
                            (bell(t, hz("D4"), 2.0) * (t / 1.6) ** 2, 0.25)))
    write("rsl_driver_fire", rail(1.6, hz("D4"), 2.0, (1500, 120, 0.09), 0.9))
    write("rsl_spinal_fire", mix((rail(2.0, hz("A3"), 2.4, (1300, 90, 0.11), 1.1), 1.0),
                                 (bell(t_axis(2.0), hz("E4"), 1.6), 0.25)))
    # Sforzando: the Virtuoso's accented voice - very sharp attack, bright bell
    write("rsl_sforzando_fire", mix((rail(0.75, hz("A5"), 1.3, (4200, 380, 0.03), 0.5), 1.0),
                                    (crack(0.75, 5000, 14000, 0.006), 0.5)))
    # flak: thump + burst + a low bell
    t = t_axis(0.6)
    write("rsl_flak_fire", mix((crack(0.6, 150, 2500, 0.05), 1.0), (thump(t, 50, 0.08), 0.8),
                               (bell(t, hz("B3"), 0.25), 0.3)))
    # missiles: filtered noise whoosh + a tuning-fork tone
    t = t_axis(0.9)
    whoosh = band_noise(0.9, 400, 3500) * env(t, 0.03, 0.25)
    write("rsl_spike_fire", mix((whoosh, 0.9), (np.sin(2 * np.pi * 440 * t) * env(t, 0.005, 0.35), 0.35),
                                (crack(0.9, 2000, 9000, 0.006), 0.4)))
    t = t_axis(1.5)
    write("rsl_bloom_fire", mix((band_noise(1.5, 150, 1800) * env(t, 0.08, 0.5), 1.0),
                                (bell(t, hz("D3"), 1.0) + 0.6 * bell(t, hz("A3"), 1.0), 0.3),
                                (thump(t, 40, 0.15), 0.7)))
    # impacts
    t = t_axis(0.7)
    write("rsl_impact_shield", mix((bell(t, 1650, 0.35, ((1, 1), (1.51, 0.6), (2.37, 0.4), (3.9, 0.2)), 5), 0.6),
                                   (band_noise(0.7, 2500, 11000) * env(t, 0.001, 0.05), 0.6),
                                   (thump(t, 90, 0.04), 0.3)))
    t = t_axis(0.6)
    clank = bell(t, 340, 0.18, ((1, 1), (1.73, 0.7), (2.91, 0.5), (4.62, 0.3)))
    write("rsl_impact_hull", mix((crack(0.6, 300, 5000, 0.03), 1.0), (clank, 0.45), (thump(t, 60, 0.07), 0.6)))


if __name__ == "__main__":
    main()
