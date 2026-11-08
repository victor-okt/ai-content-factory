"""Video uji 5 detik: puppet Kitsune dengan bagian tubuh yang bergerak sendiri-sendiri.

Kamera diam. Tidak ada pan/zoom. Yang bergerak adalah bagian tubuh.
Jalankan: python anim_tes5s.py OUTPUT.mp4
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from puppet import Kitsune  # noqa: E402

W, H, FPS, DUR = 1080, 1920, 24, 5.0
CREAM, INDIGO, RED = (241, 231, 211), (38, 52, 92), (196, 52, 46)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def seg(t, a, b):
    return ease((t - a) / (b - a))


def background():
    bg = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(bg)
    d.ellipse((690, 230, 960, 500), fill=(214, 86, 64, 255))           # matahari merah
    for i, y in enumerate(range(1300, 1920, 22)):                      # tanah
        c = tuple(int(v * (1 - 0.012 * i)) for v in (226, 211, 182))
        d.rectangle((0, y, W, y + 22), fill=c + (255,))
    for row, y in enumerate((1560, 1680, 1800)):                       # motif ombak seigaiha sederhana
        for x in range(-60 + (row % 2) * 60, W + 120, 120):
            for r, col in ((58, INDIGO), (44, CREAM), (32, INDIGO), (20, CREAM)):
                d.pieslice((x - r, y - r, x + r, y + r), 180, 360, fill=col + (255,))
    for cx, cy in ((210, 330), (330, 300)):                            # awan
        d.ellipse((cx - 80, cy - 26, cx + 80, cy + 26), fill=(250, 245, 235, 255), outline=INDIGO + (255,), width=4)
    d.line((0, 1300, W, 1300), fill=INDIGO + (255,), width=5)
    return bg


def pose_at(k, t):
    q = k.pose_default()
    q.update(scarf_t=t, tail_wave_t=t)
    breathe = math.sin(2 * math.pi * 0.9 * t)
    q["bob"] = 4 * breathe
    q["tail"] = 6 * math.sin(2 * math.pi * 0.8 * t)
    q["lantern_swing"] = 5 * math.sin(2 * math.pi * 0.7 * t + 0.6)
    q["head_rot"] = 1.5 * math.sin(2 * math.pi * 0.45 * t)

    # 0.0-2.0 s: berjalan masuk dari kiri (karakter yang bergerak, kamera diam)
    walk = 1 - seg(t, 1.7, 2.1)
    q["x"] = 590 + 90 * ease(t / 2.0)
    ph = 2 * math.pi * 1.6 * t
    q["leg_l"] = 16 * math.sin(ph) * walk
    q["leg_r"] = -16 * math.sin(ph) * walk
    q["leg_lift_l"] = 14 * max(0, math.sin(ph)) * walk
    q["leg_lift_r"] = 14 * max(0, -math.sin(ph)) * walk
    q["arm_l"] = -14 * math.sin(ph) * walk
    q["arm_r"] = 10 * math.sin(ph) * walk
    q["bob"] += -10 * abs(math.sin(ph)) * walk
    q["lantern_swing"] += -14 * math.sin(ph - 0.8) * walk

    # 2.0-2.7 s: berhenti, kaget, menoleh ke atas kanan
    sur = seg(t, 2.0, 2.2) * (1 - seg(t, 2.6, 2.8))
    q["head_rot"] += -9 * sur
    q["eye_dx"] = 9 * sur
    q["ear_l"] = -14 * sur
    q["ear_r"] = 14 * sur
    q["body_rot"] = -3 * sur
    if 2.05 <= t < 2.7:
        q["mouth"] = "o"

    # 2.7-3.7 s: berbicara + tangan kiri memberi isyarat
    if 2.7 <= t < 3.7:
        seq = ["small", "wide", "small", "line", "wide", "o", "small", "line"]
        q["mouth"] = seq[int((t - 2.7) * 8) % len(seq)]
        talk = seg(t, 2.7, 2.9) * (1 - seg(t, 3.5, 3.7))
        q["arm_l"] = 45 * talk + 10 * math.sin(2 * math.pi * 2.0 * t) * talk
        q["head_rot"] += 4 * math.sin(2 * math.pi * 2.2 * t) * talk

    # 3.7-5.0 s: senang, melompat kecil, ekor dikibas cepat
    hap = seg(t, 3.7, 3.85)
    if t >= 3.7:
        q["eyes"] = "happy"
        q["mouth"] = "wide" if t < 4.7 else "line"
        q["tail"] = 6 * math.sin(2 * math.pi * 0.8 * t) + 14 * math.sin(2 * math.pi * 3.0 * t) * hap
        q["arm_l"] = 75 * hap * (1 - seg(t, 4.6, 4.9))
        q["arm_r"] = -35 * hap * (1 - seg(t, 4.6, 4.9))
        q["ear_l"] = -8 * math.sin(2 * math.pi * 3 * t) * hap
        q["ear_r"] = 8 * math.sin(2 * math.pi * 3 * t + 1) * hap
    jump = 0.0
    if 4.0 <= t < 4.5:
        u = (t - 4.0) / 0.5
        jump = 4 * u * (1 - u)                      # parabola 0 -> 1 -> 0
        q["bob"] -= 70 * jump
        q["leg_lift_l"] = q["leg_lift_r"] = 22 * jump
        q["leg_l"], q["leg_r"] = -12 * jump, 12 * jump
        q["scarf_amp"] = 10 + 14 * jump
    if 4.5 <= t < 4.62:                              # mendarat: sedikit menekuk
        q["bob"] += 10

    # kedip di 0.9 s dan 4.85 s (bukan saat mata senang)
    if any(b <= t < b + 0.12 for b in (0.9, 4.85)) and q["eyes"] == "open":
        q["eyes"] = "closed"
    return q, jump


def main(out):
    k = Kitsune()
    bg = background()
    n = int(DUR * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    log = []
    for i in range(n):
        t = i / FPS
        q, jump = pose_at(k, t)
        frame = bg.copy()
        # bayangan di tanah mengecil saat melompat
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        r = 150 * (1 - 0.35 * jump)
        ImageDraw.Draw(sh).ellipse((q["x"] - r, 1352 - 18, q["x"] + r, 1352 + 18), fill=(40, 30, 40, 90))
        frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
        k.render(frame, q, t)
        proc.stdin.write(frame.convert("RGB").tobytes())
        log.append({k2: q[k2] for k2 in ("head_rot", "ear_l", "ear_r", "arm_l", "arm_r", "leg_l", "leg_r",
                                         "tail", "lantern_swing", "eyes", "mouth", "x", "bob")})
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg gagal")
    Path(out).with_suffix(".pose.json").write_text(json.dumps(log))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tes.mp4")
