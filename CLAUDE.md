# Aturan proyek AI Kantor + VO1995 (untuk setiap sesi Claude)

## Pemilik
Victor, bukan orang IT. Lapor dalam bahasa Indonesia sederhana, tanpa istilah teknis.
Setiap laporan ditutup dengan "Langkah Anda sekarang" (nomor 1, 2, 3) atau "Tidak ada, saya lanjut sendiri."
Ambil keputusan teknis kecil sendiri. Jangan klaim selesai tanpa tes yang dijalankan, commit, atau MP4 yang bisa ditonton.

## Pembagian kerja
- Claude: semua kode, tes, GitHub, render video. Kerja di cabang `claude/...` lalu buat PR; jangan push langsung ke `main`.
- ChatGPT: hanya membuat gambar/aset dan draft naskah. Tidak menyentuh repo.
- Victor: persetujuan, suara ElevenLabs (manual), menilai video.

## Batasan keras
- Tidak ada biaya: tanpa API berbayar, VPS, atau kredit tambahan tanpa izin tertulis Victor.
- Tidak ada publikasi otomatis.
- Tidak ada API key/password di repo.
- Identitas karakter tidak boleh berubah (Kitsune: rubah putih, tanda merah wajah & ujung telinga,
  topi jerami + lonceng emas, kimono indigo motif ombak, syal merah, ekor putih pusaran merah, lentera api, katana).

## Standar video VO1995
9:16, 20-40 detik, >= 24 fps. Cerita dulu: hook 0-3 detik, konflik, twist, ending berkesan.
Bagian tubuh harus bergerak sendiri-sendiri. DITOLAK: pan/zoom/goyang gambar utuh, slideshow, motion comic.
Subtitle kontras tinggi, maksimal 2 baris, di zona aman (bukan 15% terbawah layar).

## Tes (jalankan sebelum dan sesudah mengubah apa pun)
```
python -m unittest discover -s tests -v
python -m unittest discover -s office/runtime -p "test_*.py" -v
python -m unittest -v motion-video/stories/test_story_bank.py
node --test motion-video/character-engine/*.test.mjs
cd motion-video/puppet && python -m unittest -v test_puppet
```
Jangan pernah membuat file bernama `queue.py` (menimpa modul bawaan Python). Worker antrean ada di `office/runtime/jobqueue.py`.

## Peta
- `motion-video/puppet/` puppet Kitsune (Python + PIL), lihat README di sana.
- `motion-video/character-engine/` mesin pose/rig SVG lama (Node).
- `office/runtime/` worker antrean SQLite untuk Windows.
- `factory/` pipeline draft agent 2-6 — masih TEMPLATE, bukan AI.
- Agent: Nox (riset), Kiro (naskah), Miko (karakter/storyboard), Riku (animasi/audio/render), Senn (caption), Zek (QC/biaya). ID teknis lama jangan diubah tanpa audit.
