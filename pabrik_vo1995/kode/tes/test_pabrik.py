import json, math, os, subprocess, sys, tempfile, unittest
import numpy as np
from PIL import Image

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)
from vo1995 import suara, gerak, episode
from vo1995.rig import Puppet

class TesSuara(unittest.TestCase):
    def test_potong_tiga_kalimat(self):
        sr = suara.SR
        t = np.arange(int(sr * 1.0)) / sr
        nada = 0.3 * np.sin(2 * np.pi * 220 * t)
        diam = np.zeros(int(sr * 0.9))
        x = np.concatenate([diam, nada, diam, nada, diam, nada, diam])
        bagian = suara.potong_jeda(x)
        self.assertEqual(len(bagian), 3)
        for a, b in bagian:
            self.assertAlmostEqual(b - a, 1.0, delta=0.3)

    def test_cek_suara_pelan(self):
        x = 0.005 * np.sin(np.arange(24000) / 10)
        self.assertIn('suara terlalu pelan', suara.cek_suara(x)['masalah'])

    def test_amplop_rentang(self):
        x = np.random.default_rng(1).normal(0, 0.2, 24000)
        v = suara.amplop(x)
        self.assertTrue(len(v) > 20 and v.min() >= 0 and v.max() <= 1)

class TesRig(unittest.TestCase):
    def test_semua_karakter_terbuka(self):
        for n in ('kitsune', 'victor', 'wukong', 'tengu'):
            p = Puppet(os.path.join(AKAR, 'karakter', n))
            self.assertGreater(p.tinggi_netral(), 100)

    def test_sendi_tetap_saat_berputar(self):
        p = Puppet(os.path.join(AKAR, 'karakter', 'kitsune'))
        def titik(pose):
            m = p._matriks(pose)['lengan_kanan']
            px, py = p.data['bagian']['lengan_kanan']['pivot']
            a, b, c, d, e, f = m
            return a * px + b * py + c, d * px + e * py + f
        x0, y0 = titik({})
        x1, y1 = titik({'lengan_kanan': -120})
        self.assertAlmostEqual(x0, x1, places=4)
        self.assertAlmostEqual(y0, y1, places=4)

    def test_gambar_tidak_kosong(self):
        p = Puppet(os.path.join(AKAR, 'karakter', 'victor'))
        k = Image.new('RGBA', (600, 900), (0, 0, 0, 0))
        p.gambar(k, {'_x': 300, '_y': 880, '_tinggi': 700, 'mulut': 0.8, 'mata': 'tutup'})
        self.assertGreater(np.asarray(k)[..., 3].mean(), 10)

class TesSuaraTertukar(unittest.TestCase):
    def test_suara_berat_untuk_kitsune_ditolak(self):
        sr = suara.SR
        t = np.arange(sr) / sr
        berat = 0.3 * np.sign(np.sin(2 * np.pi * 110 * t)) * 0.5
        diam = np.zeros(sr)
        x = np.concatenate([diam, berat, diam])
        m = episode.cek_identitas_suara('kitsune', 'kitsune', x, [berat])
        self.assertTrue(m and 'tertukar' in m[0])

    def test_suara_cocok_lolos(self):
        sr = suara.SR
        t = np.arange(sr) / sr
        tinggi = 0.3 * np.sin(2 * np.pi * 250 * t)
        self.assertEqual(episode.cek_identitas_suara('kitsune', 'kitsune', tinggi, [tinggi]), [])

    def test_semua_karakter_punya_kartu_suara(self):
        for n in ('kitsune', 'victor', 'wukong', 'tengu'):
            self.assertTrue(os.path.exists(os.path.join(AKAR, 'karakter', n, 'suara.json')))

class TesNaskah(unittest.TestCase):
    def test_suara_kurang_dilaporkan(self):
        d = tempfile.mkdtemp()
        sr = suara.SR
        t = np.arange(sr) / sr
        suara.tulis(os.path.join(d, 'k.wav'),
                    np.concatenate([np.zeros(sr), 0.3 * np.sin(2 * np.pi * 200 * t), np.zeros(sr)]))
        ep = {'pemain': {'kitsune': {}}, 'suara': {'kitsune': 'k.wav'},
              'adegan': [{'siapa': 'kitsune', 'teks': 'satu'}, {'siapa': 'kitsune', 'teks': 'dua'}]}
        with self.assertRaises(episode.MasalahNaskah):
            episode.susun_jadwal(ep, d)

    def test_render_singkat(self):
        d = tempfile.mkdtemp()
        naskah = os.path.join(d, 'ep.json')
        with open(naskah, 'w') as f:
            json.dump({'pemain': {'kitsune': {'x': 540, 'y': 1500}, 'wukong': {'x': 800, 'y': 1500}},
                       'judul': 'Uji', 'depan': [{'file': 'properti/meja_kedai.png'}],
                       'adegan': [{'siapa': 'kitsune', 'teks': 'Halo semua!', 'durasi': 0.8, 'aksi': 'lambai',
                                   'ekspresi': 'kaget', 'kamera': 'dekat',
                                   'efek': [{'jenis': 'kilau', 'siapa': 'kitsune'}]}],
                       'ajakan': {'durasi': 0.5, 'pertanyaan': 'Tes?'}}, f)
        out = os.path.join(d, 'v.mp4')
        hasil = episode.render(naskah, out)
        self.assertGreater(hasil['frame'], 10)
        self.assertTrue(os.path.getsize(out) > 10000)
        info = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                               'stream=width,height,r_frame_rate', '-of', 'csv=p=0', out],
                              capture_output=True, text=True).stdout.strip()
        self.assertEqual(info, '1080,1920,24/1')

if __name__ == '__main__':
    unittest.main()
