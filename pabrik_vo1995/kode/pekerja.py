"""Pekerja pabrik VO1995 (ditulis ulang 9 Nov 2026).

Alur tiap kali komputer menyala:
  naskah di Drive VO1995/antrean  ->  Zek cek naskah  ->  Riku buat suara (Gemini)
  ->  render video  ->  Zek cek video  ->  video + laporan + caption ke Drive VO1995/3_VIDEO_JADI
Maksimal 2 video sekali nyala. Semua lokasi dihitung dari letak folder ini,
jadi folder pabrik boleh dipindah ke disk mana pun tanpa mengubah kode.

  python pekerja.py          jalankan pabrik
  python pekerja.py --uji    cek kesiapan saja
"""
import datetime
import glob
import json
import os
import shutil
import sys
import traceback

AKAR = os.path.dirname(os.path.abspath(__file__))      # ...\VO1995_PABRIK\kode
PROYEK = os.path.dirname(AKAR)                          # ...\VO1995_PABRIK
sys.path.insert(0, AKAR)
LOG = os.path.join(PROYEK, 'log_pabrik.txt')
MAKS_VIDEO = 2


def log(teks):
    baris = f'[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {teks}'
    print(baris, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(baris + '\n')
    except OSError:
        pass


def cari_drive():
    """Cari folder Google Drive VO1995 (Google Drive untuk desktop)."""
    for huruf in 'GHIJKLMNOPQRSTUVWXYZDEF':
        for sub in ('My Drive', 'Drive Saya'):
            p = f'{huruf}:\\{sub}\\VO1995'
            if os.path.isdir(p):
                return p
    return None


def folder(*bagian):
    p = os.path.join(*bagian)
    os.makedirs(p, exist_ok=True)
    return p


def uji():
    ok = True

    def baris(nama, hasil, catatan=''):
        nonlocal ok
        ok = ok and hasil
        print(f"  {'OK   ' if hasil else 'GAGAL'}  {nama}  {catatan}")

    print('UJI KESIAPAN PABRIK VO1995')
    print(f'  Folder pabrik: {PROYEK}')
    v = sys.version_info
    baris('Python 3.12', (v.major, v.minor) == (3, 12), f'(terpasang {v.major}.{v.minor})')
    try:
        import numpy, PIL  # noqa: F401
        baris('Bahan Python (numpy, pillow)', True)
    except Exception as e:  # noqa: BLE001
        baris('Bahan Python (numpy, pillow)', False, str(e))
    try:
        from vo1995 import FFMPEG
        baris('ffmpeg (pembuat video)', os.path.exists(FFMPEG) or shutil.which(FFMPEG) is not None, FFMPEG)
    except Exception as e:  # noqa: BLE001
        baris('ffmpeg (pembuat video)', False, str(e))
    try:
        from vo1995 import katalog, tts, episode, zek, rig, suara  # noqa: F401
        k = katalog.katalog()
        baris('Mesin pabrik', True, f"({len(k.get('latar', []))} latar, {len(k.get('karakter', {}))} karakter)")
    except Exception as e:  # noqa: BLE001
        baris('Mesin pabrik', False, f'{type(e).__name__}: {e}')
    try:
        from vo1995 import tts
        baris('Kunci Gemini', bool(tts.kunci()))
    except Exception as e:  # noqa: BLE001
        baris('Kunci Gemini', False, str(e))
    d = cari_drive()
    baris('Google Drive VO1995', d is not None, d or 'folder Drive VO1995 tidak ketemu')
    print('  HASIL: ' + ('BERHASIL - pabrik siap' if ok else 'ADA YANG GAGAL - kirim foto layar ini ke Claude'))
    return ok


def tandai_perbaikan(path, alasan, drive):
    nama = os.path.splitext(os.path.basename(path))[0]
    tujuan = folder(os.path.dirname(path), 'perlu_perbaikan')
    with open(os.path.join(os.path.dirname(path), f'{nama}_PERLU_PERBAIKAN.md'), 'w', encoding='utf-8') as f:
        f.write(f'# {nama} perlu perbaikan\n\n' + '\n'.join(f'- {a}' for a in alasan) + '\n')
    shutil.move(path, os.path.join(tujuan, os.path.basename(path)))


def proses_satu(path, drive):
    from vo1995 import katalog, tts, episode, zek
    nama = os.path.splitext(os.path.basename(path))[0]
    log(f'== Episode: {nama}')
    with open(path, encoding='utf-8') as f:
        ep = json.load(f)

    masalah = katalog.periksa_naskah(ep)
    if masalah:
        log('  naskah ditolak Zek: ' + '; '.join(masalah))
        tandai_perbaikan(path, masalah, drive)
        return False

    kerja = folder(PROYEK, 'kerja', nama)
    tts.buat_episode(ep, folder(kerja, 'suara'), log)
    naskah_kerja = os.path.join(kerja, 'episode.json')
    with open(naskah_kerja, 'w', encoding='utf-8') as f:
        json.dump(ep, f, ensure_ascii=False, indent=1)

    keluar = os.path.join(kerja, f'VO1995_{nama}.mp4')
    log('  render video...')
    hasil = episode.render(naskah_kerja, keluar)
    tabel = zek.periksa(hasil)
    laporan = zek.cetak(tabel)
    lulus = all(str(s).startswith('LULUS') for _, s, _ in tabel)

    caption = ep.get('caption', '') + '\n\n' + ' '.join(ep.get('hashtag', []))
    teks_laporan = f'Laporan Zek - {nama}\n\n{laporan}\n\nCAPTION:\n{caption}\n'
    sub = '' if lulus else 'perlu_dicek'
    tujuan = [folder(PROYEK, '5_VIDEO_JADI', sub)]
    if drive:
        tujuan.append(folder(drive, '3_VIDEO_JADI', sub))
    for t in tujuan:
        shutil.copy2(keluar, os.path.join(t, os.path.basename(keluar)))
        with open(os.path.join(t, f'VO1995_{nama}_laporan.txt'), 'w', encoding='utf-8') as f:
            f.write(teks_laporan)

    if lulus:
        shutil.move(path, os.path.join(folder(os.path.dirname(path), 'selesai'), os.path.basename(path)))
        log('  video LULUS, dikirim ke folder video jadi')
    else:
        gagal = [f'{c}: {k}' for c, s, k in tabel if not str(s).startswith('LULUS')]
        log('  video perlu perbaikan: ' + '; '.join(c for c, s, _ in tabel if not str(s).startswith('LULUS')))
        tandai_perbaikan(path, gagal, drive)
    return lulus


def jalankan():
    drive = cari_drive()
    log(f'Pabrik menyala. Folder: {PROYEK}. Drive: {drive or "tidak ketemu"}')
    antrean = []
    for d in filter(None, [drive and os.path.join(drive, 'antrean'), os.path.join(PROYEK, 'antrean')]):
        if os.path.isdir(d):
            antrean += glob.glob(os.path.join(d, 'ep_*.json'))
    antrean.sort(key=os.path.getmtime)
    selesai, gagal = [], []
    for path in antrean[:MAKS_VIDEO]:
        try:
            (selesai if proses_satu(path, drive) else gagal).append(os.path.basename(path))
        except Exception as e:  # noqa: BLE001
            log(f'  GAGAL: {type(e).__name__}: {e}')
            log(traceback.format_exc())
            gagal.append(os.path.basename(path))
            try:
                tandai_perbaikan(path, [f'{type(e).__name__}: {e}'], drive)
            except OSError:
                pass
    sisa = max(0, len(antrean) - MAKS_VIDEO)
    status = {'waktu': f'{datetime.datetime.now():%Y-%m-%d %H:%M}', 'selesai': selesai, 'gagal': gagal, 'sisa_antrean': sisa}
    for t in filter(None, [drive and folder(drive, '3_VIDEO_JADI'), folder(PROYEK, '5_VIDEO_JADI')]):
        with open(os.path.join(t, 'status_pabrik.json'), 'w', encoding='utf-8') as f:
            json.dump(status, f, ensure_ascii=False, indent=1)
    log(f'Pabrik selesai: {len(selesai)} video jadi, sisa antrean {sisa}.')


if __name__ == '__main__':
    if '--uji' in sys.argv:
        sys.exit(0 if uji() else 1)
    jalankan()
