# AI Content Factory — Pixel Office 🎮

Kantor AI virtual bergaya pixel. **Agent 1 memiliki kode riset publik. Agent 2–6 memiliki pipeline draft offline berbasis template, bukan AI generatif atau layanan video yang aktif.**

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
- ✅ Agent 2–6: pipeline draft offline tersedia (storyboard, prompt, timeline, caption, status internal); belum rendering, posting, atau analytics platform

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


## Agent 2–6: Creative Pipeline (tanpa biaya)

Workflow \`python -m factory.pipeline\` membaca \`office/data/latest.json\` lalu menghasilkan
\`office/data/factory.json\`. Menu **STUDIO PRODUKSI** di Pixel Office
menampilkan paket draft: ide, hook, storyboard 6 adegan/30 detik, prompt gambar,
prompt video, caption draft, dan status 6 agent.

**Batasan aktual:** Semua teks dihasilkan dengan template Python, bukan AI generatif/LLM.
Belum ada rendering gambar, rendering video, login TikTok, upload konten, ataupun data views.
Agent 3 hanya menyiapkan prompt, Agent 4 hanya membuat rencana produksi,
Agent 5 hanya menyiapkan caption, Agent 6 hanya menampilkan hambatan analytics.
Output publik tidak boleh memuat API token atau informasi privat.
Kredit video AI dan publikasi selalu memerlukan keputusan dan akses akun pengguna.

\`\`\`bash
python -m unittest discover -s tests -v
python -m trendhunter.daily
python -m factory.pipeline
\`\`\`


## Verifikasi handoff offline (Agent 1 → Agent 2–6)

Pengujian `tests/test_offline_pipeline_integration.py` menjalankan `factory.pipeline.run()` di folder sementara, membaca contoh `office/data/latest.json`, dan memastikan `office/data/factory.json` berisi storyboard, prompt, timeline, serta caption. Tes juga memeriksa bahwa gambar/video belum dirender, posting tidak dilakukan, statistik platform tidak direkayasa, dan biaya pipeline tetap nol. Kasus tanpa ide harus menghasilkan paket kosong yang aman.

Jalankan `python -m unittest discover -s tests -v`. Workflow `.github/workflows/test.yml` menjalankan perintah yang sama pada push, pull request, atau manual dispatch. **Keberadaan tes atau commit tidak membuktikan GitHub Actions sudah lulus**; periksa hasil run pada tab Actions.

**Batas pekerjaan berikutnya:** verifikasi CI, validasi output dashboard, lalu evaluasi provider AI video hanya setelah persetujuan pengguna untuk akun, biaya, dan kredensial. Tidak ada publikasi otomatis tanpa persetujuan eksplisit.


## Credit Guard — simulasi terkunci (Rp0)

Kode: `factory/credit_guard.py`. Pengujian: `tests/test_credit_guard.py`.

- Anggaran harian **Rp0** dan maksimal **1 percobaan per video**.
- `authorize_video_attempt(...)` selalu mengembalikan `allowed=False`: percobaan berbayar ditolak dan percobaan gratis hanya disimulasikan.
- Laporan `office/data/factory.json` menyertakan `credit_guard` (mode, budget, batas percobaan, dan pengeluaran aktual Rp0).
- Tidak ada koneksi ke API video, pembayaran, penyimpanan kredensial, atau publikasi.
- **Jangan** mengaktifkan provider berbayar atau menaikkan budget tanpa persetujuan eksplisit pemilik.
- Ini adalah pengaman di pipeline Python, **bukan** batas penagihan di akun provider eksternal. Sebelum integrasi provider, semua jalur pemanggilan API harus melewati guard dan batas biaya provider juga harus diatur.

Jalankan tes: `python -m unittest discover -s tests -v`. Status keberhasilan CI harus diperiksa terpisah di GitHub Actions.


## Rencana video 30 detik dengan model open-source

`factory/opensource_video.py` menyusun rencana produksi 30 detik dalam enam klip @5 detik, yang nantinya dapat dikirim ke ComfyUI lokal atau server GPU. Pipeline `factory/pipeline.py` kini menghasilkan storyboard 6 adegan dan menyertakan `open_source_video_plan` untuk setiap draft.

Calon model: [Wan 2.2](https://github.com/Wan-Video/Wan2.2) dan [HunyuanVideo-1.5](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5). Pemilihan model final bergantung pada VRAM GPU, lisensi, dan kualitas uji. Tidak ada klaim kualitas setara Seedance tanpa benchmark. ComfyUI adalah pilihan integrasi, **belum ada worker GPU, endpoint, atau rendering yang terhubung**. Menjalankan model di GPU milik sendiri dapat menghindari biaya API per video, tetapi listrik dan perangkat tetap berbiaya; sewa GPU juga berbayar.

**Status:** rencana/kontrak offline saja. Belum ada video MP4 yang dihasilkan, tidak ada koneksi API berbayar, dan tidak ada publikasi. Credit Guard saat ini tetap simulasi Rp0 sampai pemilik menentukan kebijakan biaya baru. Periksa hasil CI sebelum menganggap perubahan ini siap produksi.
