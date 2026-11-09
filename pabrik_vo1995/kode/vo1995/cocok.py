"""Cari letak setiap potongan tubuh pada gambar karakter utuh (template matching)."""
import cv2
import numpy as np
from PIL import Image

def _arr(im):
    return np.asarray(im.convert('RGBA')).astype(np.float32)

def cari(utuh, bagian, skala=(0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15)):
    """Kembalikan (x, y, s, skor) posisi kiri-atas bagian (diskalakan s) di gambar utuh."""
    U = _arr(utuh)
    Urgb = np.ascontiguousarray(U[..., :3])
    terbaik = None
    for s in skala:
        b = bagian.resize((max(4, int(bagian.width * s)), max(4, int(bagian.height * s))), Image.LANCZOS)
        B = _arr(b)
        if B.shape[0] >= U.shape[0] or B.shape[1] >= U.shape[1]:
            continue
        mask = (B[..., 3] > 200).astype(np.float32)
        # kikis tepi supaya garis luar yang beda sedikit tidak mengganggu
        mask = cv2.erode(mask, np.ones((5, 5), np.uint8))
        if mask.sum() < 50:
            continue
        m3 = np.ascontiguousarray(np.repeat(mask[..., None], 3, 2))
        r = cv2.matchTemplate(Urgb, np.ascontiguousarray(B[..., :3]), cv2.TM_SQDIFF, mask=m3)
        r = r / (mask.sum() * 3)
        r[~np.isfinite(r)] = 1e9
        _, _, loc, _ = cv2.minMaxLoc(r)
        skor = float(r[loc[1], loc[0]])
        if terbaik is None or skor < terbaik[3]:
            terbaik = (loc[0], loc[1], s, skor)
    return terbaik
