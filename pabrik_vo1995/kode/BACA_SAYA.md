# Pabrik VO1995 — kode baru (9 November 2026)

Kode ini dibangun ulang dari nol karena cadangan lama hilang bersama akun GitHub.

## Isi folder
- `vo1995/` — mesin pabrik:
  - `rig.py`: merakit karakter dari potongan tubuh, tiap bagian bergerak di sendinya sendiri; kedip, mata senang, mulut bicara.
  - `gerak.py`: daftar aksi untuk naskah: diam, bicara, lambai, tunjuk, kaget, loncat, sedih, tertawa, angguk, geleng, jalan, pikir, semangat.
  - `suara.py`: memotong file suara per kalimat (berdasarkan jeda), mengukur keras-pelan untuk gerak mulut, dan cek mutu suara.
  - `episode.py`: mengubah naskah (file .json) menjadi video MP4 9:16, 24 fps, dengan subtitle dan tanda VO1995.
  - `potong.py`: memotong lembar aset (latar hijau atau transparan) jadi bagian-bagian.
- `karakter/` — Kitsune, Victor, Wukong, Tengu: potongan tubuh + titik sendi, folder `ekspresi/` (8 wajah), dan `suara.json` (kartu suara: nama suara Gemini + rentang nada; suara yang tertukar ditolak otomatis).
- `karakter/_tertahan/` — ekspresi Tengu berwajah hitam (beda dari desain disetujui), belum dipakai.
- `efek/` — efek kartun 4 tahap: asap, debu, ledak, cepat, kilau, air, api, kilap, tinta, ombak.
- `properti/` — meja kedai (lapisan depan, menyembunyikan kaki), dango, teko, ramen, onigiri, payung.
- `contoh/` — naskah episode Dango (`episode_dango.json`) + naskah rekaman suara, contoh lama, latar.
- `tes/` — 11 tes otomatis.

## Cara kerja harian
Victor cukup menaruh suara/gambar baru di folder 1_INBOX lalu bilang "proses" ke Claude.
Claude yang menjalankan pabrik, memeriksa hasil, dan menaruh video di 5_VIDEO_JADI.

## Satu file suara per karakter
Rekam semua kalimat satu karakter dalam satu file, urut sesuai naskah, jeda ±1,5 detik antar kalimat.
Pabrik memotong otomatis dan mencocokkan ke kalimat. Kalau jumlah kalimat tidak cocok, pabrik berhenti dan melapor.

## Untuk teknisi (opsional)
Butuh Python 3.10+, paket: pillow numpy scipy opencv-python, dan ffmpeg.
  python jalankan.py video contoh/episode_contoh.json hasil.mp4
  python jalankan.py cek-suara suara.wav
  python -m unittest discover -s tes -v
