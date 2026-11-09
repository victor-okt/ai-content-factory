"""Pintu masuk pabrik VO1995.

  python jalankan.py video  <naskah.json> <hasil.mp4>   buat video dari naskah
  python jalankan.py cek-suara <file suara>              periksa suara (wajib sebelum dipakai)
  python jalankan.py potong <lembar.png> <folder>        potong lembar aset jadi bagian-bagian
"""
import json, sys
from vo1995 import episode, suara, potong

def main(a):
    if len(a) >= 3 and a[0] == 'video':
        print(episode.render(a[1], a[2]))
    elif len(a) >= 2 and a[0] == 'cek-suara':
        x = suara.baca(a[1])
        hasil = suara.cek_suara(x)
        hasil['jumlah_kalimat'] = len(suara.potong_jeda(x))
        hasil['status'] = 'LULUS' if not hasil['masalah'] else 'PERLU PERBAIKAN'
        print(json.dumps(hasil, ensure_ascii=False, indent=1))
    elif len(a) >= 3 and a[0] == 'potong':
        for h in potong.potong(a[1], a[2]):
            print(h)
    else:
        print(__doc__)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
