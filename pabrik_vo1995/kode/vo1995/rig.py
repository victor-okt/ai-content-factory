"""Rig puppet 2D: bagian tubuh terpisah, tiap bagian berputar di titik sendi sendiri.

Data rig (JSON) per karakter:
  bagian: {nama: {file, pivot:[x,y] (piksel di gambar bagian), induk, tempel:[x,y]
           (piksel di gambar induk), z, skala, sudut}}
Pose: {nama_bagian: sudut_derajat, '_x','_y' (posisi kaki di layar), '_skala',
       '_balik' (hadap kiri), 'mata': terbuka/tutup/senang, 'mulut': 0..1}
"""
import json, math, os
from PIL import Image, ImageDraw, ImageFilter

class Puppet:
    def __init__(self, folder):
        self.folder = folder
        with open(os.path.join(folder, 'rig.json'), encoding='utf-8') as f:
            self.data = json.load(f)
        self.nama = self.data.get('nama', os.path.basename(folder))
        self.img = {}
        for n, b in self.data['bagian'].items():
            im = Image.open(os.path.join(folder, b['file'])).convert('RGBA')
            self.img[n] = im
        self.urut = sorted(self.data['bagian'], key=lambda n: self.data['bagian'][n].get('z', 0))
        self.wajah = self.data.get('wajah')
        self.tint = None
        self._eks = {}

    def daftar_ekspresi(self):
        d = os.path.join(self.folder, 'ekspresi')
        return sorted(f[:-4] for f in os.listdir(d) if f.endswith('.png')) if os.path.isdir(d) else []

    def ekspresi(self, nama):
        """Gambar kepala ekspresi, disesuaikan ukuran & posisi dengan kepala rig."""
        if nama in self._eks:
            return self._eks[nama]
        f = os.path.join(self.folder, 'ekspresi', nama + '.png')
        if not os.path.exists(f) or not self.wajah:
            self._eks[nama] = None
            return None
        kepala = self.img[self.wajah['bagian']]
        e = Image.open(f).convert('RGBA')
        cfg = self.data.get('ekspresi', {})
        bk = kepala.getbbox()
        lebar = (bk[2] - bk[0]) * cfg.get('skala', 1.0)
        s = lebar / e.width
        e = e.resize((max(1, int(e.width * s)), max(1, int(e.height * s))), Image.LANCZOS)
        pad = int(kepala.width * 0.25)
        kanvas = Image.new('RGBA', (kepala.width + 2 * pad, kepala.height + 2 * pad), (0, 0, 0, 0))
        cx = (bk[0] + bk[2]) / 2 + pad + cfg.get('geser', [0, 0])[0]
        bawah = bk[3] + pad + cfg.get('geser', [0, 0])[1]
        kanvas.alpha_composite(e, (int(cx - e.width / 2), int(bawah - e.height)))
        self._eks[nama] = (kanvas, pad)
        return self._eks[nama]

    # ---- matriks 2D sederhana (a,b,c,d,e,f) : x' = a*x + b*y + c ; y' = d*x + e*y + f
    @staticmethod
    def _kali(m, n):
        a, b, c, d, e, f = m; A, B, C, D, E, F = n
        return (a*A + b*D, a*B + b*E, a*C + b*F + c, d*A + e*D, d*B + e*E, d*C + e*F + f)

    @staticmethod
    def _geser(x, y):
        return (1, 0, x, 0, 1, y)

    @staticmethod
    def _putar(deg, s=1.0):
        r = math.radians(deg); co, si = math.cos(r) * s, math.sin(r) * s
        return (co, -si, 0, si, co, 0)

    def _matriks(self, pose):
        """Hitung transformasi dunia tiap bagian."""
        hasil = {}
        def hitung(n):
            if n in hasil:
                return hasil[n]
            b = self.data['bagian'][n]
            px, py = b['pivot']
            sudut = b.get('sudut', 0) + pose.get(n, 0)
            lokal = self._kali(self._putar(sudut, b.get('skala', 1.0) * pose.get('skala_' + n, 1.0)), self._geser(-px, -py))
            induk = b.get('induk')
            if induk:
                tx, ty = b['tempel']
                m = self._kali(hitung(induk), self._kali(self._geser(tx, ty), lokal))
            else:
                s = pose.get('_skala', 1.0)
                if '_tinggi' in pose:
                    s *= pose['_tinggi'] / self.tinggi_netral()
                arah = -1 if pose.get('_balik') else 1
                akar = (arah * s, 0, pose.get('_x', 0), 0, s, pose.get('_y', 0))
                m = self._kali(akar, lokal)
            hasil[n] = m
            return m
        for n in self.data['bagian']:
            hitung(n)
        return hasil

    def _gambar_wajah(self, im, pose):
        """Kedip, mata senang, dan mulut bicara digambar di atas gambar kepala."""
        w = self.wajah
        if not w:
            return im
        mata = pose.get('mata', 'terbuka')
        mulut = pose.get('mulut', 0.0) if 'mulut' in w else 0.0
        if mata == 'terbuka' and mulut < 0.08:
            return im
        im = im.copy()
        lap = Image.new('RGBA', im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lap)
        kulit = tuple(w['kulit']) + (255,)
        garis = tuple(w.get('garis', [40, 20, 20])) + (255,)
        if mata != 'terbuka':
            for (x0, y0, x1, y1) in w['mata']:
                d.ellipse((x0, y0, x1, y1), fill=kulit)
        tebal = max(3, int(w.get('tebal', 5)))
        for (x0, y0, x1, y1) in w['mata']:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            lw = (x1 - x0) * 0.42
            if mata == 'tutup':
                d.arc((cx - lw, cy - lw * 0.5, cx + lw, cy + lw * 0.5), 15, 165, fill=garis, width=tebal)
            elif mata == 'senang':
                d.arc((cx - lw, cy - lw * 0.35, cx + lw, cy + lw * 0.9), 200, 340, fill=garis, width=tebal)
        if mulut >= 0.08 and 'mulut' in w:
            if w.get('tambal_mulut'):
                d.ellipse(tuple(w['tambal_mulut']), fill=kulit)
            mx, my = w['mulut']
            lebar = w.get('lebar_mulut', 24)
            tinggi = 3 + mulut * w.get('tinggi_mulut', 22)
            d.ellipse((mx - lebar / 2 - 3, my - 3, mx + lebar / 2 + 3, my + tinggi + 3), fill=garis)
            d.ellipse((mx - lebar / 2, my, mx + lebar / 2, my + tinggi), fill=(150, 40, 50, 255))
            if tinggi > 9:
                d.ellipse((mx - lebar / 3, my + tinggi * 0.45, mx + lebar / 3, my + tinggi), fill=(235, 120, 130, 255))
        lap = lap.filter(ImageFilter.GaussianBlur(0.6))
        im.alpha_composite(lap)
        return im

    def tinggi_netral(self):
        """Tinggi karakter (piksel) pada pose netral skala 1, dihitung sekali."""
        if not hasattr(self, '_tn'):
            mats = self._matriks({})
            ys = []
            for n, (a, b, c, d, e, f) in mats.items():
                W, H = self.img[n].size
                bb = self.img[n].getbbox() or (0, 0, W, H)
                for x, y in ((bb[0], bb[1]), (bb[2], bb[1]), (bb[0], bb[3]), (bb[2], bb[3])):
                    ys.append(d * x + e * y + f)
            self._tn = max(ys) - min(ys)
        return self._tn

    def gambar(self, kanvas, pose):
        """Gambar puppet pada kanvas (Image RGBA) sesuai pose."""
        mats = self._matriks(pose)
        for n in self.urut:
            if pose.get('_sembunyi_' + n):
                continue
            src = self.img[n]
            a, b, c, d, e, f = mats[n]
            if self.wajah and n == self.wajah.get('bagian'):
                eks = pose.get('ekspresi')
                hasil = self.ekspresi(eks) if eks and eks != 'netral' else None
                if hasil:
                    src, pad = hasil
                    # geser matriks karena kanvas ekspresi diberi bingkai
                    c, f = c - a * pad - b * pad, f - d * pad - e * pad
                else:
                    src = self._gambar_wajah(src, pose)
            # kotak tujuan
            W, H = src.size
            pts = [(a*x + b*y + c, d*x + e*y + f) for x, y in ((0, 0), (W, 0), (0, H), (W, H))]
            x0 = int(math.floor(min(p[0] for p in pts))) - 1
            y0 = int(math.floor(min(p[1] for p in pts))) - 1
            x1 = int(math.ceil(max(p[0] for p in pts))) + 1
            y1 = int(math.ceil(max(p[1] for p in pts))) + 1
            if x1 <= 0 or y1 <= 0 or x0 >= kanvas.width or y0 >= kanvas.height:
                continue
            # invers matriks untuk Image.transform
            det = a * e - b * d
            ia, ib, id_, ie = e / det, -b / det, -d / det, a / det
            # titik tujuan (u,v) relatif kotak -> sumber
            cx, cy = x0 - c, y0 - f
            inv = (ia, ib, ia * cx + ib * cy, id_, ie, id_ * cx + ie * cy)
            potong = src.transform((x1 - x0, y1 - y0), Image.AFFINE, inv, resample=Image.BICUBIC)
            if self.tint:
                potong = warnai(potong, self.tint)
            kanvas.alpha_composite(potong, (max(x0, 0), max(y0, 0)),
                                   (max(0, -x0), max(0, -y0)))
        return kanvas

def warnai(im, warna, kuat=0.85):
    """Warnai bagian (untuk bayangan): campur dengan warna gelap, alpha tetap."""
    r, g, b, a = im.split()
    gelap = Image.new('RGB', im.size, warna)
    campur = Image.blend(Image.merge('RGB', (r, g, b)), gelap, kuat)
    return Image.merge('RGBA', (*campur.split(), a))
