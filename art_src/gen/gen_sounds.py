"""Build the Resonance Lattice weapon sounds as processed derivatives of vanilla Starsector sounds.

python art_src/gen/gen_sounds.py            # writes sounds/rsl/*.ogg (mono 44.1 kHz Vorbis via ffmpeg)

User, 2026-10-12: the first, fully synthesised set ("bells and strings") sounded like musical instruments and out of
place next to vanilla. This set starts from the vanilla sounds each weapon used before the rail rework and reshapes
them so they still sit in the vanilla mix: pitch (speed) shifts, EQ, layering two vanilla shots (e.g. a railgun crack
under an ion/pulse zap for "energy rail"), and at most a very short metallic slap-back (aecho, < 40 ms) for the
lattice "ring". No tonal synthesis. Ids are registered in data/config/sounds.json by tools/gen_data.py.
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
    subprocess.run(args + ["-filter_complex", graph, "-map", "[out]", "-c:a", "libvorbis", "-q:a", "6", "-ac", "1",
                           "-ar", "44100", out], check=True)
    print(name)


# a short metallic slap-back: the lattice "ring" without a musical tone
RING = "aecho=0.8:0.5:17|29:0.25|0.15"


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".ogg"):
            os.remove(os.path.join(OUT, f))
    # PD micro-rail: the IR pulse laser, quicker and brighter, thin low end
    for k in range(1, 4):
        build("rsl_chime_fire_%d" % k, [(PULSE % k, 1.22, 1.0, "highpass=f=350")])
    # Pizzicato: small rail - railgun crack pitched up over a pulse-laser zap
    build("rsl_pizzicato_fire", [(RAIL, 1.30, 0.9, ""), (PULSE % 2, 1.10, 0.45, "")], RING)
    # Shard Caster: mining blaster bite + a high rail snap
    build("rsl_shard_fire", [(MINING, 1.15, 0.8, ""), (RAIL, 1.45, 0.5, "highpass=f=500")])
    # Crystal Flechette: flak punch + rail crack
    build("rsl_flechette_fire", [(FLAK, 1.15, 0.7, ""), (RAIL, 1.15, 0.7, "")], RING)
    # Lattice Lance: railgun body + an ion-cannon energy tail
    build("rsl_lance_fire", [(RAIL, 0.95, 1.0, ""), (ION, 1.10, 0.45, "")], RING)
    # Arpeggio: pulse laser notes on a rail crack
    for k in range(1, 4):
        build("rsl_arpeggio_fire_%d" % k, [(PULSE % (k + 2), 0.92, 0.8, ""), (RAIL, 1.20, 0.45, "")])
    # Sostenuto Rail: heavy, rapid - low railgun + kinetic blaster thump
    build("rsl_sostenuto_fire", [(RAIL, 0.80, 0.9, ""), (KBLAST, 0.90, 0.5, "")], "lowpass=f=9000")
    # Harmonic Driver charge: the tachyon lance wind-up it always used, a little brighter
    build("rsl_charge", [(TACHYON, 1.06, 0.8, "")])
    # Harmonic Driver: gauss cannon + heavy blaster energy
    build("rsl_driver_fire", [(GAUSS, 0.95, 1.0, ""), (HBLAST, 1.05, 0.45, "")], RING)
    # Spinal driver: deeper gauss + heavy blaster + a long slap-back
    build("rsl_spinal_fire", [(GAUSS, 0.80, 1.0, ""), (HBLAST, 0.85, 0.55, "")], "aecho=0.8:0.6:23|41:0.3|0.2")
    # Sforzando: the railgun it used, sharpened, with a pulse-laser accent
    build("rsl_sforzando_fire", [(RAIL, 1.08, 1.0, ""), (PULSE % 1, 1.25, 0.35, "highpass=f=600")], RING)
    # Cantus flak, Tuning Spike, Resonance Bloom: their vanilla bases, retuned
    build("rsl_flak_fire", [(FLAK, 1.10, 1.0, "")])
    build("rsl_spike_fire", [(PILUM, 1.15, 1.0, "")])
    build("rsl_bloom_fire", [(REAPER, 0.90, 1.0, "")])


if __name__ == "__main__":
    main()
