"""Perpustakaan gerak: setiap aksi = fungsi waktu -> perubahan pose.

Nama aksi untuk naskah: diam, bicara, lambai, tunjuk, kaget, loncat, sedih, tertawa,
angguk, geleng, jalan, pikir, semangat.
"""
import math

def _halus(t, durasi=0.35):
    """0 -> 1 halus di awal aksi (supaya tidak patah)."""
    if t <= 0:
        return 0.0
    if t >= durasi:
        return 1.0
    u = t / durasi
    return u * u * (3 - 2 * u)

def napas(t, seed=0):
    """Gerak diam: bernapas, kepala dan ekor bergoyang pelan."""
    s = math.sin(t * 2.1 + seed)
    return {
        '_dy': s * 4,
        'badan': math.sin(t * 1.3 + seed) * 1.2,
        'kepala': math.sin(t * 1.1 + seed * 2) * 2.5,
        'lengan_kiri': 3 + math.sin(t * 1.7 + seed) * 3,
        'lengan_kanan': -3 - math.sin(t * 1.7 + seed + 1) * 3,
        'ekor': math.sin(t * 2.4 + seed) * 8,
        'syal': math.sin(t * 3.0 + seed) * 4,
        'lentera': math.sin(t * 2.0 + seed) * 6,
    }

def aksi(nama, t, durasi, keras=0.0):
    """Perubahan pose untuk aksi pada detik t (0..durasi) dalam satu kalimat."""
    k = _halus(t) * _halus(durasi - t, 0.3)
    p = {}
    if nama == 'bicara':
        p['kepala'] = math.sin(t * 6) * 4 * keras + math.sin(t * 2.3) * 3
        p['lengan_kanan'] = -10 * k + math.sin(t * 3) * 6 * k
    elif nama == 'lambai':
        p['lengan_kanan'] = (-150 + math.sin(t * 12) * 22) * k
        p['kepala'] = 5 * k
    elif nama == 'tunjuk':
        p['lengan_kanan'] = -95 * k
        p['kepala'] = -4 * k
    elif nama == 'kaget':
        loncat = math.sin(min(t, 0.4) / 0.4 * math.pi) if t < 0.4 else 0
        p['_dy'] = -60 * loncat
        p['lengan_kiri'] = 125 * k
        p['lengan_kanan'] = -125 * k
        p['kepala'] = -6 * k
        p['ekor'] = 25 * k
        p['mata'] = 'terbuka'
    elif nama == 'loncat':
        f = (t * 2.2) % 1.0
        p['_dy'] = -110 * math.sin(f * math.pi) * k
        p['lengan_kiri'] = 60 * k
        p['lengan_kanan'] = -60 * k
        p['kaki_kiri'] = 15 * math.sin(f * math.pi) * k
        p['kaki_kanan'] = -15 * math.sin(f * math.pi) * k
    elif nama == 'sedih':
        p['kepala'] = 14 * k
        p['badan'] = 4 * k
        p['lengan_kiri'] = -8 * k
        p['lengan_kanan'] = 8 * k
        p['ekor'] = -20 * k
        p['_dy'] = 10 * k
    elif nama == 'tertawa':
        p['_dy'] = -abs(math.sin(t * 14)) * 12 * k
        p['kepala'] = (-8 + math.sin(t * 14) * 4) * k
        p['badan'] = math.sin(t * 14) * 2 * k
        p['lengan_kiri'] = 30 * k
        p['lengan_kanan'] = -30 * k
        p['mata'] = 'senang'
    elif nama == 'angguk':
        p['kepala'] = abs(math.sin(t * 7)) * 12 * k
    elif nama == 'geleng':
        p['kepala'] = math.sin(t * 9) * 10 * k
    elif nama == 'pikir':
        p['lengan_kanan'] = -120 * k
        p['kepala'] = (10 + math.sin(t * 1.5) * 3) * k
        p['mata'] = 'terbuka'
    elif nama == 'semangat':
        p['lengan_kanan'] = (-160 + math.sin(t * 8) * 10) * k
        p['lengan_kiri'] = 20 * k
        p['_dy'] = -abs(math.sin(t * 6)) * 25 * k
        p['mata'] = 'senang'
    elif nama == 'jalan':
        langkah = math.sin(t * 9)
        p['kaki_kiri'] = langkah * 22
        p['kaki_kanan'] = -langkah * 22
        p['lengan_kiri'] = -langkah * 18
        p['lengan_kanan'] = -langkah * 18
        p['_dy'] = -abs(math.cos(t * 9)) * 14
    return p

def gabung(*pose):
    """Jumlahkan pose (angka dijumlah, teks diambil yang terakhir)."""
    hasil = {}
    for p in pose:
        for k, v in p.items():
            if isinstance(v, (int, float)) and isinstance(hasil.get(k, 0), (int, float)):
                hasil[k] = hasil.get(k, 0) + v
            else:
                hasil[k] = v
    return hasil

def kedip(t, seed=0):
    """True kalau sedang kedip (kira-kira tiap 3 detik, 0,12 detik)."""
    jarak = 2.6 + (seed % 3) * 0.5
    return (t + seed * 0.77) % jarak < 0.12
