"""Tes puppet Kitsune: bukti bagian tubuh bergerak sendiri-sendiri (bukan gambar utuh digoyang).

Jalankan dari folder ini: python -m unittest -v test_puppet
Butuh: pillow, numpy, scipy (tanpa ffmpeg).
"""
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import anim_tes5s as anim
from puppet import PARTS, Kitsune

W, H = 1080, 1920
REQUIRED = ["head", "body", "arm_l", "arm_r", "leg_l", "leg_r", "tail", "lantern", "katana", "hat",
            "ear_l", "ear_r", "scarf", "eye_open_l", "eye_open_r", "eye_closed_l", "eye_closed_r",
            "eye_happy_l", "eye_happy_r", "mouth_line", "mouth_small", "mouth_wide", "mouth_o"]


def render(k, **changes):
    q = k.pose_default()
    q.update(changes)
    c = Image.new("RGBA", (W, H), (241, 231, 211, 255))
    k.render(c, q, 0.0)
    return np.asarray(c.convert("RGB")).astype(int)


def changed_box(a, b):
    """Kotak area piksel yang berubah antara dua frame, atau None jika tidak ada."""
    diff = np.abs(a - b).sum(axis=2) > 30
    if not diff.any():
        return None
    ys, xs = np.where(diff)
    return xs.min(), ys.min(), xs.max(), ys.max()


class Assets(unittest.TestCase):
    def test_all_parts_exist_and_are_transparent(self):
        for name in REQUIRED:
            path = Path(PARTS) / f"{name}.png"
            self.assertTrue(path.exists(), name)
            alpha = np.asarray(Image.open(path).convert("RGBA"))[..., 3]
            self.assertGreater((alpha == 0).mean(), 0.05, f"{name} tidak punya area transparan")
            self.assertGreater((alpha > 200).mean(), 0.1, f"{name} hampir kosong")


class IndependentMotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = Kitsune()
        cls.base = render(cls.k)
        q = cls.k.pose_default()
        cls.foot_y = q["y"]
        cls.head_y = q["y"] - (220 - 24 - 15) * q["s"]   # leher + dagu yang menumpuk di badan

    def assertOnly(self, box, region, msg):
        self.assertIsNotNone(box, msg + ": tidak ada yang bergerak")
        x0, y0, x1, y1 = box
        rx0, ry0, rx1, ry1 = region
        self.assertTrue(x0 >= rx0 and y0 >= ry0 and x1 <= rx1 and y1 <= ry1,
                        f"{msg}: area berubah {box} keluar dari {region}")

    def test_blink_changes_only_the_eyes(self):
        box = changed_box(self.base, render(self.k, eyes="closed"))
        self.assertOnly(box, (0, 0, W, self.head_y), "kedip")
        self.assertLess((box[2] - box[0]) * (box[3] - box[1]), 0.02 * W * H, "kedip mengubah area terlalu luas")

    def test_mouth_changes_only_the_mouth(self):
        box = changed_box(self.base, render(self.k, mouth="wide"))
        self.assertOnly(box, (0, 0, W, self.head_y), "mulut")
        self.assertLess((box[2] - box[0]) * (box[3] - box[1]), 0.01 * W * H, "mulut mengubah area terlalu luas")

    def test_ear_moves_without_body(self):
        box = changed_box(self.base, render(self.k, ear_l=-20))
        self.assertOnly(box, (0, 0, W, self.head_y), "telinga")

    def test_leg_moves_without_head(self):
        box = changed_box(self.base, render(self.k, leg_l=25))
        self.assertOnly(box, (0, self.head_y, W, H), "kaki")

    def test_arm_moves_without_head(self):
        box = changed_box(self.base, render(self.k, arm_l=60))
        self.assertOnly(box, (0, self.head_y, W, H), "lengan")

    def test_head_turn_does_not_move_feet(self):
        a = render(self.k, head_rot=-10)
        feet = slice(int(self.foot_y - 40), int(self.foot_y + 120))
        self.assertIsNone(changed_box(self.base[feet], a[feet]), "kaki ikut bergerak saat kepala menoleh")


class AnimationScript(unittest.TestCase):
    def test_five_second_test_uses_many_independent_parts(self):
        k = Kitsune()
        poses = [anim.pose_at(k, i / anim.FPS)[0] for i in range(int(anim.DUR * anim.FPS))]
        self.assertEqual(len(poses), 120)
        for key in ("head_rot", "ear_l", "ear_r", "arm_l", "arm_r", "leg_l", "leg_r", "tail", "lantern_swing"):
            span = max(p[key] for p in poses) - min(p[key] for p in poses)
            self.assertGreater(span, 5, f"{key} hampir tidak bergerak")
        self.assertEqual({p["eyes"] for p in poses}, {"open", "closed", "happy"})
        self.assertGreaterEqual(len({p["mouth"] for p in poses}), 4)

    def test_character_stays_inside_frame(self):
        k = Kitsune()
        for i in range(0, 120, 12):
            q, _ = anim.pose_at(k, i / anim.FPS)
            c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            k.render(c, q, i / anim.FPS)
            alpha = np.asarray(c)[..., 3]
            self.assertEqual(int(alpha[:, :2].max()), 0, f"frame {i}: terpotong di tepi kiri")
            self.assertEqual(int(alpha[:2, :].max()), 0, f"frame {i}: terpotong di tepi atas")


if __name__ == "__main__":
    unittest.main()
