# Puppet Kitsune (2D, bagian tubuh terpisah)

Animasi karakter sungguhan: kepala, telinga, mata, mulut, lengan, kaki, ekor, syal, dan lentera
masing-masing punya titik putar dan bergerak sendiri. Kamera diam. Bukan pan/zoom gambar utuh.

## Status (8 Nov 2026)
- Sudah jalan: video uji 5 detik, 1080x1920, 24 fps, 7+ bagian bergerak terpisah, tanpa suara.
- Kekurangan yang diketahui: topi terlihat ditempel di atas kepala (kepala polos tanpa bulu yang
  masuk ke topi). Menunggu aset kepala berlapis dari ChatGPT (topi belakang / kepala / topi depan
  di kanvas yang sama). Hidung digambar oleh kode karena tidak ada di lembar potongan.
- Belum ada: suara, sinkron bibir ke audio, subtitle, cerita penuh.

## File
- `puppet.py` — rig: hierarki badan > kepala > telinga/mata/mulut/topi; lengan, kaki, ekor,
  syal (dibengkokkan seperti kain), lentera (selalu tergantung tegak dan berayun).
  `Kitsune(tint=(r,g,b))` membuat versi siluet gelap untuk cerita "Bayangan yang Ingin Libur".
- `anim_tes5s.py` — contoh animasi 5 detik: jalan, kaget, bicara, lompat senang.
- `assets/kitsune_chibi/` — gambar dari ChatGPT (`Kitsune_chibi_utuh.png`, `Kitsune_chibi_potongan.png`)
  dan `parts/` hasil potongan otomatis.
- `test_puppet.py` — 9 tes: aset transparan, kedip hanya mengubah mata, kaki bergerak tanpa kepala, dst.

## Menjalankan
```
pip install pillow numpy scipy        # ffmpeg juga dibutuhkan untuk membuat MP4
cd motion-video/puppet
python -m unittest -v test_puppet
python anim_tes5s.py tes.mp4          # sekitar 30 detik
```
