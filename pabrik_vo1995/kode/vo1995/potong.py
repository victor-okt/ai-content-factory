"""Potong lembar aset (latar hijau / transparan) menjadi bagian-bagian terpisah."""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

def buang_hijau(im):
    """Ubah latar hijau (chroma) menjadi transparan, kurangi sisa hijau di tepi."""
    a = np.asarray(im.convert('RGBA')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hijau = (g > 150) & (g - np.maximum(r, b) > 80)
    a[..., 3] = np.where(hijau, 0, a[..., 3])
    # tepi agak hijau: turunkan hijau ke rata-rata merah/biru
    semi = (g - np.maximum(r, b) > 25) & ~hijau
    a[..., 1] = np.where(semi, np.maximum(r, b), g)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')

def latar_transparan(im):
    im = im.convert('RGBA')
    a = np.asarray(im)
    if a[..., 3].min() == 255:  # tidak ada transparansi -> anggap latar hijau
        return buang_hijau(im)
    return im

def potong(path, keluar, min_luas=400, gabung=6):
    im = latar_transparan(Image.open(path))
    a = np.asarray(im)
    mask = a[..., 3] > 40
    # gabungkan potongan yang sangat dekat (garis tipis/lonceng)
    mask_g = ndimage.binary_dilation(mask, iterations=gabung)
    lab, n = ndimage.label(mask_g)
    os.makedirs(keluar, exist_ok=True)
    hasil = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        ys, xs = sl
        sub = (lab[sl] == i) & mask[sl]
        if sub.sum() < min_luas:
            continue
        potongan = a[sl].copy()
        potongan[..., 3] = np.where(sub, potongan[..., 3], 0)
        nama = f'bag_{len(hasil):02d}.png'
        Image.fromarray(potongan).save(os.path.join(keluar, nama))
        hasil.append({'file': nama, 'x': xs.start, 'y': ys.start,
                      'w': xs.stop - xs.start, 'h': ys.stop - ys.start,
                      'luas': int(sub.sum())})
    with open(os.path.join(keluar, 'daftar.json'), 'w') as f:
        json.dump(hasil, f, indent=1)
    return hasil

if __name__ == '__main__':
    for h in potong(sys.argv[1], sys.argv[2]):
        print(h)
