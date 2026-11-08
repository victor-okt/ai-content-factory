"""Puppet 2D Kitsune: setiap bagian tubuh punya titik putar dan bergerak sendiri.

Bukan pan/zoom gambar utuh: tiap bagian (kepala, telinga, mata, mulut, lengan,
kaki, ekor, syal, lentera) ditransformasi terpisah per frame lalu disusun.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = Path(__file__).resolve().parent
PARTS = HERE / "assets" / "kitsune_chibi" / "parts"


def load(name, flip=False):
    im = Image.open(PARTS / f"{name}.png").convert("RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


# ---------------------------------------------------------------- matriks 2D
def M_translate(x, y):
    return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], float)


def M_rotate(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def M_scale(sx, sy=None):
    sy = sx if sy is None else sy
    return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], float)


def draw_part(canvas, img, world):
    """Tempel `img` ke `canvas` memakai matriks `world` (koordinat gambar -> kanvas)."""
    w, h = img.size
    corners = np.array([[0, 0, 1], [w, 0, 1], [0, h, 1], [w, h, 1]], float).T
    pts = world @ corners
    x0, y0 = np.floor(pts[0].min()) - 2, np.floor(pts[1].min()) - 2
    x1, y1 = np.ceil(pts[0].max()) + 2, np.ceil(pts[1].max()) + 2
    W, H = canvas.size
    x0, y0, x1, y1 = int(max(0, x0)), int(max(0, y0)), int(min(W, x1)), int(min(H, y1))
    if x1 <= x0 or y1 <= y0:
        return
    inv = np.linalg.inv(M_translate(-x0, -y0) @ world)
    data = (inv[0, 0], inv[0, 1], inv[0, 2], inv[1, 0], inv[1, 1], inv[1, 2])
    # premultiplied alpha agar tepi tidak bergaris gelap
    region = img.convert("RGBa").transform((x1 - x0, y1 - y0), Image.AFFINE, data,
                                           resample=Image.BICUBIC).convert("RGBA")
    canvas.alpha_composite(region, (x0, y0))


def wave_warp(img, t, amp, freq, wavelength, anchor="right", axis_pow=1.6):
    """Bengkokkan gambar seperti kain/ekor: ujung bebas bergoyang, pangkal diam."""
    a = np.array(img.convert("RGBa"), float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    if anchor == "right":
        free = (1 - xx / (w - 1)) ** axis_pow
    else:
        free = (xx / (w - 1)) ** axis_pow
    dy = amp * free * np.sin(2 * math.pi * (freq * t) + xx / wavelength)
    out = np.empty_like(a)
    for c in range(4):
        out[..., c] = nd.map_coordinates(a[..., c], [yy - dy, xx], order=1, mode="constant", cval=0)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBa").convert("RGBA")


# ---------------------------------------------------------------- rig Kitsune
class Kitsune:
    """Titik putar (pivot) dan titik tempel (attach) dalam koordinat gambar potongan."""

    def __init__(self, tint=None):
        self.tint = tint
        P = {}
        for n in ["head", "body", "arm_l", "arm_r", "leg_l", "leg_r", "tail", "lantern", "katana",
                  "hat", "ear_l", "ear_r", "eye_open_l", "eye_open_r", "eye_closed_l", "eye_closed_r",
                  "eye_happy_l", "eye_happy_r", "mouth_line", "mouth_small", "mouth_wide", "mouth_o"]:
            P[n] = load(n)
        P["scarf"] = load("scarf", flip=True)  # ujung syal berkibar ke kiri seperti desain master
        if tint is not None:
            P = {k: self._tinted(v, tint) for k, v in P.items()}
        self.P = P

    @staticmethod
    def _tinted(im, rgb):
        a = np.array(im)
        a[..., :3] = rgb
        return Image.fromarray(a, "RGBA")

    def pose_default(self):
        return dict(x=610, y=1100, s=1.65, body_rot=0, bob=0, head_rot=0, head_dx=0,
                    ear_l=0, ear_r=0, arm_l=0, arm_r=0, leg_l=0, leg_r=0, leg_lift_l=0, leg_lift_r=0,
                    tail=0, scarf_t=0, scarf_amp=10, tail_wave_t=0, lantern_swing=0,
                    eyes="open", eye_dx=0, mouth="line", hat_rot=0)

    def render(self, canvas, q, t):
        P = self.P
        # akar: badan (titik putar di pinggang bawah)
        root = (M_translate(q["x"], q["y"] + q["bob"]) @ M_scale(q["s"]) @ M_rotate(q["body_rot"])
                @ M_translate(-153, -220))
        body = root

        def child(parent, attach, rot, pivot, extra=None):
            m = parent @ M_translate(*attach) @ M_rotate(rot) @ M_translate(-pivot[0], -pivot[1])
            return m if extra is None else m @ extra

        # --- lapisan belakang
        tail_img = wave_warp(P["tail"], q["tail_wave_t"], amp=6, freq=1.0, wavelength=40, anchor="right")
        draw_part(canvas, tail_img, child(body, (70, 205), q["tail"], (232, 175)))
        draw_part(canvas, P["katana"], child(body, (255, 150), 4, (55, 120)))
        leg_l = child(body, (112, 228 - q["leg_lift_l"]), q["leg_l"], (45, 12))
        leg_r = child(body, (196, 228 - q["leg_lift_r"]), q["leg_r"], (45, 12))
        draw_part(canvas, P["leg_l"], leg_l)
        draw_part(canvas, P["leg_r"], leg_r)

        # --- badan dan lengan
        draw_part(canvas, P["body"], body)
        arm_l = child(body, (58, 92), q["arm_l"], (60, 18))
        arm_r = child(body, (248, 92), q["arm_r"], (50, 18))
        draw_part(canvas, P["arm_l"], arm_l)

        # lentera tergantung tegak dari tangan kanan (melawan putaran lengan + ayunan)
        arm_world = q["body_rot"] + q["arm_r"]
        hand = arm_r @ np.array([62, 140, 1.0])
        lantern = (M_translate(hand[0], hand[1]) @ M_scale(q["s"]) @ M_rotate(q["lantern_swing"])
                   @ M_translate(-65, -6))
        draw_part(canvas, P["lantern"], lantern)
        draw_part(canvas, P["arm_r"], arm_r)

        # --- syal di leher (ujung berkibar)
        scarf_img = wave_warp(P["scarf"], q["scarf_t"], amp=q["scarf_amp"], freq=1.3, wavelength=55, anchor="right")
        draw_part(canvas, scarf_img, child(body, (175, 22), 0, (352, 62)))

        # --- kepala dan anak-anaknya
        head = child(body, (153, 24), q["head_rot"], (165, 205), M_translate(165, 205) @ M_scale(1.1) @ M_translate(-165 + q["head_dx"], -205))
        draw_part(canvas, P["ear_l"], child(head, (82, 42), q["ear_l"], (72, 150), M_translate(72,150) @ M_scale(1.1) @ M_translate(-72,-150)))
        draw_part(canvas, P["ear_r"], child(head, (248, 42), q["ear_r"], (38, 150), M_translate(38,150) @ M_scale(1.1) @ M_translate(-38,-150)))
        draw_part(canvas, P["head"], head)
        e = q["eyes"]
        dx = q["eye_dx"]
        for side, ex in (("l", 112), ("r", 218)):
            eye = P[f"eye_{e}_{side}"]
            draw_part(canvas, eye, child(head, (ex + dx, 128), 0, (eye.size[0] / 2, eye.size[1] / 2)))
        # hidung kecil (tidak ada di lembar potongan, digambar di sini)
        nose = head @ np.array([165 + dx * 0.6, 156, 1.0])
        d = ImageDraw.Draw(canvas)
        r = 5 * q["s"]
        d.polygon([(nose[0] - r, nose[1] - r * 0.6), (nose[0] + r, nose[1] - r * 0.6), (nose[0], nose[1] + r * 0.6)],
                  fill=(40, 25, 30, 255) if self.tint is None else (*self.tint, 255))
        m = P[f"mouth_{q['mouth']}"]
        draw_part(canvas, m, child(head, (165 + dx * 0.6, 172), 0, (m.size[0] / 2, m.size[1] * 0.25)))
        draw_part(canvas, P["hat"], child(head, (165, 30), q["hat_rot"], (191, 128), M_translate(191,128) @ M_scale(1.08) @ M_translate(-191,-128)))
