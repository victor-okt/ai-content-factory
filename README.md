# AI Content Factory — Pixel Office 🎮

Kantor AI virtual bergaya pixel. **Agent 1 (Nova / Trend Hunter) sudah memiliki kode riset otomatis; agent lain masih karakter visual, belum agent aktif.**

## Cara membuka Pixel Office

1. Buka **Settings → Pages** di repository ini: https://github.com/victor-okt/ai-content-factory/settings/pages
2. Pada **Build and deployment → Source**, pilih **GitHub Actions**.
3. Jalankan ulang workflow **Publish Pixel Office** di tab Actions jika belum otomatis berhasil.
4. Setelah deploy berhasil, buka: **https://victor-okt.github.io/ai-content-factory/**

Di layar kantor, ketuk Nova (Trend Hunter), lalu pilih **Lihat Laporan**.

## Pekerjaan Nova (Agent 1)

- Mengambil RSS publik Google Trends Indonesia dan liputan Google News.
- Menolak sebagian topik sensitif dan tidak relevan.
- Menyimpan hasil di `office/data/latest.json`, termasuk link sumber, tanggal, konsep, dan skor.
- Mencatat ide yang pernah muncul di `office/data/seen.json` untuk mengurangi duplikasi.
- Jadwal otomatis melalui GitHub Actions sekitar **07.23 WIB** setiap hari. Waktu bisa terlambat.

**Penting:** Ini belum membaca analytics TikTok langsung. Skor hanyalah heuristik, **bukan prediksi views, viral, atau penghasilan.** Foto karakter yang berjalan di kantor adalah animasi.

## Status pengembangan

- ✅ Pixel Office modern dan animasi pekerja
- ✅ Pipeline riset data publik (tanpa AI API berbayar)
- ✅ GitHub Actions test dan penjadwalan
- ✅ Laporan pertama dari sumber publik
- ⏳ Aktivasi GitHub Pages oleh pemilik repository
- ⏳ Peningkatan kualitas filter tren TikTok entertainment
- 🔒 Agent 2–6 belum dibuat

## Pengujian

Python 3.12, tanpa dependensi eksternal:
```sh
python -m unittest discover -s tests -v
python -m trendhunter.daily
python -m http.server 8000 --directory office
```

Hasil web mengikuti data di `office/data/latest.json`. Jika koneksi sumber gagal, status dilaporkan secara jujur.

## Keamanan dan biaya

Tidak ada API key dalam repository. Website dan laporan riset bersifat **publik**. Jangan menaruh password, token, data pelanggan, atau informasi privat di repo. GitHub Pages dan Actions bisa digunakan dalam batas layanan gratis untuk proyek publik.


## Agent 1 quality filter v1.2
- News items must name a specific entertainment subject AND visual motion; tutorials, prompts and promotional tool articles are excluded.
- Google Trends search terms must match entertainment niches. Source links and dates remain attached to each candidate.
- Scores are heuristic creative-fit points, never verified viral probability.
- If collection fails, previous ideas are labeled stale. If no source qualifies, the report can be empty.
- `quality_control` records how many feed items were examined and rejected.
- `handoff` prepares IDs for future Agent 2, but does **not** execute it without approval.


## Riwayat harian Nova

`office/data/history.json` mencatat maksimal 30 tanggal terbaru (satu rangkuman per hari): jumlah sinyal yang diperiksa, contoh video komunitas, sinyal berita/pencarian, dan kegagalan sumber. Kantor pixel menampilkan tujuh tanggal terbaru melalui tombol **Lihat Riwayat Riset**. Semua ini merupakan *aktivitas riset*, bukan angka TikTok atau kinerja konten yang dipublikasi.

Jika riset menemukan 0 sumber yang memenuhi syarat, Nova tetap dapat menampilkan tiga **ide laboratorium** berlabel jelas sebagai contoh editorial, bukan tren nyata. Pilihan ide disimpan hanya di browser pengguna; belum diteruskan secara otomatis ke Agent 2.
