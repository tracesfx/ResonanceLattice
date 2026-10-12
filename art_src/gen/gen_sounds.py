"""Build the Resonance Lattice weapon sounds as processed derivatives of vanilla Starsector sounds.

python art_src/gen/gen_sounds.py            # writes sounds/rsl/*.ogg (mono 44.1 kHz Vorbis via ffmpeg)

User, 2026-10-12: the first, fully synthesised set ("bells and strings") sounded like musical instruments and out of
place next to vanilla. This set starts from the vanilla sounds each weapon used before the rail rework and reshapes
them: strong pitch (speed) shifts, EQ, layering two vanilla shots (e.g. a railgun crack under an ion/pulse zap for
"energy rail"), a quiet octave-up "ghost" copy for an energy shimmer, modulation (flanger / phaser / chorus) and a very
short metallic slap-back for the lattice "ring". No tonal synthesis (bells/strings were rejected). Ids are registered in data/config/sounds.json by tools/gen_data.py.
"""
import os
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CORE = os.path.abspath(os.path.join(ROOT, "..", "..", "starsector-core"))
OUT = os.path.join(ROOT, "sounds", "rsl")
FFMPEG = "ffmpeg"
for cand in ("C:/ffmpeg/ffmpeg.exe", "C:/ffmpeg/bin/ffmpeg.exe"):
    if os.path.isfile(cand):
        FFMPEG = cand

RAIL = "sounds/sfx_wpn_guns/rail_gun_fire_01.ogg"
GAUSS = "sounds/sfx_wpn_guns/gauss_cannon_fire_01.ogg"
FLAK = "sounds/sfx_wpn_guns/flak_fire_01.ogg"
PULSE = "sounds/sfx_wpn_energy/pulse_laser_fire_%02d.ogg"
ION = "sounds/sfx_wpn_energy/ion_cannon_fire_01.ogg"
HBLAST = "sounds/sfx_wpn_energy/heavy_blaster_fire_01.ogg"
KBLAST = "sounds/sfx_wpn_energy/kinetic_blaster_01.ogg"
MINING = "sounds/sfx_wpn_energy/mining_blaster_fire_01.ogg"
TACHYON = "sounds/sfx_wpn_energy/tachyon_lance_fire_01.ogg"
PILUM = "sounds/sfx_wpn_missiles/pilum_lrm_fire_01.ogg"
REAPER = "sounds/sfx_wpn_missiles/reaper_fire_01.ogg"


def pitch(p):
    """Game-style pitch: speed and pitch change together."""
    return "asetrate=44100*%.3f,aresample=44100" % p


def build(name, layers, post=""):
    """layers: [(vanilla file, pitch, gain, extra filter or "")]; post: filter applied to the mix."""
    args = [FFMPEG, "-y", "-loglevel", "error"]
    chains = []
    for i, (f, p, g, extra) in enumerate(layers):
        args += ["-i", os.path.join(CORE, f)]
        chain = "[%d:a]aformat=channel_layouts=mono,%s,volume=%.2f%s[l%d]" % (i, pitch(p), g,
                                                                             ("," + extra) if extra else "", i)
        chains.append(chain)
    mix = "".join("[l%d]" % i for i in range(len(layers)))
    graph = ";".join(chains) + ";%samix=inputs=%d:duration=longest:normalize=0%s,alimiter=limit=0.9[out]" % (
        mix, len(layers), ("," + post) if post else "")
    out = os.path.join(OUT, name + ".ogg")
    # two passes: render, measure the peak, then render again normalised to a -1 dB peak (as vanilla's samples)
    probe = subprocess.run(args[:3] + ["info"] + args[4:] + ["-filter_complex", graph + ";[out]volumedetect[v]", "-map", "[v]", "-f", "null", "-"],
                           check=True, capture_output=True, text=True).stderr
    peak = float(probe.split("max_volume:")[1].split("dB")[0])
    graph += ";[out]volume=%.2fdB[norm]" % (-1.0 - peak)
    subprocess.run(args + ["-filter_complex", graph, "-map", "[norm]", "-c:a", "libvorbis", "-q:a", "6", "-ac", "1",
                           "-ar", "44100", out], check=True)
    print("%-24s peak %+.1f dB -> -1 dB" % (name, peak))


# Effects (v3, user: "make them more different from vanilla - pitch them up more or add effects"):
RING = "aecho=0.8:0.5:17|29:0.25|0.15"                         # short metallic slap-back: the lattice "ring"
FLANGE = "flanger=delay=1.5:depth=3:speed=0.6:width=80"         # jet-like sweep: energy, not powder
FLANGE_FAST = "flanger=delay=1:depth=2:speed=4:width=90"
PHASE = "aphaser=type=t:speed=1.6:decay=0.55:in_gain=0.8"
CHORUS = "chorus=0.6:0.85:18|31:0.35|0.3:0.4|0.55:1.6|2.2"     # doubled, crystalline smear
GRIT = "acrusher=bits=10:mix=0.18:mode=log"                      # a little digital crackle


def ghost(f, p, g=0.25):
    """The same shot an octave-plus higher, quiet and high-passed: an energy shimmer over the body (not a tone)."""
    return (f, p, g, "highpass=f=1500")


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".ogg"):
            os.remove(os.path.join(OUT, f))
    # PD micro-rail: IR pulse laser, much quicker and brighter, thin low end, swept
    for k in range(1, 4):
        build("rsl_chime_fire_%d" % k, [(PULSE % k, 1.45, 1.0, "highpass=f=450"), ghost(PULSE % k, 2.4, 0.3)],
              FLANGE_FAST)
    # Pizzicato: small rail - a railgun crack pitched well up, a pulse zap, shimmer, phased
    build("rsl_pizzicato_fire", [(RAIL, 1.55, 0.9, ""), (PULSE % 2, 1.35, 0.4, ""), ghost(RAIL, 2.6, 0.25)],
          PHASE + "," + RING)
    # Shard Caster: mining blaster bite + a high rail snap, doubled and gritty
    build("rsl_shard_fire", [(MINING, 1.40, 0.8, ""), (RAIL, 1.75, 0.5, "highpass=f=500")], CHORUS + "," + GRIT)
    # Crystal Flechette: flak punch + rail crack, doubled
    build("rsl_flechette_fire", [(FLAK, 1.35, 0.7, ""), (RAIL, 1.40, 0.7, ""), ghost(RAIL, 2.3, 0.2)],
          CHORUS + "," + RING)
    # Lattice Lance: railgun body + ion-cannon tail, phased
    build("rsl_lance_fire", [(RAIL, 1.18, 1.0, ""), (ION, 1.40, 0.5, ""), ghost(RAIL, 2.2, 0.25)],
          PHASE + "," + RING)
    # Arpeggio: three rising notes - each variant a step higher
    for k, pp in ((1, 1.20), (2, 1.32), (3, 1.45)):
        build("rsl_arpeggio_fire_%d" % k, [(PULSE % (k + 2), pp, 0.8, ""), (RAIL, pp + 0.15, 0.45, "")], FLANGE)
    # Sostenuto Rail: heavy and rapid - railgun + kinetic blaster, a slow wobble
    build("rsl_sostenuto_fire", [(RAIL, 0.98, 0.9, ""), (KBLAST, 1.15, 0.5, ""), ghost(RAIL, 1.9, 0.2)],
          "vibrato=f=9:d=0.25," + PHASE + ",lowpass=f=10000")
    # Harmonic Driver charge: the tachyon wind-up, higher, with a sweeping flange
    build("rsl_charge", [(TACHYON, 1.25, 0.8, ""), ghost(TACHYON, 2.0, 0.2)], FLANGE)
    # Harmonic Driver: gauss cannon + heavy blaster, phased
    build("rsl_driver_fire", [(GAUSS, 1.12, 1.0, ""), (HBLAST, 1.30, 0.5, ""), ghost(GAUSS, 2.0, 0.22)],
          PHASE + "," + RING)
    # Spinal driver: deep gauss + heavy blaster + a long flanged slap-back
    build("rsl_spinal_fire", [(GAUSS, 0.90, 1.0, ""), (HBLAST, 1.00, 0.55, ""), ghost(GAUSS, 1.8, 0.25)],
          FLANGE + ",aecho=0.8:0.6:23|41:0.3|0.2")
    # Sforzando: the Virtuoso's voice - a sharp, high railgun crack, a bright accent and a fast flanged shimmer
    build("rsl_sforzando_fire", [(RAIL, 1.32, 1.0, ""), (PULSE % 1, 1.60, 0.4, "highpass=f=600"),
                                 ghost(RAIL, 2.6, 0.32)], FLANGE_FAST + "," + RING)
    # Cantus flak, Tuning Spike, Resonance Bloom: their vanilla bases, retuned with effects
    build("rsl_flak_fire", [(FLAK, 1.25, 1.0, "")], FLANGE)
    build("rsl_spike_fire", [(PILUM, 1.35, 1.0, ""), ghost(PILUM, 2.2, 0.2)], PHASE)
    build("rsl_bloom_fire", [(REAPER, 1.05, 1.0, ""), ghost(REAPER, 1.8, 0.2)], CHORUS)


if __name__ == "__main__":
    main()
